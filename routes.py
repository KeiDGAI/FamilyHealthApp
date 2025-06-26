from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from requests_oauthlib import OAuth2Session
from datetime import datetime, timedelta
import os
import requests
import json
from openai import OpenAI
from app import app, db
from models import User, FamilyGroup

# OpenAI client initialization
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Fitbit Data Fetching Functions
def refresh_fitbit_token(user):
    """Fitbitアクセストークンをリフレッシュ"""
    try:
        token_url = 'https://api.fitbit.com/oauth2/token'
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': user.fitbit_refresh_token,
            'client_id': app.config['FITBIT_CLIENT_ID']
        }
        
        # Basic認証でClient SecretとClient IDを送信
        auth = (app.config['FITBIT_CLIENT_ID'], app.config['FITBIT_CLIENT_SECRET'])
        
        response = requests.post(token_url, data=data, auth=auth)
        
        if response.status_code == 200:
            token_data = response.json()
            
            # 新しいトークンでユーザー情報を更新
            user.fitbit_access_token = token_data['access_token']
            user.fitbit_refresh_token = token_data['refresh_token']
            user.fitbit_token_expires_at = datetime.utcnow() + timedelta(seconds=token_data['expires_in'])
            
            db.session.commit()
            app.logger.info(f'Successfully refreshed Fitbit token for user {user.username}')
            return True
        else:
            app.logger.error(f'Failed to refresh Fitbit token: {response.status_code} - {response.text}')
            return False
            
    except Exception as e:
        app.logger.error(f'Error refreshing Fitbit token: {e}')
        return False

def make_fitbit_api_request(user, endpoint):
    """Fitbit APIリクエストを実行（レート制限管理付き）"""
    from fitbit_rate_limit_manager import rate_limit_manager
    
    # レート制限チェック
    if not rate_limit_manager.can_make_request():
        app.logger.warning(f'Skipping Fitbit API request due to rate limit: {endpoint}')
        return None
    
    # トークンの有効期限をチェック
    if user.fitbit_token_expires_at and datetime.utcnow() >= user.fitbit_token_expires_at:
        app.logger.info('Fitbit token expired, refreshing...')
        if not refresh_fitbit_token(user):
            return None
    
    try:
        headers = {
            'Authorization': f'Bearer {user.fitbit_access_token}',
            'Accept': 'application/json'
        }
        
        response = requests.get(f'https://api.fitbit.com{endpoint}', headers=headers)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            # トークンが無効な場合、リフレッシュを試行
            app.logger.info('Received 401, attempting token refresh...')
            if refresh_fitbit_token(user):
                headers['Authorization'] = f'Bearer {user.fitbit_access_token}'
                response = requests.get(f'https://api.fitbit.com{endpoint}', headers=headers)
                if response.status_code == 200:
                    return response.json()
            
            app.logger.error(f'Fitbit API authentication failed: {response.status_code}')
            return None
        elif response.status_code == 429:
            # レート制限を記録し、今後のリクエストを一時停止
            rate_limit_manager.mark_rate_limited()
            app.logger.warning(f'Fitbit API rate limit exceeded. Requests suspended until reset.')
            return None
        else:
            app.logger.error(f'Fitbit API request failed: {response.status_code} - {response.text}')
            return None
            
    except Exception as e:
        app.logger.error(f'Error making Fitbit API request: {e}')
        return None

def parse_fitbit_data(raw_data):
    """FitbitのAPIレスポンスを解析して使いやすい形式に変換"""
    parsed_data = {
        'steps': 0,
        'calories_burned': 0,
        'resting_heart_rate': None,
        'max_heart_rate': None,
        'hrv': None,
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M')
    }
    
    try:
        # ステップ数とカロリー
        if 'activities' in raw_data:
            activities = raw_data['activities']
            if 'summary' in activities:
                summary = activities['summary']
                parsed_data['steps'] = summary.get('steps', 0)
                parsed_data['calories_burned'] = summary.get('caloriesOut', 0)
        
        # 心拍数データ
        if 'heart_rate' in raw_data:
            heart_data = raw_data['heart_rate']
            if 'activities-heart' in heart_data and heart_data['activities-heart']:
                heart_info = heart_data['activities-heart'][0]
                if 'value' in heart_info:
                    value = heart_info['value']
                    parsed_data['resting_heart_rate'] = value.get('restingHeartRate')
                    
                    # 心拍数ゾーンから最大心拍数を取得
                    if 'heartRateZones' in value:
                        zones = value['heartRateZones']
                        for zone in zones:
                            if zone.get('name') == 'Peak' and 'max' in zone:
                                parsed_data['max_heart_rate'] = zone['max']
                                break
        
        # HRVデータ
        if 'hrv' in raw_data:
            hrv_data = raw_data['hrv']
            if 'hrv' in hrv_data and hrv_data['hrv']:
                hrv_info = hrv_data['hrv'][0]
                if 'value' in hrv_info and 'dailyRmssd' in hrv_info['value']:
                    parsed_data['hrv'] = hrv_info['value']['dailyRmssd']
    
    except Exception as e:
        app.logger.error(f'Error parsing Fitbit data: {e}')
    
    return parsed_data

def get_fitbit_daily_data(user):
    """本日のFitbitデータを取得（レート制限対応）"""
    # レート制限を避けるため、一度に1つのエンドポイントのみ取得
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 最も重要なアクティビティデータのみ取得
    endpoint = f'/1/user/-/activities/date/{today}.json'
    
    result = make_fitbit_api_request(user, endpoint)
    if result:
        data = {'activities': result}
        return parse_fitbit_data(data)
    else:
        # APIが利用できない場合はデフォルト値を返す
        return {
            'steps': 0,
            'calories_burned': 0,
            'resting_heart_rate': None,
            'max_heart_rate': None,
            'hrv': None,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M')
        }

def get_fitbit_weekly_data(user):
    """過去7日間のFitbitデータを取得（効率化版）"""
    weekly_data = {
        'dates': [],
        'steps': [],
        'calories': [],
        'resting_hr': [],
        'max_hr': [],
        'hrv': []
    }
    
    # レート制限を避けるため、今日のデータのみ取得
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 今日のデータを取得
    daily_data = get_fitbit_daily_data(user)
    
    # 7日分のデータを生成（今日以外はデフォルト値）
    for i in range(7):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        weekly_data['dates'].insert(0, date)
        
        if date == today:
            # 今日のデータを使用
            weekly_data['steps'].insert(0, daily_data.get('steps', 0))
            weekly_data['calories'].insert(0, daily_data.get('calories_burned', 0))
            weekly_data['resting_hr'].insert(0, daily_data.get('resting_heart_rate', None))
            weekly_data['max_hr'].insert(0, daily_data.get('max_heart_rate', None))
            weekly_data['hrv'].insert(0, daily_data.get('hrv', None))
        else:
            # 過去のデータはデフォルト値（レート制限回避）
            weekly_data['steps'].insert(0, 0)
            weekly_data['calories'].insert(0, 0)
            weekly_data['resting_hr'].insert(0, None)
            weekly_data['max_hr'].insert(0, None)
            weekly_data['hrv'].insert(0, None)
    
    return weekly_data

def generate_health_comment(fitbit_data):
    """Fitbitデータに基づいてAIで健康コメントを生成"""
    if not fitbit_data:
        return "今日のデータが取得できませんでした。Fitbitデバイスを確認してください。"
    
    # Fitbitデータを要約文字列に変換
    summary_parts = []
    
    if fitbit_data.get('steps', 0) > 0:
        summary_parts.append(f"歩数: {fitbit_data['steps']:,}歩")
    
    if fitbit_data.get('calories_burned', 0) > 0:
        summary_parts.append(f"消費カロリー: {fitbit_data['calories_burned']:,}kcal")
    
    if fitbit_data.get('resting_heart_rate'):
        summary_parts.append(f"安静時心拍数: {fitbit_data['resting_heart_rate']}bpm")
    
    if fitbit_data.get('max_heart_rate'):
        summary_parts.append(f"最大心拍数: {fitbit_data['max_heart_rate']}bpm")
    
    if fitbit_data.get('hrv'):
        summary_parts.append(f"心拍変動 (HRV): {fitbit_data['hrv']}ms")
    
    if not summary_parts:
        return "今日のデータが不完全です。Fitbitデバイスを確認してください。"
    
    fitbit_summary = "、".join(summary_parts)
    
    try:
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": f"ユーザーの運動状況に対して健康寿命の観点でコメントしてください。前向きに活動を続けられるようにするアドバイスを心がけてください。以下がその日のデータです：{fitbit_summary}"
                }
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        app.logger.error(f'OpenAI API error: {e}')
        return "健康コメントの生成中にエラーが発生しました。しばらく経ってからもう一度お試しください。"

# Route handlers
def create_test_user():
    """テストユーザーを作成（存在しない場合のみ）"""
    try:
        test_user = User.query.filter_by(username='user').first()
        if not test_user:
            # テスト用ファミリーグループを作成
            test_group = FamilyGroup.query.filter_by(name='テスト家族').first()
            if not test_group:
                test_group = FamilyGroup(name='テスト家族')
                db.session.add(test_group)
                db.session.flush()
            
            # テストユーザーを作成
            test_user = User()
            test_user.username = 'user'
            test_user.email = 'test@example.com'
            test_user.set_password('testtest')
            test_user.group_id = test_group.id
            
            db.session.add(test_user)
            db.session.commit()
            app.logger.info(f'Test user created: user/testtest with group: {test_group.invite_code}')
    except Exception as e:
        app.logger.error(f'Error creating test user: {e}')
        db.session.rollback()

@app.route('/health')
def health_check():
    """ヘルスチェック用エンドポイント"""
    try:
        # データベース接続テスト
        User.query.first()
        return {"status": "ok", "database": "connected"}, 200
    except Exception as e:
        app.logger.error(f'Health check failed: {e}')
        return {"status": "error", "message": str(e)}, 500

@app.route('/')
def index():
    """ホームページ - ログインチェック"""
    try:
        # テストユーザーを作成
        create_test_user()
        
        if 'user_id' not in session:
            return redirect(url_for('login'))
    except Exception as e:
        app.logger.error(f'Index route error: {e}')
        return f"Application Error: {e}", 500
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))
    
    # 自分のFitbitデータの取得
    fitbit_data = None
    weekly_data = None
    health_comment = None
    if user.fitbit_access_token:
        fitbit_data = get_fitbit_daily_data(user)
        weekly_data = get_fitbit_weekly_data(user)
        if fitbit_data:
            health_comment = generate_health_comment(fitbit_data)
    
    # ファミリーグループメンバーのデータを取得
    family_members_data = []
    if user.group_id:
        family_group = user.family_group
        all_members = User.query.filter_by(group_id=user.group_id).all()
        
        for member in all_members:
            member_data = {
                'user': member,
                'fitbit_data': None,
                'health_comment': None,
                'is_current_user': member.id == user.id
            }
            
            if member.fitbit_access_token:
                member_fitbit_data = get_fitbit_daily_data(member)
                if member_fitbit_data:
                    member_data['fitbit_data'] = member_fitbit_data
                    # Generate health comment for family members too
                    member_data['health_comment'] = generate_health_comment(member_fitbit_data)
            
            family_members_data.append(member_data)
    
    return render_template('index.html', 
                         user=user, 
                         fitbit_data=fitbit_data, 
                         weekly_data=weekly_data, 
                         health_comment=health_comment,
                         family_members_data=family_members_data,
                         family_group=user.family_group if user.group_id else None)

@app.route('/group/leave', methods=['POST'])
def leave_group():
    """ファミリーグループから脱退"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user or not user.group_id:
        flash('グループに参加していません。', 'error')
        return redirect(url_for('index'))
    
    try:
        group_name = user.family_group.name if user.family_group else 'グループ'
        user.group_id = None
        db.session.commit()
        flash(f'ファミリーグループ「{group_name}」から脱退しました。', 'info')
    except Exception as e:
        db.session.rollback()
        flash('グループ脱退中にエラーが発生しました。', 'error')
        app.logger.error(f'Group leave error: {e}')
    
    return redirect(url_for('index'))

@app.route('/group/join', methods=['GET', 'POST'])
def join_group():
    """既存のファミリーグループに参加"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('login'))
    
    if user.group_id:
        flash('既にファミリーグループに参加しています。', 'info')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        invite_code = request.form.get('invite_code')
        
        if not invite_code:
            flash('招待コードを入力してください。', 'error')
            return render_template('join_group.html')
        
        family_group = FamilyGroup.query.filter_by(invite_code=invite_code.upper()).first()
        if not family_group:
            flash('無効な招待コードです。', 'error')
            return render_template('join_group.html')
        
        try:
            user.group_id = family_group.id
            db.session.commit()
            flash(f'ファミリーグループ「{family_group.name}」に参加しました！', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash('グループ参加中にエラーが発生しました。', 'error')
            app.logger.error(f'Group join error: {e}')
    
    return render_template('join_group.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """ログインページ"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('ユーザー名とパスワードを入力してください。', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f'{user.username}さん、おかえりなさい！', 'success')
            return redirect(url_for('index'))
        else:
            flash('ユーザー名またはパスワードが間違っています。', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """ユーザー登録ページ"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        group_action = request.form.get('group_action')
        group_name = request.form.get('group_name')
        invite_code = request.form.get('invite_code')
        
        # 基本バリデーション
        if not all([username, email, password]):
            flash('すべての必須項目を入力してください。', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('パスワードが一致しません。', 'error')
            return render_template('register.html')
        
        if password and len(password) < 6:
            flash('パスワードは6文字以上で入力してください。', 'error')
            return render_template('register.html')
        
        # ファミリーグループ関連のバリデーション
        if group_action == 'create' and not group_name:
            flash('ファミリーグループ名を入力してください。', 'error')
            return render_template('register.html')
        
        if group_action == 'join' and not invite_code:
            flash('招待コードを入力してください。', 'error')
            return render_template('register.html')
        
        # 既存ユーザーチェック
        if User.query.filter_by(username=username).first():
            flash('このユーザー名は既に使用されています。', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('このメールアドレスは既に使用されています。', 'error')
            return render_template('register.html')
        
        try:
            # ファミリーグループ処理
            family_group = None
            if group_action == 'create':
                # 新しいファミリーグループを作成
                family_group = FamilyGroup(name=group_name)
                db.session.add(family_group)
                db.session.flush()  # IDを取得するためにflush
                
            elif group_action == 'join':
                # 既存のファミリーグループに参加
                if invite_code:
                    family_group = FamilyGroup.query.filter_by(invite_code=invite_code.upper()).first()
                    if not family_group:
                        flash('無効な招待コードです。正しいコードを入力してください。', 'error')
                        return render_template('register.html')
                else:
                    flash('招待コードを入力してください。', 'error')
                    return render_template('register.html')
            
            # 新規ユーザー作成
            user = User()
            user.username = username
            user.email = email
            user.set_password(password)
            
            if family_group:
                user.group_id = family_group.id
                if group_action == 'create':
                    family_group.created_by = user.id
            
            db.session.add(user)
            db.session.commit()
            
            if group_action == 'create' and family_group:
                flash(f'登録が完了しました。ファミリーグループ「{group_name}」を作成しました。招待コード: {family_group.invite_code}', 'success')
            elif group_action == 'join' and family_group:
                flash(f'登録が完了しました。ファミリーグループ「{family_group.name}」に参加しました。', 'success')
            else:
                flash('登録が完了しました。ログインしてください。', 'success')
                
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            flash('登録中にエラーが発生しました。もう一度お試しください。', 'error')
            app.logger.error(f'Registration error: {e}')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """ログアウト"""
    username = session.get('username', 'ユーザー')
    session.clear()
    flash(f'{username}さん、お疲れ様でした。', 'info')
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    """プロフィールページ"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))
    
    return render_template('profile.html', user=user)

# Fitbit OAuth Routes
@app.route('/connect_fitbit')
def connect_fitbit():
    """Fitbit OAuth認証開始"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        # Fitbit OAuth 2.0の設定
        authorization_base_url = 'https://www.fitbit.com/oauth2/authorize'
        
        app.logger.info(f'Using Client ID: {app.config["FITBIT_CLIENT_ID"][:8]}...')
        app.logger.info(f'Using Redirect URI: {app.config["FITBIT_REDIRECT_URI"]}')
        
        fitbit = OAuth2Session(
            app.config['FITBIT_CLIENT_ID'],
            scope=['activity', 'heartrate', 'location', 'nutrition', 'profile', 'settings', 'sleep', 'social', 'weight'],
            redirect_uri=app.config['FITBIT_REDIRECT_URI']
        )
        
        authorization_url, state = fitbit.authorization_url(authorization_base_url)
        
        # stateをセッションに保存（セキュリティのため）
        session['fitbit_oauth_state'] = state
        
        app.logger.info(f'Redirecting to: {authorization_url}')
        return redirect(authorization_url)
        
    except Exception as e:
        app.logger.error(f'Error starting OAuth flow: {e}')
        flash('Fitbit認証の開始中にエラーが発生しました。設定を確認してください。', 'error')
        return redirect(url_for('index'))

@app.route('/fitbit_callback')
def fitbit_callback():
    """Fitbit OAuth認証コールバック"""
    if 'user_id' not in session:
        flash('ログインが必要です。', 'error')
        return redirect(url_for('login'))
    
    # エラーチェック
    if 'error' in request.args:
        flash('Fitbit認証がキャンセルされました。', 'warning')
        return redirect(url_for('index'))
    
    # 認証コードとstateの取得
    code = request.args.get('code')
    state = request.args.get('state')
    
    if not code or not state:
        flash('認証に失敗しました。', 'error')
        return redirect(url_for('index'))
    
    # stateの検証
    if state != session.get('fitbit_oauth_state'):
        flash('認証エラー：無効なリクエストです。', 'error')
        return redirect(url_for('index'))
    
    try:
        # トークン取得 - Fitbit APIの認証方式に合わせて修正
        import base64
        
        token_url = 'https://api.fitbit.com/oauth2/token'
        
        # Basic認証ヘッダーを正しく作成
        auth_string = f"{app.config['FITBIT_CLIENT_ID']}:{app.config['FITBIT_CLIENT_SECRET']}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        fitbit = OAuth2Session(
            app.config['FITBIT_CLIENT_ID'],
            redirect_uri=app.config['FITBIT_REDIRECT_URI']
        )
        
        # カスタムヘッダーでトークンを取得
        token = fitbit.fetch_token(
            token_url,
            code=code,
            client_secret=app.config['FITBIT_CLIENT_SECRET'],
            include_client_id=True,
            headers={'Authorization': f'Basic {auth_b64}'}
        )
        
        # ユーザー情報取得
        user_info_response = fitbit.get('https://api.fitbit.com/1/user/-/profile.json')
        user_info = user_info_response.json()
        
        # データベースにトークンを保存
        user = User.query.get(session['user_id'])
        if user:
            user.fitbit_user_id = user_info['user']['encodedId']
            user.fitbit_access_token = token['access_token']
            user.fitbit_refresh_token = token['refresh_token']
            user.fitbit_token_expires_at = datetime.utcnow() + timedelta(seconds=token['expires_in'])
            
            db.session.commit()
            
            flash('Fitbitアカウントが正常に連携されました！', 'success')
        else:
            flash('ユーザー情報の取得に失敗しました。', 'error')
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        app.logger.error(f'Fitbit OAuth error: {e}')
        app.logger.error(f'Full traceback: {error_details}')
        
        # より詳細なエラーメッセージを提供
        if 'invalid_client' in str(e):
            flash('Fitbit認証エラー: クライアントIDまたはシークレットが無効です。', 'error')
        elif 'invalid_grant' in str(e):
            flash('Fitbit認証エラー: 認証コードが無効または期限切れです。', 'error')
        elif 'redirect_uri_mismatch' in str(e):
            flash('Fitbit認証エラー: リダイレクトURIが一致しません。', 'error')
        else:
            flash(f'Fitbit認証中にエラーが発生しました: {str(e)[:100]}', 'error')
    
    finally:
        # stateをセッションから削除
        session.pop('fitbit_oauth_state', None)
    
    return redirect(url_for('index'))

@app.route('/disconnect_fitbit')
def disconnect_fitbit():
    """Fitbit連携解除"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if user:
        user.fitbit_user_id = None
        user.fitbit_access_token = None
        user.fitbit_refresh_token = None
        user.fitbit_token_expires_at = None
        
        db.session.commit()
        flash('Fitbit連携を解除しました。', 'info')
    
    return redirect(url_for('index'))

@app.route('/chart/<metric>')
def chart_view(metric):
    """個別チャート表示ページ"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user or not user.fitbit_access_token:
        flash('Fitbitデータが利用できません。', 'error')
        return redirect(url_for('index'))
    
    # 有効なメトリクスかチェック
    valid_metrics = ['steps', 'calories', 'resting_hr', 'max_hr', 'hrv']
    if metric not in valid_metrics:
        flash('無効なメトリクスです。', 'error')
        return redirect(url_for('index'))
    
    # 週間データを取得
    weekly_data = get_fitbit_weekly_data(user)
    
    # メトリクス情報を設定
    metric_info = {
        'steps': {'title': '歩数', 'unit': '歩', 'color': '#0d6efd', 'icon': 'fa-walking'},
        'calories': {'title': '消費カロリー', 'unit': 'kcal', 'color': '#dc3545', 'icon': 'fa-fire'},
        'resting_hr': {'title': '安静時心拍数', 'unit': 'bpm', 'color': '#198754', 'icon': 'fa-heartbeat'},
        'max_hr': {'title': '最大心拍数', 'unit': 'bpm', 'color': '#ffc107', 'icon': 'fa-tachometer-alt'},
        'hrv': {'title': '心拍変動 (HRV)', 'unit': 'ms', 'color': '#0dcaf0', 'icon': 'fa-chart-line'}
    }
    
    return render_template('chart.html', 
                         metric=metric, 
                         metric_info=metric_info[metric],
                         weekly_data=weekly_data,
                         user=user)
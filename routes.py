from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from requests_oauthlib import OAuth2Session
from datetime import datetime, timedelta
import os
from app import app, db
from models import User

@app.route('/')
def index():
    """ホームページ - ログインチェック"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))
    
    return render_template('index.html', user=user)

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
        
        # バリデーション
        if not all([username, email, password]):
            flash('すべての必須項目を入力してください。', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('パスワードが一致しません。', 'error')
            return render_template('register.html')
        
        if password and len(password) < 6:
            flash('パスワードは6文字以上で入力してください。', 'error')
            return render_template('register.html')
        
        # 既存ユーザーチェック
        if User.query.filter_by(username=username).first():
            flash('このユーザー名は既に使用されています。', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('このメールアドレスは既に使用されています。', 'error')
            return render_template('register.html')
        
        # 新規ユーザー作成
        user = User()
        user.username = username
        user.email = email
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
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
    
    # Fitbit OAuth 2.0の設定
    authorization_base_url = 'https://www.fitbit.com/oauth2/authorize'
    
    fitbit = OAuth2Session(
        app.config['FITBIT_CLIENT_ID'],
        scope=['activity', 'heartrate', 'location', 'nutrition', 'profile', 'settings', 'sleep', 'social', 'weight'],
        redirect_uri=app.config['FITBIT_REDIRECT_URI']
    )
    
    authorization_url, state = fitbit.authorization_url(authorization_base_url)
    
    # stateをセッションに保存（セキュリティのため）
    session['fitbit_oauth_state'] = state
    
    return redirect(authorization_url)

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
        # トークン取得
        token_url = 'https://api.fitbit.com/oauth2/token'
        
        fitbit = OAuth2Session(
            app.config['FITBIT_CLIENT_ID'],
            redirect_uri=app.config['FITBIT_REDIRECT_URI']
        )
        
        token = fitbit.fetch_token(
            token_url,
            code=code,
            client_secret=app.config['FITBIT_CLIENT_SECRET']
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
        app.logger.error(f'Fitbit OAuth error: {e}')
        flash('Fitbit認証中にエラーが発生しました。', 'error')
    
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

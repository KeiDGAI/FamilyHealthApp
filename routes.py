from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
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

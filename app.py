import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# 環境判定 - より確実な本番環境検出
IS_PRODUCTION = bool(os.environ.get('REPLIT_DEPLOYMENT')) or 'replit.app' in os.environ.get('REPLIT_DOMAINS', '')

# ログ設定
if IS_PRODUCTION:
    logging.basicConfig(level=logging.INFO)
else:
    logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# アプリケーション作成
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Fitbit OAuth 設定
app.config['FITBIT_CLIENT_ID'] = os.environ.get('FITBIT_CLIENT_ID', 'your-fitbit-client-id')
app.config['FITBIT_CLIENT_SECRET'] = os.environ.get('FITBIT_CLIENT_SECRET', 'your-fitbit-client-secret')

# Fitbit Redirect URIを設定 - 本番環境のURLを使用
app.config['FITBIT_REDIRECT_URI'] = 'https://family-health-tracker-wkeisuke.replit.app/fitbit_callback'

# データベース設定
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///:memory:")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# デモモード設定（本番環境では False に変更）
app.config['USE_DEMO_DATA'] = os.environ.get('USE_DEMO_DATA', 'True').lower() == 'true'

# データベース初期化
db.init_app(app)

# データベースとルートの安全な初期化
def initialize_app():
    """アプリケーションを安全に初期化"""
    try:
        with app.app_context():
            # モデルをインポート
            import models
            
            # データベース接続テスト
            db.engine.connect()
            app.logger.info('Database connection successful')
            
            # テーブル作成
            db.create_all()
            app.logger.info('Database tables created successfully')
            
        # ルートをインポート
        import routes
        app.logger.info('Routes imported successfully')
        
        return True
    except Exception as e:
        app.logger.error(f'Application initialization failed: {e}')
        import traceback
        app.logger.error(traceback.format_exc())
        return False

# アプリケーション初期化
if not initialize_app():
    # 初期化に失敗した場合のフォールバック
    app.logger.error('Application failed to initialize properly')

# エラーハンドラー
@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f'Internal Server Error: {error}')
    try:
        db.session.rollback()
    except:
        pass
    
    if IS_PRODUCTION:
        return """
        <html>
            <head><title>システムエラー</title></head>
            <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                <h1>システムエラー</h1>
                <p>申し訳ございません。一時的なエラーが発生しました。</p>
                <p>しばらく経ってからもう一度お試しください。</p>
                <a href="/" style="color: #007bff;">ホームに戻る</a>
            </body>
        </html>
        """, 500
    else:
        return f"Internal Server Error: {error}", 500

@app.errorhandler(404)
def not_found_error(error):
    return """
    <html>
        <head><title>ページが見つかりません</title></head>
        <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
            <h1>404 - ページが見つかりません</h1>
            <p>お探しのページは存在しません。</p>
            <a href="/" style="color: #007bff;">ホームに戻る</a>
        </body>
    </html>
    """, 404

# ヘルスチェック用の基本ルート
@app.route('/health')
def basic_health():
    """基本的なヘルスチェック"""
    return {"status": "ok", "app": "running"}, 200

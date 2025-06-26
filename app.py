import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# ログ設定
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# アプリケーション作成
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key-for-development")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Fitbit OAuth 設定
app.config['FITBIT_CLIENT_ID'] = os.environ.get('FITBIT_CLIENT_ID', 'your-fitbit-client-id')
app.config['FITBIT_CLIENT_SECRET'] = os.environ.get('FITBIT_CLIENT_SECRET', 'your-fitbit-client-secret')
app.config['FITBIT_REDIRECT_URI'] = os.environ.get('FITBIT_REDIRECT_URI', 'http://localhost:5000/fitbit_callback')

# データベース設定（SQLite）
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# データベース初期化
db.init_app(app)

with app.app_context():
    # モデルをインポート
    import models
    # テーブル作成
    db.create_all()
    
# ルートをインポート
import routes

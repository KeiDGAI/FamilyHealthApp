from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets
import string

class FamilyGroup(db.Model):
    """家族グループモデル - 家族単位でデータを管理"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    invite_code = db.Column(db.String(8), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, nullable=True)  # Will be set after user creation
    
    # Relationship to users
    members = db.relationship('User', backref='family_group', lazy=True, foreign_keys='User.group_id')
    
    def __init__(self, **kwargs):
        super(FamilyGroup, self).__init__(**kwargs)
        if not self.invite_code:
            self.invite_code = self.generate_invite_code()
    
    @staticmethod
    def generate_invite_code():
        """招待コードを生成（8文字の英数字）"""
        while True:
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            if not FamilyGroup.query.filter_by(invite_code=code).first():
                return code
    
    def __repr__(self):
        return f'<FamilyGroup {self.name}>'

class User(db.Model):
    """ユーザーモデル - 家族メンバーの情報を管理"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Family group association
    group_id = db.Column(db.Integer, db.ForeignKey('family_group.id'), nullable=True)
    
    # Fitbit OAuth tokens
    fitbit_user_id = db.Column(db.String(50))
    fitbit_access_token = db.Column(db.Text)
    fitbit_refresh_token = db.Column(db.Text)
    fitbit_token_expires_at = db.Column(db.DateTime)
    
    def set_password(self, password):
        """パスワードをハッシュ化して保存"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """パスワードを検証"""
        return check_password_hash(self.password_hash, password)
    
    def get_group_members(self):
        """同じグループの他のメンバーを取得"""
        if not self.group_id:
            return []
        return User.query.filter(
            User.group_id == self.group_id,
            User.id != self.id
        ).all()
    
    def can_view_user_data(self, other_user_id):
        """他のユーザーのデータを閲覧可能かチェック"""
        if self.id == other_user_id:
            return True
        if not self.group_id:
            return False
        other_user = User.query.get(other_user_id)
        return other_user and other_user.group_id == self.group_id
    
    def __repr__(self):
        return f'<User {self.username}>'

class FitbitData(db.Model):
    """Fitbitデータキャッシュモデル - APIレート制限対策"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    
    # 健康データ
    steps = db.Column(db.Integer, default=0)
    calories_burned = db.Column(db.Integer, default=0)
    resting_heart_rate = db.Column(db.Integer, nullable=True)
    max_heart_rate = db.Column(db.Integer, nullable=True)
    hrv = db.Column(db.Float, nullable=True)
    
    # キャッシュ管理
    fetched_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # ユーザーとの関係
    user = db.relationship('User', backref=db.backref('fitbit_data', lazy=True))
    
    # ユニーク制約（ユーザーと日付の組み合わせ）
    __table_args__ = (db.UniqueConstraint('user_id', 'date', name='_user_date_uc'),)
    
    def is_cache_expired(self, cache_duration_minutes=30):
        """キャッシュが期限切れかチェック"""
        if not self.fetched_at:
            return True
        
        from datetime import timedelta
        expiry_time = self.fetched_at + timedelta(minutes=cache_duration_minutes)
        return datetime.utcnow() > expiry_time
    
    def to_dict(self):
        """辞書形式でデータを返す"""
        return {
            'steps': self.steps or 0,
            'calories_burned': self.calories_burned or 0,
            'resting_heart_rate': self.resting_heart_rate,
            'max_heart_rate': self.max_heart_rate,
            'hrv': self.hrv,
            'last_updated': self.fetched_at.strftime('%Y-%m-%d %H:%M') if self.fetched_at else 'N/A'
        }
    
    def __repr__(self):
        return f'<FitbitData {self.user.username} {self.date}>'

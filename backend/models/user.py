from backend import db
from .base import BaseModel
from werkzeug.security import generate_password_hash, check_password_hash

class User(BaseModel):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    is_active = db.Column(db.Boolean, default=True)
    
    role = db.relationship('Role', back_populates='users')
    
    @staticmethod
    def create_user(username, password, email, role_id=None):
        """创建新用户的工厂方法"""
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        user = User(
            username=username,
            password=hashed_password,
            email=email,
            role_id=role_id
        )
        return user

    def __init__(self, username, password, email, role_id=None):
        self.username = username
        self.password = password  # 已经哈希过的密码
        self.email = email
        self.role_id = role_id

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_id(self):
        return str(self.id)

    def has_permission(self, permission):
        """检查用户是否有特定权限"""
        return (self.role and 
                self.role.permissions and 
                permission in self.role.permissions)

    @staticmethod
    def create_password_hash(password):
        """创建密码哈希"""
        return generate_password_hash(password, method='pbkdf2:sha256')
        
    def to_dict(self):
        """转换为字典，用于JSON序列化"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role.to_dict() if self.role else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
 
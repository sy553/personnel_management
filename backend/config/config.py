from datetime import timedelta
import os

class Config:
    # JWT配置
    JWT_SECRET_KEY = "your-secret-key-keep-it-secret"  # 生产环境应使用更安全的密钥
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@localhost/personnel_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 文件上传配置
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'xls', 'xlsx'}
    
    # 安全配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')
    
    # CORS配置
    CORS_HEADERS = 'Content-Type'
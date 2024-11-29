from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os
from .config.config import Config  # 导入配置类

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 配置日志
    import logging
    logging.basicConfig(level=logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)
    
    # 加载配置
    app.config.from_object(Config)
    
    # CORS 配置
    CORS(app, resources={
        r"/*": {
            "origins": ["http://localhost:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    # 确保上传目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    # 确保员工附件目录存在
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'employee_attachments'), exist_ok=True)
    # 确保合同文件目录存在
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'contracts'), exist_ok=True)
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # 确保导入所有模型
    with app.app_context():
        from .models.user import User
        from .models.permission import Role
        from .models.employee import Employee, EmployeeEducation
        
        # 注册蓝图
        from .routes.auth import auth_bp
        from .routes.permission import permission_bp
        from .routes.department import department_bp
        from .routes.employee import employee_bp
        from .routes.attendance import attendance_bp
        from .routes.salary import salary_bp
        from .routes.report import report_bp
        from .routes.budget import budget_bp
        from .routes.alert import alert_bp
        from .routes.export import export_bp
        
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(permission_bp, url_prefix='/api/permission')
        app.register_blueprint(department_bp, url_prefix='/api/department')
        app.register_blueprint(employee_bp, url_prefix='/api/employee')
        app.register_blueprint(attendance_bp)
        app.register_blueprint(salary_bp, url_prefix='/api/salary')
        app.register_blueprint(report_bp, url_prefix='/api/report')
        app.register_blueprint(budget_bp, url_prefix='/api/budget')
        app.register_blueprint(alert_bp, url_prefix='/api/alert')
        app.register_blueprint(export_bp, url_prefix='/api/export')
        
        # 创建所有表
        db.create_all()
        
        # 创建教育经历表
        try:
            with open('migrations/create_education_table.sql', 'r', encoding='utf-8') as f:
                sql = f.read()
                from sqlalchemy import text
                db.session.execute(text(sql))
                db.session.commit()
        except Exception as e:
            app.logger.error(f"创建教育经历表失败: {str(e)}")
            db.session.rollback()
        
        # 创建默认角色和用户
        try:
            # 创建管理员角色
            admin_role = Role.query.filter_by(name='admin').first()
            if not admin_role:
                admin_role = Role(
                    name='admin',
                    description='系统管理员',
                    permissions=['admin', 'manage_users', 'manage_roles']
                )
                db.session.add(admin_role)
                db.session.commit()
            
            # 创建管理员用户
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                admin_user = User.create_user(
                    username='admin',
                    password='admin123',
                    email='admin@example.com',
                    role_id=admin_role.id
                )
                db.session.add(admin_user)
                db.session.commit()
        except Exception as e:
            app.logger.error(f"创建默认数据失败: {str(e)}")
            db.session.rollback()
    
    return app

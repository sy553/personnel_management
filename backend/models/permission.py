from .. import db
from .base import BaseModel

class Role(BaseModel):
    """角色表"""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    permissions = db.Column(db.JSON)  # 存储权限列表
    
    users = db.relationship('User', back_populates='role')

    def to_dict(self):
        """转换为字典，用于JSON序列化"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'permissions': self.permissions
        }

class Permission:
    """权限常量定义"""
    # 员工权限
    ATTENDANCE = 'attendance'  # 考勤打卡
    VIEW_SELF_SALARY = 'view_self_salary'  # 查看自己的工资
    APPLY_LEAVE = 'apply_leave'  # 申请请假
    
    # 管理员权限
    MANAGE_USERS = 'manage_users'  # 用户管理
    MANAGE_EMPLOYEES = 'manage_employees'  # 员工管理
    MANAGE_ATTENDANCE = 'manage_attendance'  # 考勤管理
    MANAGE_SALARY = 'manage_salary'  # 薪资管理
    MANAGE_ROLES = 'manage_roles'  # 角色管理
    
    # 系统管理员权限
    ADMIN = 'admin'  # 系统管理

def create_default_roles():
    """创建默认角色"""
    # 管理员角色
    admin_role = Role.query.filter_by(name='admin').first()
    if not admin_role:
        admin_role = Role(
            name='admin',
            description='系统管理员',
            permissions=['admin', 'manage_users', 'manage_roles', 'manage_employees', 
                        'manage_attendance', 'manage_salary']
        )
        db.session.add(admin_role)
        
    # 普通员工角色
    employee_role = Role.query.filter_by(name='employee').first()
    if not employee_role:
        employee_role = Role(
            name='employee',
            description='普通员工',
            permissions=['attendance', 'view_self_salary', 'apply_leave']
        )
        db.session.add(employee_role)
        
    db.session.commit()
    return admin_role, employee_role
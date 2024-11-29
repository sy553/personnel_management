from .. import db
from .base import BaseModel
from datetime import datetime

class Salary(BaseModel):
    """薪资表"""
    __tablename__ = 'salaries'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    base_salary = db.Column(db.Numeric(10, 2), nullable=False)
    overtime_pay = db.Column(db.Numeric(10, 2), default=0)
    bonus = db.Column(db.Numeric(10, 2), default=0)
    deductions = db.Column(db.Numeric(10, 2), default=0)
    social_security = db.Column(db.Numeric(10, 2), default=0)
    tax = db.Column(db.Numeric(10, 2), default=0)
    net_salary = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default='pending')
    payment_date = db.Column(db.DateTime)
    notes = db.Column(db.String(200))
    
    # 关系
    employee = db.relationship('Employee', backref='salaries')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.name,
            'employee_no': self.employee.employee_no,
            'year': self.year,
            'month': self.month,
            'base_salary': float(self.base_salary),
            'overtime_pay': float(self.overtime_pay),
            'bonus': float(self.bonus),
            'deductions': float(self.deductions),
            'social_security': float(self.social_security),
            'tax': float(self.tax),
            'net_salary': float(self.net_salary),
            'status': self.status,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class SalaryConfig(BaseModel):
    """薪资配置表"""
    __tablename__ = 'salary_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    base_salary = db.Column(db.Numeric(10, 2), nullable=False)
    overtime_rate = db.Column(db.Numeric(5, 2), default=1.5)
    social_security_rate = db.Column(db.Numeric(5, 2), default=0.1)
    effective_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Boolean, default=True)
    
    # 关系
    employee = db.relationship('Employee', backref='salary_configs')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.name,
            'employee_no': self.employee.employee_no,
            'base_salary': float(self.base_salary),
            'overtime_rate': float(self.overtime_rate),
            'social_security_rate': float(self.social_security_rate),
            'effective_date': self.effective_date.isoformat(),
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
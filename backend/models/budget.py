from .. import db
from .base import BaseModel
from datetime import datetime

class DepartmentBudget(BaseModel):
    """部门预算表"""
    __tablename__ = 'department_budgets'
    
    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    salary_budget = db.Column(db.Numeric(12, 2), nullable=False)  # 工资预算
    overtime_budget = db.Column(db.Numeric(12, 2), default=0)  # 加班费预算
    bonus_budget = db.Column(db.Numeric(12, 2), default=0)  # 奖金预算
    other_budget = db.Column(db.Numeric(12, 2), default=0)  # 其他预算
    total_budget = db.Column(db.Numeric(12, 2), nullable=False)  # 总预算
    notes = db.Column(db.String(200))  # 备注
    status = db.Column(db.String(20), default='draft')  # draft草稿, approved已审批
    
    # 关系
    department = db.relationship('Department', backref='budgets')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'department_id': self.department_id,
            'department_name': self.department.name,
            'year': self.year,
            'month': self.month,
            'salary_budget': float(self.salary_budget),
            'overtime_budget': float(self.overtime_budget),
            'bonus_budget': float(self.bonus_budget),
            'other_budget': float(self.other_budget),
            'total_budget': float(self.total_budget),
            'notes': self.notes,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 
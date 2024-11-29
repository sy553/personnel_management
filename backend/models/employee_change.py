from .. import db
from .base import BaseModel
from datetime import datetime

class EmployeeChange(BaseModel):
    """员工异动记录表"""
    __tablename__ = 'employee_changes'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    change_type = db.Column(db.String(20), nullable=False)  # entry入职, leave离职, transfer调岗, promotion晋升
    old_department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    new_department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    old_position = db.Column(db.String(50))
    new_position = db.Column(db.String(50))
    effective_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.String(200))
    
    # 关系
    employee = db.relationship('Employee', backref='changes')
    old_department = db.relationship('Department', foreign_keys=[old_department_id])
    new_department = db.relationship('Department', foreign_keys=[new_department_id])
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.name,
            'employee_no': self.employee.employee_no,
            'change_type': self.change_type,
            'old_department': self.old_department.name if self.old_department else None,
            'new_department': self.new_department.name if self.new_department else None,
            'old_position': self.old_position,
            'new_position': self.new_position,
            'effective_date': self.effective_date.isoformat(),
            'reason': self.reason,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 
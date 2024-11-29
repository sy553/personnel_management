from backend import db
from .base import BaseModel
from datetime import datetime, time

class Attendance(BaseModel):
    """考勤记录表"""
    __tablename__ = 'attendances'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)  # 考勤日期
    clock_in = db.Column(db.Time)  # 上班打卡时间
    clock_out = db.Column(db.Time)  # 下班打卡时间
    status = db.Column(db.String(20))  # normal正常, late迟到, early早退, absent缺勤
    notes = db.Column(db.String(200))  # 备注
    
    # 关系
    employee = db.relationship('Employee', backref='attendances')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.name,
            'employee_no': self.employee.employee_no,
            'date': self.date.isoformat(),
            'clock_in': self.clock_in.strftime('%H:%M:%S') if self.clock_in else None,
            'clock_out': self.clock_out.strftime('%H:%M:%S') if self.clock_out else None,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Leave(BaseModel):
    """请假记录表"""
    __tablename__ = 'leaves'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 请假类型：sick病假, annual年假, personal事假
    start_date = db.Column(db.Date, nullable=False)  # 开始日期
    end_date = db.Column(db.Date, nullable=False)  # 结束日期
    reason = db.Column(db.String(200))  # 请假原因
    status = db.Column(db.String(20), default='pending')  # pending待审批, approved已批准, rejected已拒绝
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 审批人
    
    # 关系
    employee = db.relationship('Employee', backref='leaves')
    approver = db.relationship('User', backref='approved_leaves')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.name,
            'employee_no': self.employee.employee_no,
            'type': self.type,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'reason': self.reason,
            'status': self.status,
            'approver_id': self.approver_id,
            'approver_name': self.approver.username if self.approver else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
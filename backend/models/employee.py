from backend import db
from .base import BaseModel
from datetime import datetime
from flask import current_app

class Employee(BaseModel):
    """员工表"""
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_no = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10))
    birth_date = db.Column(db.Date)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    id_card = db.Column(db.String(18), unique=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    position = db.Column(db.String(50))
    entry_date = db.Column(db.Date)
    base_salary = db.Column(db.Numeric(10, 2))
    bank_account = db.Column(db.String(50))
    bank_name = db.Column(db.String(100))
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')
    leave_date = db.Column(db.Date)
    leave_reason = db.Column(db.Text)
    
    # 合同相关字段
    contract_number = db.Column(db.String(50))
    contract_type = db.Column(db.String(20))
    contract_duration = db.Column(db.Integer)
    contract_start_date = db.Column(db.Date)
    contract_end_date = db.Column(db.Date)
    contract_sign_date = db.Column(db.Date)
    contract_status = db.Column(db.String(20))
    
    # 关系
    department = db.relationship('Department', backref='employees')
    education = db.relationship('EmployeeEducation', backref='employee',
                              cascade='all, delete-orphan',
                              primaryjoin='Employee.employee_no==EmployeeEducation.employee_no',
                              lazy='dynamic')
    training = db.relationship('EmployeeTraining', backref='employee',
                             cascade='all, delete-orphan',
                             primaryjoin='Employee.employee_no==EmployeeTraining.employee_no',
                             lazy='dynamic')
    
    def to_dict(self):
        """转换为字典"""
        try:
            data = {
                'id': self.id,
                'employee_no': self.employee_no,
                'name': self.name,
                'gender': self.gender,
                'birth_date': self.birth_date.strftime('%Y-%m-%d') if self.birth_date else None,
                'phone': self.phone,
                'email': self.email,
                'id_card': self.id_card,
                'department': self.department.to_dict() if self.department else None,
                'position': self.position,
                'entry_date': self.entry_date.strftime('%Y-%m-%d') if self.entry_date else None,
                'base_salary': str(self.base_salary) if self.base_salary else None,
                'bank_account': self.bank_account,
                'bank_name': self.bank_name,
                'notes': self.notes,
                'status': self.status,
                'leave_date': self.leave_date.strftime('%Y-%m-%d') if self.leave_date else None,
                'leave_reason': self.leave_reason,
            }
            
            # 获取教育经历数据
            try:
                education_list = [edu.to_dict() for edu in self.education.all()]
                current_app.logger.debug(f"员工 {self.employee_no} 的教育经历: {education_list}")
                data['education'] = education_list
            except Exception as e:
                current_app.logger.error(f"获取教育经历失败: {str(e)}")
                data['education'] = []
            
            # 获取培训记录数据
            try:
                training_list = [training.to_dict() for training in self.training.all()]
                current_app.logger.debug(f"员工 {self.employee_no} 的培训记录: {training_list}")
                data['training'] = training_list
            except Exception as e:
                current_app.logger.error(f"获取培训记录失败: {str(e)}")
                data['training'] = []
            
            # 如果有合同信息，添加合同对象
            if any([
                self.contract_number,
                self.contract_type,
                self.contract_duration,
                self.contract_start_date,
                self.contract_end_date,
                self.contract_sign_date,
                self.contract_status
            ]):
                data['contract'] = {
                    'id': self.id,  # 使用员工ID作为合同ID
                    'number': self.contract_number,
                    'type': self.contract_type,
                    'duration': self.contract_duration,
                    'start_date': self.contract_start_date.strftime('%Y-%m-%d') if self.contract_start_date else None,
                    'end_date': self.contract_end_date.strftime('%Y-%m-%d') if self.contract_end_date else None,
                    'sign_date': self.contract_sign_date.strftime('%Y-%m-%d') if self.contract_sign_date else None,
                    'status': self.contract_status
                }
            else:
                data['contract'] = None
                
            # 添加其他数组字段的默认值
            data.update({
                'work_experience': [],
                'position_changes': [],
                'reward_punishments': [],
                'attachments': []
            })
                
            return data
        except Exception as e:
            current_app.logger.error(f"转换员工数据失败: employee_no={self.employee_no}, error={str(e)}")
            # 返回最小数据集
            return {
                'id': self.id,
                'employee_no': self.employee_no,
                'name': self.name,
                'status': self.status
            }

class EmployeeEducation(BaseModel):
    """员工教育经历表"""
    __tablename__ = 'employee_education'

    id = db.Column(db.Integer, primary_key=True)
    employee_no = db.Column(db.String(50), db.ForeignKey('employees.employee_no', ondelete='CASCADE'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    school = db.Column(db.String(100), nullable=False)
    major = db.Column(db.String(100), nullable=False)
    degree = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        try:
            data = {
                'id': self.id,
                'employee_no': self.employee_no,
                'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
                'end_date': self.end_date.strftime('%Y-%m-%d') if self.end_date else None,
                'school': self.school,
                'major': self.major,
                'degree': self.degree,
                'description': self.description
            }
            current_app.logger.debug(f"教育经历数据: {data}")
            return data
        except Exception as e:
            current_app.logger.error(f"转换教育经历数据失败: id={self.id}, error={str(e)}")
            return {
                'id': self.id,
                'employee_no': self.employee_no,
                'school': self.school,
                'degree': self.degree
            }
    
class EmployeeTraining(BaseModel):
    """员工培训记录表"""
    __tablename__ = 'employee_training'

    id = db.Column(db.Integer, primary_key=True)
    employee_no = db.Column(db.String(50), db.ForeignKey('employees.employee_no', ondelete='CASCADE'), nullable=False)
    course_name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    trainer = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Integer)
    status = db.Column(db.String(20), default='not_started')
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        try:
            data = {
                'id': self.id,
                'employee_no': self.employee_no,
                'course_name': self.course_name,
                'type': self.type,
                'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
                'end_date': self.end_date.strftime('%Y-%m-%d') if self.end_date else None,
                'trainer': self.trainer,
                'score': self.score,
                'status': self.status,
                'description': self.description
            }
            current_app.logger.debug(f"培训记录数据: {data}")
            return data
        except Exception as e:
            current_app.logger.error(f"转换培训记录数据失败: id={self.id}, error={str(e)}")
            return {
                'id': self.id,
                'employee_no': self.employee_no,
                'course_name': self.course_name,
                'status': self.status
            }
    
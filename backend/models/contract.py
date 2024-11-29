from .. import db
from datetime import datetime
from sqlalchemy.orm import validates

class EmployeeContract(db.Model):
    __tablename__ = 'employee_contracts'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_no = db.Column(db.String(50), db.ForeignKey('employees.employee_no'), nullable=False)
    number = db.Column(db.String(100), nullable=False, unique=True)
    type = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    sign_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    created_by = db.Column(db.String(50))
    updated_by = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    @validates('status')
    def validate_status(self, key, status):
        allowed_statuses = ['active', 'expired', 'terminated']
        if status not in allowed_statuses:
            raise ValueError(f'Invalid status. Must be one of: {", ".join(allowed_statuses)}')
        return status

    @validates('type')
    def validate_type(self, key, type_):
        allowed_types = ['fixed_term', 'non_fixed_term', 'internship', 'probation']
        if type_ not in allowed_types:
            raise ValueError(f'Invalid contract type. Must be one of: {", ".join(allowed_types)}')
        return type_

    @validates('duration')
    def validate_duration(self, key, duration):
        if duration < 0 or duration > 100:
            raise ValueError('Duration must be between 0 and 100 years')
        return duration

    def to_dict(self):
        return {
            'id': self.id,
            'employee_no': self.employee_no,
            'number': self.number,
            'type': self.type,
            'duration': self.duration,
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
            'end_date': self.end_date.strftime('%Y-%m-%d') if self.end_date else None,
            'sign_date': self.sign_date.strftime('%Y-%m-%d') if self.sign_date else None,
            'status': self.status
        } 
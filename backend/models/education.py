from .. import db
from datetime import datetime

class EmployeeEducation(db.Model):
    __tablename__ = 'employee_education'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_no = db.Column(db.String(50), db.ForeignKey('employees.employee_no'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    school = db.Column(db.String(100), nullable=False)
    major = db.Column(db.String(100), nullable=False)
    degree = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    created_by = db.Column(db.String(50))
    updated_by = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'employee_no': self.employee_no,
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
            'end_date': self.end_date.strftime('%Y-%m-%d') if self.end_date else None,
            'school': self.school,
            'major': self.major,
            'degree': self.degree,
            'description': self.description
        }
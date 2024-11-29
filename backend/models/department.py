from .. import db
from .base import BaseModel

class Department(BaseModel):
    """部门表"""
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    leader_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    description = db.Column(db.String(200))
    status = db.Column(db.Boolean, default=True)  # True: 启用, False: 禁用
    
    # 关系
    parent = db.relationship('Department', remote_side=[id], backref='children')
    leader = db.relationship('User', backref='led_departments')
    
    def to_dict(self, include_children=True):
        """转换为字典"""
        data = {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'parent_id': self.parent_id,
            'leader_id': self.leader_id,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'leader': self.leader.username if self.leader else None
        }
        if include_children and self.children:
            data['children'] = [child.to_dict(include_children=True) for child in self.children]
        return data 
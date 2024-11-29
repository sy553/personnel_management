from .. import db
from .base import BaseModel
from datetime import datetime

class BudgetAdjustment(BaseModel):
    """预算调整记录表"""
    __tablename__ = 'budget_adjustments'
    
    id = db.Column(db.Integer, primary_key=True)
    budget_id = db.Column(db.Integer, db.ForeignKey('department_budgets.id'), nullable=False)
    original_amount = db.Column(db.Numeric(12, 2), nullable=False)
    adjusted_amount = db.Column(db.Numeric(12, 2), nullable=False)
    adjustment_type = db.Column(db.String(20), nullable=False)  # modify修改, increase增加, decrease减少
    reason = db.Column(db.String(200))
    notes = db.Column(db.String(500))
    
    # 关系
    budget = db.relationship('DepartmentBudget', backref='adjustments')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'budget_id': self.budget_id,
            'original_amount': float(self.original_amount),
            'adjusted_amount': float(self.adjusted_amount),
            'adjustment_type': self.adjustment_type,
            'reason': self.reason,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 
from .. import db
from .base import BaseModel

class AlertRule(BaseModel):
    """预警规则表"""
    __tablename__ = 'alert_rules'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    rule_type = db.Column(db.String(50), nullable=False)  # budget_exceed预算超支, expense_abnormal费用异常
    threshold = db.Column(db.Integer, nullable=False)  # 阈值（百分比）
    alert_level = db.Column(db.String(20), nullable=False)  # info普通, warning警告, critical严重
    notify_email = db.Column(db.Boolean, default=True)  # 是否发送邮件通知
    status = db.Column(db.Boolean, default=True)  # 规则是否启用
    description = db.Column(db.String(200))
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'rule_type': self.rule_type,
            'threshold': self.threshold,
            'alert_level': self.alert_level,
            'notify_email': self.notify_email,
            'status': self.status,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 
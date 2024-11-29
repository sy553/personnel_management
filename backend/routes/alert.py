from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..models.alert_rule import AlertRule
from ..models.budget import DepartmentBudget
from ..models.department import Department
from ..models.salary import Salary
from ..models.employee import Employee
from .. import db
from sqlalchemy import and_, func
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

alert_bp = Blueprint('alert', __name__)

@alert_bp.route('/rules', methods=['POST'])
@jwt_required()
def create_rule():
    """创建预警规则"""
    try:
        data = request.get_json()
        
        rule = AlertRule(
            name=data['name'],
            rule_type=data['rule_type'],
            threshold=data['threshold'],
            alert_level=data['alert_level'],
            notify_email=data.get('notify_email', True),
            description=data.get('description', '')
        )
        
        db.session.add(rule)
        db.session.commit()
        
        return jsonify(rule.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@alert_bp.route('/rules/<int:rule_id>', methods=['PUT'])
@jwt_required()
def update_rule(rule_id):
    """更新预警规则"""
    try:
        rule = AlertRule.query.get_or_404(rule_id)
        data = request.get_json()
        
        for key, value in data.items():
            if hasattr(rule, key):
                setattr(rule, key, value)
                
        db.session.commit()
        
        return jsonify(rule.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@alert_bp.route('/check', methods=['GET'])
@jwt_required()
def check_alerts():
    """检查预警情况"""
    try:
        year = request.args.get('year', datetime.now().year, type=int)
        month = request.args.get('month', datetime.now().month, type=int)
        
        # 获取启用的预警规则
        rules = AlertRule.query.filter_by(status=True).all()
        
        # 获取部门预算执行情况
        execution_data = db.session.query(
            Department.name.label('department'),
            DepartmentBudget.total_budget,
            func.sum(Salary.net_salary).label('actual_expense')
        ).join(
            DepartmentBudget,
            and_(
                Department.id == DepartmentBudget.department_id,
                DepartmentBudget.year == year,
                DepartmentBudget.month == month
            )
        ).join(
            Employee,
            Employee.department_id == Department.id
        ).join(
            Salary,
            and_(
                Salary.employee_id == Employee.id,
                Salary.year == year,
                Salary.month == month
            )
        ).group_by(
            Department.name,
            DepartmentBudget.total_budget
        ).all()
        
        # 分析预警情况
        alerts = []
        for dept, budget, expense in execution_data:
            if expense is None:
                continue
                
            execution_rate = (expense / budget * 100) if budget else 0
            
            # 检查每个规则
            for rule in rules:
                if rule.rule_type == 'budget_exceed' and execution_rate >= rule.threshold:
                    alert = {
                        'department': dept,
                        'alert_type': 'budget_exceed',
                        'alert_level': rule.alert_level,
                        'message': f'部门 {dept} 预算执行率达到 {execution_rate:.1f}%，超过阈值 {rule.threshold}%',
                        'execution_rate': float(execution_rate),
                        'budget': float(budget),
                        'expense': float(expense)
                    }
                    alerts.append(alert)
                    
                    # 发送邮件通知
                    if rule.notify_email:
                        send_alert_email(alert)
                        
        return jsonify(alerts), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def send_alert_email(alert_data):
    """发送预警邮件"""
    try:
        # 邮件配置
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.example.com')
        smtp_port = int(os.getenv('SMTP_PORT', 587))
        smtp_user = os.getenv('SMTP_USER', 'user@example.com')
        smtp_password = os.getenv('SMTP_PASSWORD', 'password')
        
        # 创建邮件
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = os.getenv('ALERT_EMAIL', 'admin@example.com')
        msg['Subject'] = f"预算预警通知 - {alert_data['department']}"
        
        # 邮件内容
        body = f"""
        预警通知：
        
        部门：{alert_data['department']}
        预警类型：{alert_data['alert_type']}
        预警级别：{alert_data['alert_level']}
        
        预算金额：{alert_data['budget']:,.2f}
        实际支出：{alert_data['expense']:,.2f}
        执行率：{alert_data['execution_rate']:.1f}%
        
        消息：{alert_data['message']}
        
        请及时处理！
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # 发送邮件
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            
    except Exception as e:
        print(f"Failed to send alert email: {str(e)}") 
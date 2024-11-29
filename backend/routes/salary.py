from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..models.salary import Salary, SalaryConfig
from ..models.employee import Employee
from ..models.attendance import Attendance
from .. import db
from datetime import datetime, date
from sqlalchemy import and_
from decimal import Decimal

salary_bp = Blueprint('salary', __name__)

@salary_bp.route('/configs', methods=['POST'])
@jwt_required()
def create_salary_config():
    """创建薪资配置"""
    try:
        data = request.get_json()
        
        # 验证必要字段
        required_fields = ['employee_id', 'base_salary', 'effective_date']
        if not all(k in data for k in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
            
        # 检查员工是否存在
        employee = Employee.query.get_or_404(data['employee_id'])
        
        # 创建薪资配置
        config = SalaryConfig(
            employee_id=data['employee_id'],
            base_salary=data['base_salary'],
            overtime_rate=data.get('overtime_rate', 1.5),
            social_security_rate=data.get('social_security_rate', 0.1),
            effective_date=datetime.strptime(data['effective_date'], '%Y-%m-%d').date(),
            status=True
        )
        
        # 将之前的配置设置为无效
        old_configs = SalaryConfig.query.filter_by(
            employee_id=data['employee_id'],
            status=True
        ).all()
        for old_config in old_configs:
            old_config.status = False
            
        db.session.add(config)
        db.session.commit()
        
        return jsonify(config.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@salary_bp.route('/calculate', methods=['POST'])
@jwt_required()
def calculate_salary():
    """计算月度薪资"""
    try:
        data = request.get_json()
        
        # 验证必要字段
        if not all(k in data for k in ['employee_id', 'year', 'month']):
            return jsonify({'error': 'Missing required fields'}), 400
            
        employee_id = data['employee_id']
        year = data['year']
        month = data['month']
        
        # 检查是否已经生成过工资单
        existing_salary = Salary.query.filter_by(
            employee_id=employee_id,
            year=year,
            month=month
        ).first()
        
        if existing_salary:
            return jsonify({'error': 'Salary already calculated for this month'}), 400
            
        # 获取薪资配置
        config = SalaryConfig.query.filter(
            and_(
                SalaryConfig.employee_id == employee_id,
                SalaryConfig.status == True,
                SalaryConfig.effective_date <= date(year, month, 1)
            )
        ).order_by(SalaryConfig.effective_date.desc()).first()
        
        if not config:
            return jsonify({'error': 'No valid salary configuration found'}), 400
            
        # 计算工资
        base_salary = Decimal(str(config.base_salary))
        
        # 计算加班费
        overtime_hours = 0  # 这里需要从考勤记录中计算加班时间
        overtime_pay = overtime_hours * base_salary / 174 * config.overtime_rate
        
        # 计算社保
        social_security = base_salary * config.social_security_rate
        
        # 计算个税（简化计算）
        taxable_income = base_salary + overtime_pay - social_security
        tax = Decimal('0')
        if taxable_income > 5000:
            tax = (taxable_income - 5000) * Decimal('0.1')
            
        # 计算实发工资
        net_salary = base_salary + overtime_pay - social_security - tax + Decimal(str(data.get('bonus', 0))) - Decimal(str(data.get('deductions', 0)))
        
        # 创建工资单
        salary = Salary(
            employee_id=employee_id,
            year=year,
            month=month,
            base_salary=base_salary,
            overtime_pay=overtime_pay,
            bonus=data.get('bonus', 0),
            deductions=data.get('deductions', 0),
            social_security=social_security,
            tax=tax,
            net_salary=net_salary,
            status='pending',
            notes=data.get('notes')
        )
        
        db.session.add(salary)
        db.session.commit()
        
        return jsonify(salary.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@salary_bp.route('/approve/<int:salary_id>', methods=['PUT'])
@jwt_required()
def approve_salary(salary_id):
    """审批工资单"""
    try:
        salary = Salary.query.get_or_404(salary_id)
        
        if salary.status != 'pending':
            return jsonify({'error': 'Salary already processed'}), 400
            
        salary.status = 'paid'
        salary.payment_date = datetime.now()
        
        db.session.commit()
        return jsonify(salary.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@salary_bp.route('/report', methods=['GET'])
@jwt_required()
def salary_report():
    """获取薪资报表"""
    try:
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)
        employee_id = request.args.get('employee_id', type=int)
        department_id = request.args.get('department_id', type=int)
        
        # 构建查询
        query = Salary.query
        
        # 应用过滤条件
        if year:
            query = query.filter_by(year=year)
        if month:
            query = query.filter_by(month=month)
        if employee_id:
            query = query.filter_by(employee_id=employee_id)
        if department_id:
            query = query.join(Employee).filter(Employee.department_id == department_id)
            
        salaries = query.all()
        
        return jsonify([salary.to_dict() for salary in salaries]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500 
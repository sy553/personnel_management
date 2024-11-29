from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..models.budget import DepartmentBudget
from ..models.department import Department
from ..models.salary import Salary
from ..models.employee import Employee
from ..models.budget_adjustment import BudgetAdjustment
from .. import db
from sqlalchemy import and_, func, distinct
from datetime import datetime
from decimal import Decimal

budget_bp = Blueprint('budget', __name__)

@budget_bp.route('/budgets', methods=['POST'])
@jwt_required()
def create_budget():
    """创建部门预算"""
    try:
        data = request.get_json()
        
        # 验证必要字段
        required_fields = ['department_id', 'year', 'month', 'salary_budget']
        if not all(k in data for k in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
            
        # 检查部门是否存在
        department = Department.query.get_or_404(data['department_id'])
        
        # 检查是否已存在预算
        existing_budget = DepartmentBudget.query.filter_by(
            department_id=data['department_id'],
            year=data['year'],
            month=data['month']
        ).first()
        
        if existing_budget:
            return jsonify({'error': 'Budget already exists for this period'}), 400
            
        # 计算总预算
        total_budget = (
            Decimal(str(data['salary_budget'])) +
            Decimal(str(data.get('overtime_budget', 0))) +
            Decimal(str(data.get('bonus_budget', 0))) +
            Decimal(str(data.get('other_budget', 0)))
        )
        
        # 创建预算
        budget = DepartmentBudget(
            department_id=data['department_id'],
            year=data['year'],
            month=data['month'],
            salary_budget=data['salary_budget'],
            overtime_budget=data.get('overtime_budget', 0),
            bonus_budget=data.get('bonus_budget', 0),
            other_budget=data.get('other_budget', 0),
            total_budget=total_budget,
            notes=data.get('notes'),
            status='draft'
        )
        
        db.session.add(budget)
        db.session.commit()
        
        return jsonify(budget.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@budget_bp.route('/budgets/<int:budget_id>/approve', methods=['PUT'])
@jwt_required()
def approve_budget(budget_id):
    """审批部门预算"""
    try:
        budget = DepartmentBudget.query.get_or_404(budget_id)
        
        if budget.status != 'draft':
            return jsonify({'error': 'Budget already approved'}), 400
            
        budget.status = 'approved'
        db.session.commit()
        
        return jsonify(budget.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@budget_bp.route('/budgets/execution', methods=['GET'])
@jwt_required()
def budget_execution():
    """获取预算执行情况"""
    try:
        year = request.args.get('year', datetime.now().year, type=int)
        month = request.args.get('month', datetime.now().month, type=int)
        department_id = request.args.get('department_id', type=int)
        
        # 构建查询
        query = db.session.query(
            DepartmentBudget,
            func.sum(Salary.net_salary).label('actual_expense')
        ).join(
            Department,
            Department.id == DepartmentBudget.department_id
        ).join(
            Employee,
            Employee.department_id == Department.id
        ).join(
            Salary,
            and_(
                Salary.employee_id == Employee.id,
                Salary.year == DepartmentBudget.year,
                Salary.month == DepartmentBudget.month
            ),
            isouter=True
        ).filter(
            DepartmentBudget.year == year,
            DepartmentBudget.month == month,
            DepartmentBudget.status == 'approved'
        )
        
        if department_id:
            query = query.filter(DepartmentBudget.department_id == department_id)
            
        results = query.group_by(DepartmentBudget.id).all()
        
        return jsonify([{
            **budget.to_dict(),
            'actual_expense': float(actual) if actual else 0,
            'execution_rate': float(actual / budget.total_budget * 100) if actual else 0,
            'remaining_budget': float(budget.total_budget - (actual or 0))
        } for budget, actual in results]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@budget_bp.route('/budgets/alert', methods=['GET'])
@jwt_required()
def budget_alert():
    """获取预算预警信息"""
    try:
        year = request.args.get('year', datetime.now().year, type=int)
        month = request.args.get('month', datetime.now().month, type=int)
        
        # 获取所有部门的预算执行情况
        execution_data = db.session.query(
            DepartmentBudget,
            func.sum(Salary.net_salary).label('actual_expense')
        ).join(
            Department,
            Department.id == DepartmentBudget.department_id
        ).join(
            Employee,
            Employee.department_id == Department.id
        ).join(
            Salary,
            and_(
                Salary.employee_id == Employee.id,
                Salary.year == DepartmentBudget.year,
                Salary.month == DepartmentBudget.month
            ),
            isouter=True
        ).filter(
            DepartmentBudget.year == year,
            DepartmentBudget.month == month,
            DepartmentBudget.status == 'approved'
        ).group_by(DepartmentBudget.id).all()
        
        # 分析预警情况
        alerts = []
        for budget, actual in execution_data:
            actual = actual or 0
            execution_rate = (actual / budget.total_budget * 100) if actual else 0
            
            alert_level = 'normal'
            if execution_rate >= 90:
                alert_level = 'critical'
            elif execution_rate >= 80:
                alert_level = 'warning'
                
            alerts.append({
                'department_id': budget.department_id,
                'department_name': budget.department.name,
                'budget_amount': float(budget.total_budget),
                'actual_expense': float(actual),
                'execution_rate': float(execution_rate),
                'remaining_budget': float(budget.total_budget - actual),
                'alert_level': alert_level
            })
            
        return jsonify(alerts), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@budget_bp.route('/budgets/<int:budget_id>/adjust', methods=['PUT'])
@jwt_required()
def adjust_budget(budget_id):
    """调整部门预算"""
    try:
        budget = DepartmentBudget.query.get_or_404(budget_id)
        data = request.get_json()
        
        # 验证预算状态
        if budget.status != 'approved':
            return jsonify({'error': 'Only approved budgets can be adjusted'}), 400
            
        # 记录原始预算数据
        original_data = {
            'salary_budget': float(budget.salary_budget),
            'overtime_budget': float(budget.overtime_budget),
            'bonus_budget': float(budget.bonus_budget),
            'other_budget': float(budget.other_budget),
            'total_budget': float(budget.total_budget)
        }
        
        # 更新预算金额
        if 'salary_budget' in data:
            budget.salary_budget = data['salary_budget']
        if 'overtime_budget' in data:
            budget.overtime_budget = data['overtime_budget']
        if 'bonus_budget' in data:
            budget.bonus_budget = data['bonus_budget']
        if 'other_budget' in data:
            budget.other_budget = data['other_budget']
            
        # 重新计算总预算
        budget.total_budget = (
            Decimal(str(budget.salary_budget)) +
            Decimal(str(budget.overtime_budget)) +
            Decimal(str(budget.bonus_budget)) +
            Decimal(str(budget.other_budget))
        )
        
        # 创建预算调整记录
        adjustment = BudgetAdjustment(
            budget_id=budget.id,
            original_amount=original_data['total_budget'],
            adjusted_amount=float(budget.total_budget),
            adjustment_type='modify',
            reason=data.get('reason', ''),
            notes=data.get('notes', '')
        )
        
        db.session.add(adjustment)
        db.session.commit()
        
        return jsonify({
            'budget': budget.to_dict(),
            'adjustment': {
                'id': adjustment.id,
                'original_amount': float(adjustment.original_amount),
                'adjusted_amount': float(adjustment.adjusted_amount),
                'difference': float(adjustment.adjusted_amount - adjustment.original_amount),
                'reason': adjustment.reason,
                'created_at': adjustment.created_at.isoformat()
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@budget_bp.route('/budgets/<int:budget_id>/history', methods=['GET'])
@jwt_required()
def budget_history(budget_id):
    """获取预算调整历史"""
    try:
        budget = DepartmentBudget.query.get_or_404(budget_id)
        
        # 获取所有调整记录
        adjustments = BudgetAdjustment.query.filter_by(
            budget_id=budget_id
        ).order_by(BudgetAdjustment.created_at.desc()).all()
        
        return jsonify({
            'budget': budget.to_dict(),
            'adjustments': [{
                'id': adj.id,
                'original_amount': float(adj.original_amount),
                'adjusted_amount': float(adj.adjusted_amount),
                'difference': float(adj.adjusted_amount - adj.original_amount),
                'adjustment_type': adj.adjustment_type,
                'reason': adj.reason,
                'notes': adj.notes,
                'created_at': adj.created_at.isoformat()
            } for adj in adjustments]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@budget_bp.route('/budgets/analysis', methods=['GET'])
@jwt_required()
def budget_analysis():
    """获取预算分析报表"""
    try:
        year = request.args.get('year', datetime.now().year, type=int)
        month = request.args.get('month', datetime.now().month, type=int)
        
        # 获取所有部门的预算和实际支出
        stats = db.session.query(
            Department.name.label('department'),
            DepartmentBudget.total_budget,
            func.sum(Salary.net_salary).label('actual_expense'),
            func.count(distinct(Employee.id)).label('employee_count')
        ).join(
            DepartmentBudget,
            and_(
                Department.id == DepartmentBudget.department_id,
                DepartmentBudget.year == year,
                DepartmentBudget.month == month,
                DepartmentBudget.status == 'approved'
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
            ),
            isouter=True
        ).group_by(
            Department.id,
            Department.name,
            DepartmentBudget.total_budget
        ).all()
        
        return jsonify([{
            'department': dept,
            'budget_amount': float(budget),
            'actual_expense': float(actual) if actual else 0,
            'employee_count': emp_count,
            'execution_rate': float(actual / budget * 100) if actual else 0,
            'per_capita_budget': float(budget / emp_count) if emp_count > 0 else 0,
            'per_capita_expense': float(actual / emp_count) if emp_count > 0 and actual else 0
        } for dept, budget, actual, emp_count in stats]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500 
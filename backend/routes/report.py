from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..models.employee import Employee
from ..models.attendance import Attendance, Leave
from ..models.salary import Salary
from ..models.department import Department
from ..models.employee_change import EmployeeChange
from .. import db
from sqlalchemy import func, and_, case, extract, distinct
from datetime import datetime, date
import calendar

report_bp = Blueprint('report', __name__)

@report_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    """获取仪表盘数据"""
    try:
        # 获取基础统计数据
        total_employees = Employee.query.count()
        total_departments = Department.query.count()
        
        # 获取在职/离职员工数量
        active_employees = Employee.query.filter_by(status='active').count()
        inactive_employees = Employee.query.filter_by(status='inactive').count()
        
        # 获取本月考勤统计
        today = date.today()
        first_day = date(today.year, today.month, 1)
        last_day = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
        
        attendance_stats = db.session.query(
            Attendance.status,
            func.count(Attendance.id)
        ).filter(
            Attendance.date.between(first_day, last_day)
        ).group_by(Attendance.status).all()
        
        # 获取本月请假统计
        leave_stats = db.session.query(
            Leave.type,
            func.count(Leave.id)
        ).filter(
            Leave.start_date <= last_day,
            Leave.end_date >= first_day,
            Leave.status == 'approved'
        ).group_by(Leave.type).all()
        
        return jsonify({
            'employee_stats': {
                'total': total_employees,
                'active': active_employees,
                'inactive': inactive_employees
            },
            'department_count': total_departments,
            'attendance_stats': dict(attendance_stats),
            'leave_stats': dict(leave_stats)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@report_bp.route('/department/headcount', methods=['GET'])
@jwt_required()
def department_headcount():
    """获取部门人数统计"""
    try:
        stats = db.session.query(
            Department.name,
            func.count(Employee.id)
        ).join(
            Employee,
            and_(
                Employee.department_id == Department.id,
                Employee.status == 'active'
            ),
            isouter=True
        ).group_by(Department.id, Department.name).all()
        
        return jsonify([{
            'department': name,
            'headcount': count
        } for name, count in stats]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@report_bp.route('/attendance/monthly', methods=['GET'])
@jwt_required()
def monthly_attendance():
    """获取月度考勤统计"""
    try:
        year = request.args.get('year', datetime.now().year, type=int)
        month = request.args.get('month', datetime.now().month, type=int)
        department_id = request.args.get('department_id', type=int)
        
        # 构建基础查询
        query = db.session.query(
            Employee.name,
            Employee.employee_no,
            func.count(case(
                (Attendance.status == 'normal', 1),
                else_=0
            )).label('normal_days'),
            func.count(case(
                (Attendance.status == 'late', 1),
                else_=0
            )).label('late_days'),
            func.count(case(
                (Attendance.status == 'early', 1),
                else_=0
            )).label('early_days'),
            func.count(case(
                (Attendance.status == 'absent', 1),
                else_=0
            )).label('absent_days')
        ).join(
            Attendance,
            and_(
                Employee.id == Attendance.employee_id,
                extract('year', Attendance.date) == year,
                extract('month', Attendance.date) == month
            ),
            isouter=True
        )
        
        # 应用部门过滤
        if department_id:
            query = query.filter(Employee.department_id == department_id)
            
        # 分组并获取结果
        stats = query.group_by(Employee.id, Employee.name, Employee.employee_no).all()
        
        return jsonify([{
            'employee_name': name,
            'employee_no': no,
            'normal_days': normal,
            'late_days': late,
            'early_days': early,
            'absent_days': absent
        } for name, no, normal, late, early, absent in stats]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@report_bp.route('/salary/summary', methods=['GET'])
@jwt_required()
def salary_summary():
    """获取薪资汇总报表"""
    try:
        year = request.args.get('year', datetime.now().year, type=int)
        month = request.args.get('month', datetime.now().month, type=int)
        department_id = request.args.get('department_id', type=int)
        
        # 构建基础查询
        query = db.session.query(
            Department.name.label('department'),
            func.count(Employee.id).label('employee_count'),
            func.sum(Salary.base_salary).label('total_base'),
            func.sum(Salary.overtime_pay).label('total_overtime'),
            func.sum(Salary.bonus).label('total_bonus'),
            func.sum(Salary.net_salary).label('total_net')
        ).join(
            Employee, Employee.department_id == Department.id
        ).join(
            Salary,
            and_(
                Salary.employee_id == Employee.id,
                Salary.year == year,
                Salary.month == month
            )
        )
        
        # 应用部门过滤
        if department_id:
            query = query.filter(Department.id == department_id)
            
        # 分组并获取结果
        stats = query.group_by(Department.id, Department.name).all()
        
        return jsonify([{
            'department': dept,
            'employee_count': count,
            'total_base_salary': float(base),
            'total_overtime_pay': float(overtime),
            'total_bonus': float(bonus),
            'total_net_salary': float(net)
        } for dept, count, base, overtime, bonus, net in stats]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@report_bp.route('/employee/changes', methods=['GET'])
@jwt_required()
def employee_changes():
    """获取员工异动报表"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        change_type = request.args.get('change_type')
        department_id = request.args.get('department_id', type=int)
        
        # 构建查询
        query = EmployeeChange.query
        
        # 应用过滤条件
        if start_date:
            query = query.filter(EmployeeChange.effective_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        if end_date:
            query = query.filter(EmployeeChange.effective_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        if change_type:
            query = query.filter_by(change_type=change_type)
        if department_id:
            query = query.filter(
                db.or_(
                    EmployeeChange.old_department_id == department_id,
                    EmployeeChange.new_department_id == department_id
                )
            )
            
        # 获取统计数据
        changes = query.order_by(EmployeeChange.effective_date.desc()).all()
        
        # 按类型统计数量
        stats = db.session.query(
            EmployeeChange.change_type,
            func.count(EmployeeChange.id)
        ).filter(
            EmployeeChange.id.in_([c.id for c in changes])
        ).group_by(EmployeeChange.change_type).all()
        
        return jsonify({
            'changes': [change.to_dict() for change in changes],
            'statistics': dict(stats),
            'total': len(changes)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@report_bp.route('/department/changes', methods=['GET'])
@jwt_required()
def department_changes():
    """获取部门人员变动统计"""
    try:
        year = request.args.get('year', datetime.now().year, type=int)
        month = request.args.get('month', datetime.now().month, type=int)
        
        # 获取指定月份的起止日期
        start_date = date(year, month, 1)
        end_date = date(year, month, calendar.monthrange(year, month)[1])
        
        # 建查询
        stats = db.session.query(
            Department.name,
            func.count(case(
                (EmployeeChange.change_type == 'entry', 1),
                else_=0
            )).label('entry_count'),
            func.count(case(
                (EmployeeChange.change_type == 'leave', 1),
                else_=0
            )).label('leave_count'),
            func.count(case(
                (EmployeeChange.change_type == 'transfer', 1),
                else_=0
            )).label('transfer_count')
        ).join(
            EmployeeChange,
            db.or_(
                Department.id == EmployeeChange.old_department_id,
                Department.id == EmployeeChange.new_department_id
            )
        ).filter(
            EmployeeChange.effective_date.between(start_date, end_date)
        ).group_by(Department.id, Department.name).all()
        
        return jsonify([{
            'department': name,
            'entry_count': entry,
            'leave_count': leave,
            'transfer_count': transfer,
            'net_change': entry - leave
        } for name, entry, leave, transfer in stats]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@report_bp.route('/overtime/summary', methods=['GET'])
@jwt_required()
def overtime_summary():
    """获取加班统计汇总"""
    try:
        year = request.args.get('year', datetime.now().year, type=int)
        month = request.args.get('month', datetime.now().month, type=int)
        
        # 获取指定月份的起止日期
        start_date = date(year, month, 1)
        end_date = date(year, month, calendar.monthrange(year, month)[1])
        
        # 按部门统计加班情况
        dept_stats = db.session.query(
            Department.name,
            func.count(distinct(Employee.id)).label('employee_count'),
            func.count(Attendance.id).label('overtime_count'),
            func.sum(Salary.overtime_pay).label('overtime_pay')
        ).join(
            Employee, Employee.department_id == Department.id
        ).join(
            Attendance, Attendance.employee_id == Employee.id
        ).join(
            Salary, and_(
                Salary.employee_id == Employee.id,
                Salary.year == year,
                Salary.month == month
            )
        ).filter(
            Attendance.date.between(start_date, end_date),
            Attendance.clock_out > Attendance.clock_in
        ).group_by(Department.id, Department.name).all()
        
        return jsonify({
            'department_stats': [{
                'department': name,
                'employee_count': emp_count,
                'overtime_count': ot_count,
                'overtime_pay': float(ot_pay) if ot_pay else 0
            } for name, emp_count, ot_count, ot_pay in dept_stats],
            'year': year,
            'month': month
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@report_bp.route('/overtime/employee', methods=['GET'])
@jwt_required()
def employee_overtime():
    """获取员工加班明细"""
    try:
        year = request.args.get('year', datetime.now().year, type=int)
        month = request.args.get('month', datetime.now().month, type=int)
        department_id = request.args.get('department_id', type=int)
        
        # 获取指定月份的起止日期
        start_date = date(year, month, 1)
        end_date = date(year, month, calendar.monthrange(year, month)[1])
        
        # 构建基础查询
        query = db.session.query(
            Employee.name,
            Employee.employee_no,
            Department.name.label('department'),
            func.count(Attendance.id).label('overtime_days'),
            func.sum(Salary.overtime_pay).label('overtime_pay')
        ).join(
            Department, Employee.department_id == Department.id
        ).join(
            Attendance, Attendance.employee_id == Employee.id
        ).join(
            Salary, and_(
                Salary.employee_id == Employee.id,
                Salary.year == year,
                Salary.month == month
            )
        ).filter(
            Attendance.date.between(start_date, end_date),
            Attendance.clock_out > Attendance.clock_in
        )
        
        # 应用部门过滤
        if department_id:
            query = query.filter(Department.id == department_id)
            
        # 分组并获取结果
        stats = query.group_by(
            Employee.id, 
            Employee.name, 
            Employee.employee_no,
            Department.name
        ).all()
        
        return jsonify([{
            'employee_name': name,
            'employee_no': no,
            'department': dept,
            'overtime_days': ot_days,
            'overtime_pay': float(ot_pay) if ot_pay else 0
        } for name, no, dept, ot_days, ot_pay in stats]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@report_bp.route('/attendance/abnormal', methods=['GET'])
@jwt_required()
def attendance_abnormal():
    """获取考勤异常报表"""
    try:
        year = request.args.get('year', datetime.now().year, type=int)
        month = request.args.get('month', datetime.now().month, type=int)
        department_id = request.args.get('department_id', type=int)
        
        # 获取指定月份的起止日期
        start_date = date(year, month, 1)
        end_date = date(year, month, calendar.monthrange(year, month)[1])
        
        # 构建基础查询
        query = db.session.query(
            Employee.name,
            Employee.employee_no,
            Department.name.label('department'),
            func.count(case(
                (Attendance.status == 'late', 1),
                else_=0
            )).label('late_count'),
            func.count(case(
                (Attendance.status == 'early', 1),
                else_=0
            )).label('early_count'),
            func.count(case(
                (Attendance.status == 'absent', 1),
                else_=0
            )).label('absent_count')
        ).join(
            Department, Employee.department_id == Department.id
        ).join(
            Attendance, Attendance.employee_id == Employee.id
        ).filter(
            Attendance.date.between(start_date, end_date)
        )
        
        # 应用部门过滤
        if department_id:
            query = query.filter(Department.id == department_id)
            
        # 分组并获取结果
        stats = query.group_by(
            Employee.id,
            Employee.name,
            Employee.employee_no,
            Department.name
        ).having(
            db.or_(
                func.count(case((Attendance.status == 'late', 1), else_=0)) > 0,
                func.count(case((Attendance.status == 'early', 1), else_=0)) > 0,
                func.count(case((Attendance.status == 'absent', 1), else_=0)) > 0
            )
        ).all()
        
        # 获取请假记录
        leave_query = db.session.query(
            Employee.name,
            Employee.employee_no,
            Department.name.label('department'),
            Leave.type,
            func.count(Leave.id).label('leave_count'),
            func.sum(
                func.datediff(Leave.end_date, Leave.start_date) + 1
            ).label('leave_days')
        ).join(
            Department, Employee.department_id == Department.id
        ).join(
            Leave, Leave.employee_id == Employee.id
        ).filter(
            Leave.start_date <= end_date,
            Leave.end_date >= start_date,
            Leave.status == 'approved'
        )
        
        if department_id:
            leave_query = leave_query.filter(Department.id == department_id)
            
        leave_stats = leave_query.group_by(
            Employee.id,
            Employee.name,
            Employee.employee_no,
            Department.name,
            Leave.type
        ).all()
        
        return jsonify({
            'attendance_abnormal': [{
                'employee_name': name,
                'employee_no': no,
                'department': dept,
                'late_count': late,
                'early_count': early,
                'absent_count': absent,
                'total_abnormal': late + early + absent
            } for name, no, dept, late, early, absent in stats],
            'leave_statistics': [{
                'employee_name': name,
                'employee_no': no,
                'department': dept,
                'leave_type': type_,
                'leave_count': count,
                'leave_days': days
            } for name, no, dept, type_, count, days in leave_stats],
            'year': year,
            'month': month
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@report_bp.route('/attendance/department/abnormal', methods=['GET'])
@jwt_required()
def department_attendance_abnormal():
    """获取部门考勤异常汇总"""
    try:
        year = request.args.get('year', datetime.now().year, type=int)
        month = request.args.get('month', datetime.now().month, type=int)
        
        # 获取指定月份的起止日期
        start_date = date(year, month, 1)
        end_date = date(year, month, calendar.monthrange(year, month)[1])
        
        # 按部门统计考勤异常
        dept_stats = db.session.query(
            Department.name,
            func.count(distinct(Employee.id)).label('employee_count'),
            func.count(case(
                (Attendance.status == 'late', 1),
                else_=0
            )).label('late_count'),
            func.count(case(
                (Attendance.status == 'early', 1),
                else_=0
            )).label('early_count'),
            func.count(case(
                (Attendance.status == 'absent', 1),
                else_=0
            )).label('absent_count')
        ).join(
            Employee, Employee.department_id == Department.id
        ).join(
            Attendance, Attendance.employee_id == Employee.id
        ).filter(
            Attendance.date.between(start_date, end_date)
        ).group_by(Department.id, Department.name).all()
        
        return jsonify([{
            'department': name,
            'employee_count': emp_count,
            'late_count': late,
            'early_count': early,
            'absent_count': absent,
            'total_abnormal': late + early + absent,
            'abnormal_rate': round((late + early + absent) / emp_count, 2) if emp_count > 0 else 0
        } for name, emp_count, late, early, absent in dept_stats]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@report_bp.route('/department/expense', methods=['GET'])
@jwt_required()
def department_expense():
    """获取部门费用统计"""
    try:
        year = request.args.get('year', datetime.now().year, type=int)
        month = request.args.get('month', datetime.now().month, type=int)
        department_id = request.args.get('department_id', type=int)
        
        # 构建基础查询
        query = db.session.query(
            Department.name,
            func.count(distinct(Employee.id)).label('employee_count'),
            func.sum(Salary.base_salary).label('total_base_salary'),
            func.sum(Salary.overtime_pay).label('total_overtime_pay'),
            func.sum(Salary.bonus).label('total_bonus'),
            func.sum(Salary.net_salary).label('total_net_salary')
        ).join(
            Employee, Employee.department_id == Department.id
        ).join(
            Salary, and_(
                Salary.employee_id == Employee.id,
                Salary.year == year,
                Salary.month == month
            )
        )
        
        # 应用部门过滤
        if department_id:
            query = query.filter(Department.id == department_id)
            
        # 分组并获取结果
        stats = query.group_by(Department.id, Department.name).all()
        
        return jsonify([{
            'department': name,
            'employee_count': emp_count,
            'total_base_salary': float(base) if base else 0,
            'total_overtime_pay': float(ot) if ot else 0,
            'total_bonus': float(bonus) if bonus else 0,
            'total_net_salary': float(net) if net else 0,
            'average_salary': float(net / emp_count) if emp_count > 0 and net else 0
        } for name, emp_count, base, ot, bonus, net in stats]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@report_bp.route('/department/expense/trend', methods=['GET'])
@jwt_required()
def department_expense_trend():
    """获取部门费用趋势"""
    try:
        year = request.args.get('year', datetime.now().year, type=int)
        department_id = request.args.get('department_id', type=int)
        
        # 构建基础查询
        query = db.session.query(
            Department.name,
            Salary.month,
            func.count(distinct(Employee.id)).label('employee_count'),
            func.sum(Salary.net_salary).label('total_expense')
        ).join(
            Employee, Employee.department_id == Department.id
        ).join(
            Salary, and_(
                Salary.employee_id == Employee.id,
                Salary.year == year
            )
        )
        
        # 应用部门过滤
        if department_id:
            query = query.filter(Department.id == department_id)
            
        # 分组并获取结果
        stats = query.group_by(
            Department.id,
            Department.name,
            Salary.month
        ).order_by(
            Department.name,
            Salary.month
        ).all()
        
        # 重组数据为按部门分组的月度趋势
        trends = {}
        for name, month, emp_count, total in stats:
            if name not in trends:
                trends[name] = {
                    'department': name,
                    'monthly_data': []
                }
            trends[name]['monthly_data'].append({
                'month': month,
                'employee_count': emp_count,
                'total_expense': float(total) if total else 0,
                'average_expense': float(total / emp_count) if emp_count > 0 and total else 0
            })
            
        return jsonify(list(trends.values())), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@report_bp.route('/department/expense/comparison', methods=['GET'])
@jwt_required()
def department_expense_comparison():
    """获取部门费用结构对比"""
    try:
        year = request.args.get('year', datetime.now().year, type=int)
        month = request.args.get('month', datetime.now().month, type=int)
        
        # 构建查询
        stats = db.session.query(
            Department.name,
            func.sum(Salary.base_salary).label('base_salary'),
            func.sum(Salary.overtime_pay).label('overtime_pay'),
            func.sum(Salary.bonus).label('bonus'),
            func.sum(
                Salary.net_salary - Salary.base_salary - 
                Salary.overtime_pay - Salary.bonus
            ).label('other')
        ).join(
            Employee, Employee.department_id == Department.id
        ).join(
            Salary, and_(
                Salary.employee_id == Employee.id,
                Salary.year == year,
                Salary.month == month
            )
        ).group_by(Department.id, Department.name).all()
        
        return jsonify([{
            'department': name,
            'expense_structure': {
                'base_salary': float(base) if base else 0,
                'overtime_pay': float(ot) if ot else 0,
                'bonus': float(bonus) if bonus else 0,
                'other': float(other) if other else 0
            },
            'total_expense': float(
                (base if base else 0) + 
                (ot if ot else 0) + 
                (bonus if bonus else 0) + 
                (other if other else 0)
            )
        } for name, base, ot, bonus, other in stats]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@report_bp.route('/employee/cost', methods=['GET'])
@jwt_required()
def employee_cost_analysis():
    """获取员工成本分析"""
    try:
        year = request.args.get('year', datetime.now().year, type=int)
        month = request.args.get('month', datetime.now().month, type=int)
        department_id = request.args.get('department_id', type=int)
        
        # 构建基础查询
        query = db.session.query(
            Employee.id,
            Employee.name,
            Employee.employee_no,
            Department.name.label('department'),
            Employee.position,
            Salary.base_salary,
            Salary.overtime_pay,
            Salary.bonus,
            Salary.social_security,
            Salary.net_salary
        ).join(
            Department, Employee.department_id == Department.id
        ).join(
            Salary, and_(
                Salary.employee_id == Employee.id,
                Salary.year == year,
                Salary.month == month
            )
        )
        
        # 应用部门过滤
        if department_id:
            query = query.filter(Department.id == department_id)
            
        # 获取结果
        employees = query.all()
        
        # 计算额外统计信息
        total_cost = sum(emp.net_salary for emp in employees) if employees else 0
        avg_cost = total_cost / len(employees) if employees else 0
        
        return jsonify({
            'employees': [{
                'employee_id': emp.id,
                'employee_name': emp.name,
                'employee_no': emp.employee_no,
                'department': emp.department,
                'position': emp.position,
                'cost_details': {
                    'base_salary': float(emp.base_salary),
                    'overtime_pay': float(emp.overtime_pay),
                    'bonus': float(emp.bonus),
                    'social_security': float(emp.social_security),
                    'net_salary': float(emp.net_salary)
                },
                'cost_ratio': float(emp.net_salary / total_cost) if total_cost else 0
            } for emp in employees],
            'summary': {
                'total_cost': float(total_cost),
                'average_cost': float(avg_cost),
                'employee_count': len(employees)
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@report_bp.route('/employee/cost/trend', methods=['GET'])
@jwt_required()
def employee_cost_trend():
    """获取员工成本趋势"""
    try:
        employee_id = request.args.get('employee_id', type=int)
        year = request.args.get('year', datetime.now().year, type=int)
        
        if not employee_id:
            return jsonify({'error': 'Employee ID is required'}), 400
            
        # 获取员工信息
        employee = Employee.query.get_or_404(employee_id)
        
        # 获取年度薪资记录
        salary_records = Salary.query.filter(
            Salary.employee_id == employee_id,
            Salary.year == year
        ).order_by(Salary.month).all()
        
        # 计算趋势数据
        trend_data = [{
            'month': record.month,
            'base_salary': float(record.base_salary),
            'overtime_pay': float(record.overtime_pay),
            'bonus': float(record.bonus),
            'social_security': float(record.social_security),
            'net_salary': float(record.net_salary)
        } for record in salary_records]
        
        # 计算年度统计
        total_cost = sum(record.net_salary for record in salary_records)
        avg_monthly_cost = total_cost / len(salary_records) if salary_records else 0
        
        return jsonify({
            'employee_info': {
                'id': employee.id,
                'name': employee.name,
                'employee_no': employee.employee_no,
                'department': employee.department.name,
                'position': employee.position
            },
            'trend_data': trend_data,
            'annual_summary': {
                'total_cost': float(total_cost),
                'average_monthly_cost': float(avg_monthly_cost),
                'months_count': len(salary_records)
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@report_bp.route('/employee/cost/comparison', methods=['GET'])
@jwt_required()
def employee_cost_comparison():
    """获取员工成本对比"""
    try:
        year = request.args.get('year', datetime.now().year, type=int)
        month = request.args.get('month', datetime.now().month, type=int)
        
        # 按职位分组的成本统计
        position_stats = db.session.query(
            Employee.position,
            func.count(distinct(Employee.id)).label('employee_count'),
            func.avg(Salary.net_salary).label('avg_cost'),
            func.min(Salary.net_salary).label('min_cost'),
            func.max(Salary.net_salary).label('max_cost')
        ).join(
            Salary, and_(
                Salary.employee_id == Employee.id,
                Salary.year == year,
                Salary.month == month
            )
        ).group_by(Employee.position).all()
        
        # 计算总体统计
        total_stats = db.session.query(
            func.count(distinct(Employee.id)).label('total_employees'),
            func.avg(Salary.net_salary).label('overall_avg'),
            func.min(Salary.net_salary).label('overall_min'),
            func.max(Salary.net_salary).label('overall_max')
        ).join(
            Salary, and_(
                Salary.employee_id == Employee.id,
                Salary.year == year,
                Salary.month == month
            )
        ).first()
        
        return jsonify({
            'position_comparison': [{
                'position': pos,
                'employee_count': count,
                'average_cost': float(avg),
                'minimum_cost': float(min_),
                'maximum_cost': float(max_),
                'cost_range': float(max_ - min_)
            } for pos, count, avg, min_, max_ in position_stats],
            'overall_statistics': {
                'total_employees': total_stats[0],
                'average_cost': float(total_stats[1]),
                'minimum_cost': float(total_stats[2]),
                'maximum_cost': float(total_stats[3]),
                'cost_range': float(total_stats[3] - total_stats[2])
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500 
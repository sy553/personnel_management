from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.attendance import Attendance, Leave
from ..models.employee import Employee
from .. import db
from datetime import datetime, time

attendance_bp = Blueprint('attendance', __name__, url_prefix='/api/attendance')

@attendance_bp.route('/clock-in', methods=['POST'])
@jwt_required()
def clock_in():
    """员工上班打卡"""
    try:
        data = request.get_json()
        employee_id = data.get('employee_id')
        
        if not employee_id:
            return jsonify({'error': 'Employee ID is required'}), 400
            
        # 检查员工是否存在
        employee = Employee.query.get_or_404(employee_id)
        
        # 获取今天的日期和当前时间
        today = datetime.now().date()
        current_time = datetime.now().time()
        
        # 检查是否已经打卡
        attendance = Attendance.query.filter_by(
            employee_id=employee_id,
            date=today
        ).first()
        
        if attendance and attendance.clock_in:
            return jsonify({'error': 'Already clocked in today'}), 400
            
        # 判断是否迟到（假设9:00为上班时间）
        status = 'normal' if current_time <= time(9, 0) else 'late'
        
        if not attendance:
            attendance = Attendance(
                employee_id=employee_id,
                date=today,
                clock_in=current_time,
                status=status
            )
            db.session.add(attendance)
        else:
            attendance.clock_in = current_time
            attendance.status = status
            
        db.session.commit()
        return jsonify(attendance.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@attendance_bp.route('/clock-out', methods=['POST'])
@jwt_required()
def clock_out():
    """员工下班打卡"""
    try:
        data = request.get_json()
        employee_id = data.get('employee_id')
        
        if not employee_id:
            return jsonify({'error': 'Employee ID is required'}), 400
            
        # 获取今天的日期和当前时间
        today = datetime.now().date()
        current_time = datetime.now().time()
        
        # 获取今天的考勤记录
        attendance = Attendance.query.filter_by(
            employee_id=employee_id,
            date=today
        ).first()
        
        if not attendance or not attendance.clock_in:
            return jsonify({'error': 'No clock-in record found'}), 400
            
        # 判断是否早退（假设18:00为下班时间）
        if current_time < time(18, 0):
            attendance.status = 'early'
            
        attendance.clock_out = current_time
        db.session.commit()
        
        return jsonify(attendance.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@attendance_bp.route('/leaves', methods=['POST'])
@jwt_required()
def apply_leave():
    """申请请假"""
    try:
        data = request.get_json()
        
        # 验证必要字段
        required_fields = ['employee_id', 'type', 'start_date', 'end_date', 'reason']
        if not all(k in data for k in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
            
        # 检查日期格式
        try:
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
            
        # 检查日期有效性
        if start_date > end_date:
            return jsonify({'error': 'Start date must be before end date'}), 400
            
        # 创建请假记录
        leave = Leave(
            employee_id=data['employee_id'],
            type=data['type'],
            start_date=start_date,
            end_date=end_date,
            reason=data['reason'],
            status='pending'
        )
        
        db.session.add(leave)
        db.session.commit()
        
        return jsonify(leave.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@attendance_bp.route('/leaves/<int:leave_id>/approve', methods=['PUT'])
@jwt_required()
def approve_leave(leave_id):
    """审批请假"""
    try:
        data = request.get_json()
        status = data.get('status')
        
        if status not in ['approved', 'rejected']:
            return jsonify({'error': 'Invalid status'}), 400
            
        leave = Leave.query.get_or_404(leave_id)
        current_user_id = get_jwt_identity()
        
        leave.status = status
        leave.approver_id = current_user_id
        db.session.commit()
        
        return jsonify(leave.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@attendance_bp.route('/attendance/report', methods=['GET'])
@jwt_required()
def attendance_report():
    """获取考勤报表"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        employee_id = request.args.get('employee_id')
        department_id = request.args.get('department_id')
        
        # 构建查询
        query = Attendance.query
        
        # 应用过滤条件
        if start_date:
            query = query.filter(Attendance.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        if end_date:
            query = query.filter(Attendance.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        if employee_id:
            query = query.filter_by(employee_id=employee_id)
        if department_id:
            query = query.join(Employee).filter(Employee.department_id == department_id)
            
        attendances = query.all()
        
        return jsonify([att.to_dict() for att in attendances]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500 
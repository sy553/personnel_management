from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..models.department import Department
from .. import db
from flask_cors import cross_origin
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

department_bp = Blueprint('department', __name__)

@department_bp.route('/departments', methods=['GET'])
@jwt_required()
def get_departments():
    """获取部门列表（树形结构）"""
    try:
        # 只获取顶级部门，子部门会通过递归获取
        departments = Department.query.filter_by(parent_id=None).all()
        logger.info(f"成功获取到 {len(departments)} 个部门")
        return jsonify([dept.to_dict() for dept in departments]), 200
    except Exception as e:
        logger.error(f"获取部门列表失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

@department_bp.route('/all', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_all_departments():
    """获取所有部门（平铺结构）"""
    # 处理 OPTIONS 请求
    if request.method == 'OPTIONS':
        response = jsonify({'code': 200})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        return response

    try:
        departments = Department.query.filter_by(status=True).all()
        return jsonify({
            'code': 200,
            'data': {
                'departments': [
                    {
                        'id': dept.id,
                        'name': dept.name,
                        'code': dept.code,
                        'parent_id': dept.parent_id,
                        'leader_id': dept.leader_id,
                        'description': dept.description,
                        'status': dept.status
                    }
                    for dept in departments
                ]
            }
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取部门列表失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取部门列表失败: {str(e)}'
        }), 500

@department_bp.route('/departments/<int:dept_id>', methods=['GET'])
@jwt_required()
def get_department(dept_id):
    """获取单个部门详情"""
    try:
        department = Department.query.get_or_404(dept_id)
        return jsonify(department.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@department_bp.route('/departments', methods=['POST'])
@jwt_required()
def create_department():
    """创建新部门"""
    try:
        data = request.get_json()
        
        # 验证必要字段
        if not all(k in data for k in ['name', 'code']):
            return jsonify({'error': 'Missing required fields'}), 400
            
        # 检查部门代码是否已存在
        if Department.query.filter_by(code=data['code']).first():
            return jsonify({'error': 'Department code already exists'}), 400
            
        # 创建新部门
        new_dept = Department(
            name=data['name'],
            code=data['code'],
            parent_id=data.get('parent_id'),
            leader_id=data.get('leader_id'),
            description=data.get('description', ''),
            status=data.get('status', True)
        )
        
        db.session.add(new_dept)
        db.session.commit()
        
        return jsonify(new_dept.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@department_bp.route('/departments/<int:dept_id>', methods=['PUT'])
@jwt_required()
def update_department(dept_id):
    """更新部门信息"""
    try:
        department = Department.query.get_or_404(dept_id)
        data = request.get_json()
        
        # 更新基本信息
        if 'name' in data:
            department.name = data['name']
        if 'code' in data and data['code'] != department.code:
            if Department.query.filter_by(code=data['code']).first():
                return jsonify({'error': 'Department code already exists'}), 400
            department.code = data['code']
        if 'parent_id' in data:
            # 检查是否形成循环引用
            if data['parent_id'] == dept_id:
                return jsonify({'error': 'Department cannot be its own parent'}), 400
            department.parent_id = data['parent_id']
        if 'leader_id' in data:
            department.leader_id = data['leader_id']
        if 'description' in data:
            department.description = data['description']
        if 'status' in data:
            department.status = data['status']
            
        db.session.commit()
        return jsonify(department.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@department_bp.route('/departments/<int:dept_id>', methods=['DELETE'])
@jwt_required()
def delete_department(dept_id):
    """删除部门"""
    try:
        department = Department.query.get_or_404(dept_id)
        
        # 检查是否有子部门
        if department.children:
            return jsonify({'error': 'Cannot delete department with sub-departments'}), 400
            
        db.session.delete(department)
        db.session.commit()
        
        return jsonify({'message': 'Department deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@department_bp.route('/list', methods=['GET', 'OPTIONS'])
@cross_origin()
def list_departments():
    """获取部门列表"""
    try:
        print("开始查询部门列表")
        departments = Department.query.filter_by(status=True).all()
        print(f"查询到 {len(departments)} 个部门")
        
        department_list = []
        for dept in departments:
            dept_data = {
                'id': dept.id,
                'name': dept.name,
                'code': dept.code,
                'parent_id': dept.parent_id,
                'leader_id': dept.leader_id,
                'description': dept.description,
                'status': dept.status
            }
            department_list.append(dept_data)
            print("部门数据:", dept_data)
        
        response_data = {
            'code': 200,
            'data': {
                'departments': department_list,
                'total': len(department_list)
            }
        }
        
        print("返回的响应数据:", response_data)
        return jsonify(response_data), 200
        
    except Exception as e:
        import traceback
        error_msg = f"获取部门列表失败: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({
            'code': 500,
            'message': error_msg
        }), 500
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..models.department import Department
from .. import db

department_bp = Blueprint('department', __name__)

@department_bp.route('/list', methods=['GET'])
@jwt_required()
def get_departments():
    try:
        departments = Department.query.all()
        return jsonify({
            'code': 200,
            'message': '获取部门列表成功',
            'data': [dept.to_dict() for dept in departments]
        })
    except Exception as e:
        print(f"获取部门列表错误: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取部门列表失败: {str(e)}'
        }), 500
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..models.department import Department
from .. import db
<<<<<<< HEAD
from flask_cors import cross_origin
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
=======
>>>>>>> affba6b97d4c5bcc7a35d4ae0adb7ce3b2706e97

department_bp = Blueprint('department', __name__)

@department_bp.route('/list', methods=['GET'])
@jwt_required()
def get_departments():
    try:
<<<<<<< HEAD
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
=======
        departments = Department.query.all()
>>>>>>> affba6b97d4c5bcc7a35d4ae0adb7ce3b2706e97
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
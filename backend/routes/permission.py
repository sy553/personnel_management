from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..models.permission import Role, Permission
from .. import db

permission_bp = Blueprint('permission', __name__)

@permission_bp.route('/roles', methods=['GET'])
@jwt_required()
def get_roles():
    """获取角色列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        roles = Role.query.paginate(page=page, per_page=per_page)
        
        return jsonify({
            'roles': [role.to_dict() for role in roles.items],
            'total': roles.total,
            'pages': roles.pages,
            'current_page': roles.page
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@permission_bp.route('/roles/<int:role_id>', methods=['GET'])
@jwt_required()
def get_role(role_id):
    """获取单个角色详情"""
    try:
        role = Role.query.get_or_404(role_id)
        return jsonify(role.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@permission_bp.route('/roles', methods=['POST'])
@jwt_required()
def create_role():
    """创建新角色"""
    try:
        data = request.get_json()
        
        # 验证必要字段
        if not all(k in data for k in ['name', 'permissions']):
            return jsonify({'error': 'Missing required fields'}), 400
            
        # 检查角色名是否已存在
        if Role.query.filter_by(name=data['name']).first():
            return jsonify({'error': 'Role name already exists'}), 400
            
        # 创建新角色
        new_role = Role(
            name=data['name'],
            description=data.get('description', ''),
            permissions=data['permissions']
        )
        
        db.session.add(new_role)
        db.session.commit()
        
        return jsonify(new_role.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@permission_bp.route('/roles/<int:role_id>', methods=['PUT'])
@jwt_required()
def update_role(role_id):
    """更新角色信息"""
    try:
        role = Role.query.get_or_404(role_id)
        data = request.get_json()
        
        # 不允许修改管理员角色的关键信息
        if role.name == 'admin':
            return jsonify({'error': 'Cannot modify admin role'}), 403
            
        if 'name' in data and data['name'] != role.name:
            if Role.query.filter_by(name=data['name']).first():
                return jsonify({'error': 'Role name already exists'}), 400
            role.name = data['name']
            
        if 'description' in data:
            role.description = data['description']
            
        if 'permissions' in data:
            role.permissions = data['permissions']
            
        db.session.commit()
        return jsonify(role.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@permission_bp.route('/roles/<int:role_id>', methods=['DELETE'])
@jwt_required()
def delete_role(role_id):
    """删除角色"""
    try:
        role = Role.query.get_or_404(role_id)
        
        # 不允许删除管理员角色
        if role.name == 'admin':
            return jsonify({'error': 'Cannot delete admin role'}), 403
            
        # 检查是否有用户正在使用该角色
        if role.users:
            return jsonify({'error': 'Role is still in use by some users'}), 400
            
        db.session.delete(role)
        db.session.commit()
        
        return jsonify({'message': 'Role deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@permission_bp.route('/permissions', methods=['GET'])
@jwt_required()
def get_permissions():
    """获取所有可用权限"""
    try:
        permissions = {
            'system': [
                {'code': 'admin', 'name': '系统管理员'},
                {'code': 'manage_users', 'name': '用户管理'},
                {'code': 'manage_roles', 'name': '角色管理'}
            ],
            'employee': [
                {'code': 'manage_employees', 'name': '员工管理'},
                {'code': 'view_employees', 'name': '查看员工'}
            ],
            'attendance': [
                {'code': 'manage_attendance', 'name': '考勤管理'},
                {'code': 'view_attendance', 'name': '查看考勤'}
            ],
            'salary': [
                {'code': 'manage_salary', 'name': '薪资管理'},
                {'code': 'view_salary', 'name': '查看薪资'}
            ]
        }
        return jsonify(permissions), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500 
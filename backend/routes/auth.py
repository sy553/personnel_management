from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)
from ..models.user import User
from .. import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import cross_origin

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@jwt_required()
def register():
    try:
        data = request.get_json()
        
        # 验证必要字段
        if not all(k in data for k in ['username', 'password', 'email']):
            return jsonify({'error': 'Missing required fields'}), 400
            
        # 检查用户名是否已存在
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
            
        # 检查邮箱是否已存在
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
            
        # 创建新用户
        new_user = User.create_user(
            username=data['username'],
            password=data['password'],
            email=data['email'],
            role_id=data.get('role_id')  # 角色ID是可选的
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'message': 'User created successfully',
            'user': new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
@cross_origin()
def login():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        response.headers.add('Access-Control-Max-Age', '3600')
        return response

    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({
                'code': 400,
                'message': '用户名和密码不能为空'
            }), 400

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            access_token = create_access_token(identity=username)
            return jsonify({
                'code': 200,
                'data': {
                    'token': access_token,
                    'user': user.to_dict()
                },
                'message': '登录成功'
            }), 200
        else:
            return jsonify({
                'code': 401,
                'message': '用户名或密码错误'
            }), 401

    except Exception as e:
        print(f"登录错误: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'登录失败: {str(e)}'
        }), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """刷新访问令牌"""
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    return jsonify({'access_token': access_token}), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取用户信息"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    return jsonify({
        'code': 200,
        'data': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        },
        'message': '获取用户信息成功'
    }), 200

@auth_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """获取用户列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        users = User.query.paginate(page=page, per_page=per_page)
        
        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'total': users.total,
            'pages': users.pages,
            'current_page': users.page
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """获取单个用户详情"""
    try:
        user = User.query.get_or_404(user_id)
        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """更新用户信息"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # 更新基本信息
        if 'email' in data:
            user.email = data['email']
        if 'role_id' in data:
            user.role_id = data['role_id']
        if 'is_active' in data:
            user.is_active = data['is_active']
            
        db.session.commit()
        return jsonify(user.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/users/<int:user_id>/password', methods=['PUT'])
@jwt_required()
def change_password(user_id):
    """修改用户密码"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        if not data or 'new_password' not in data:
            return jsonify({'error': 'New password is required'}), 400
            
        # 如果是修改自己的密码，需要验证旧密码
        current_user_id = get_jwt_identity()
        if int(current_user_id) == user_id and (
            'old_password' not in data or 
            not user.check_password(data['old_password'])
        ):
            return jsonify({'error': 'Invalid old password'}), 400
            
        user.password = User.create_password_hash(data['new_password'])
        db.session.commit()
        
        return jsonify({'message': 'Password updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """删除用户"""
    try:
        user = User.query.get_or_404(user_id)
        
        # 不允许删除管理员用户
        if user.role and 'admin' in user.role.permissions:
            return jsonify({'error': 'Cannot delete admin user'}), 403
            
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'User deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/users/<int:user_id>/status', methods=['PUT'])
@jwt_required()
def toggle_user_status(user_id):
    """启用/禁用用户"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        if 'is_active' not in data:
            return jsonify({'error': 'Status is required'}), 400
            
        # 不允许禁用管理员用户
        if user.role and 'admin' in user.role.permissions and not data['is_active']:
            return jsonify({'error': 'Cannot disable admin user'}), 403
            
        user.is_active = data['is_active']
        db.session.commit()
        
        return jsonify({
            'message': f"User {'activated' if data['is_active'] else 'deactivated'} successfully"
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500 
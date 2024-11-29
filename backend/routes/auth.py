from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash
from ..models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
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
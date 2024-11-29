from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required
from flask_cors import cross_origin
from ..models.employee import Employee, EmployeeEducation, EmployeeTraining
from .. import db
from datetime import datetime
import os

employee_bp = Blueprint('employee', __name__)

@employee_bp.route('/list', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_employee_list():
    if request.method == 'OPTIONS':
        # 预检请求处理
        response = jsonify({'code': 200})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response

    try:
        print("收到的请求参数:", request.args)
        print("请求头:", request.headers)
        
        # 获取查询参数
        try:
            page = request.args.get('page', '1')
            page_size = request.args.get('pageSize', '10')
            
            print("页码:", page)
            print("每页条数:", page_size)
            
            try:
                page = int(page)
                page_size = int(page_size)
            except ValueError as e:
                print("参数转换错误:", str(e))
                return jsonify({
                    'code': 422,
                    'message': '页码和每页条数必须为数字'
                }), 422
            
            if page < 1 or page_size < 1:
                print("无效的页码或每页条数:", page, page_size)
                return jsonify({
                    'code': 422,
                    'message': '页码和每页条数必须大于0'
                }), 422
                
        except Exception as e:
            print("参数处理错误:", str(e))
            return jsonify({
                'code': 422,
                'message': '无效的分页参数'
            }), 422
        
        name = request.args.get('name', '').strip()
        department = request.args.get('department', '').strip()
        status = request.args.get('status', '').strip()
        
        print("姓名:", name)
        print("部门:", department)
        print("状态:", status)
        
        # 构建查询
        query = db.session.query(Employee).join(
            Employee.department, isouter=True
        )
        
        # 添加过滤条件
        if name:
            query = query.filter(Employee.name.like(f"%{name}%"))
            print("添加姓名过滤条件:", name)
        
        if department:
            try:
                department_id = int(department)
                query = query.filter(Employee.department_id == department_id)
                print("添加部门过滤条件:", department_id)
            except ValueError:
                print("无效的部门ID:", department)
                return jsonify({
                    'code': 422,
                    'message': '无效的部门ID'
                }), 422
        
        if status:
            valid_status = ['active', 'inactive', 'resigned']
            if status not in valid_status:
                print("无效的状态值:", status)
                return jsonify({
                    'code': 422,
                    'message': '无效的状态值'
                }), 422
            query = query.filter(Employee.status == status)
            print("添加状态过滤条件:", status)
        
        # 获取总记录数
        total = query.count()
        print("总记录数:", total)
        
        # 添加分页
        query = query.order_by(Employee.employee_no)
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        # 执行查询
        employees = query.all()
        print("查询到的员工数:", len(employees))
        
        # 格式化员工数据
        formatted_employees = []
        for emp in employees:
            formatted_emp = {
                'employee_no': emp.employee_no,
                'name': emp.name,
                'gender': emp.gender,
                'birth_date': emp.birth_date.strftime('%Y-%m-%d') if emp.birth_date else None,
                'phone': emp.phone,
                'email': emp.email,
                'id_card': emp.id_card,
                'department': {
                    'id': emp.department.id,
                    'name': emp.department.name
                } if emp.department else None,
                'position': emp.position,
                'entry_date': emp.entry_date.strftime('%Y-%m-%d') if emp.entry_date else None,
                'status': emp.status
            }
            formatted_employees.append(formatted_emp)
        
        response_data = {
            'code': 200,
            'message': 'success',
            'data': {
                'data': formatted_employees,
                'total': total,
                'current_page': page,
                'pages': (total + page_size - 1) // page_size
            }
        }
        
        print("返回数据:", response_data)
        
        response = jsonify(response_data)
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        
        return response
        
    except Exception as e:
        print('获取员工列表失败:', str(e))
        print('错误类型:', type(e).__name__)
        print('错误详情:', str(e))
        import traceback
        print('错误堆栈:', traceback.format_exc())
        return jsonify({
            'code': 500,
            'message': f'获取员工列表失败: {str(e)}'
        }), 500

@employee_bp.route('/detail/<string:employee_no>', methods=['GET', 'PUT', 'OPTIONS'])
@cross_origin(
    origins=["http://localhost:5173"],
    methods=['GET', 'PUT', 'OPTIONS'],
    allow_headers=['Content-Type', 'Authorization'],
    expose_headers=['Content-Range', 'X-Total-Count'],
    supports_credentials=True,
    max_age=600
)
def employee_detail(employee_no):
    """获取或更新员工详情"""
    if request.method == 'OPTIONS':
        response = jsonify({'code': 200})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,OPTIONS')
        return response

    try:
        current_app.logger.info(f"获取员工详情: employee_no={employee_no}")
        employee = Employee.query.filter_by(employee_no=str(employee_no)).first()
        
        if not employee:
            current_app.logger.warning(f"未找到员工: employee_no={employee_no}")
            return jsonify({
                'code': 404,
                'message': f'未找到工号为 {employee_no} 的员工'
            }), 404
        
        if request.method == 'GET':
            # 获取员工的所有相关数据
            employee_data = employee.to_dict()
            current_app.logger.info(f"基础员工数据: {employee_data}")
            
            # 获取教育经历数据
            try:
                education_list = [edu.to_dict() for edu in employee.education.all()]
                current_app.logger.info(f"获取到的教育经历列表: {education_list}")
                employee_data['education'] = education_list
            except Exception as e:
                current_app.logger.error(f"获取教育经历失败: {str(e)}")
                employee_data['education'] = []
            
            # 添加其他数组字段的默认值
            employee_data.update({
                'training': [],
                'work_experience': [],
                'position_changes': [],
                'reward_punishments': [],
                'attachments': []
            })
            
            # 组装合同数据
            if any([
                employee.contract_number,
                employee.contract_type,
                employee.contract_duration,
                employee.contract_start_date,
                employee.contract_end_date,
                employee.contract_sign_date,
                employee.contract_status
            ]):
                employee_data['contract'] = {
                    'number': employee.contract_number,
                    'type': employee.contract_type,
                    'duration': employee.contract_duration,
                    'start_date': employee.contract_start_date.strftime('%Y-%m-%d') if employee.contract_start_date else None,
                    'end_date': employee.contract_end_date.strftime('%Y-%m-%d') if employee.contract_end_date else None,
                    'sign_date': employee.contract_sign_date.strftime('%Y-%m-%d') if employee.contract_sign_date else None,
                    'status': employee.contract_status
                }
            else:
                employee_data['contract'] = None
            
            current_app.logger.info(f"返回的完整员工数据: {employee_data}")
            return jsonify({
                'code': 200,
                'data': employee_data
            }), 200
            
        elif request.method == 'PUT':
            try:
                # 获取请求数据
                data = request.get_json()
                current_app.logger.info(f"收到更新请求: employee_no={employee_no}, data={data}")
                
                if not data:
                    return jsonify({
                        'code': 422,
                        'message': '无效的请求数据',
                        'detail': {
                            'error': 'No data provided'
                        }
                    }), 422

                # 过滤掉不允许更新的字段
                allowed_fields = {
                    'name', 'gender', 'birth_date', 'phone', 'email', 
                    'id_card', 'position', 'entry_date', 'base_salary', 
                    'bank_account', 'bank_name', 'notes', 'status',
                    'department_id', 'contract_number', 'contract_type',
                    'contract_duration', 'contract_start_date', 'contract_end_date',
                    'contract_sign_date', 'contract_status', 'work_experience',
                    'education', 'training', 'position_changes', 'reward_punishments',
                    'attachments'
                }
                
                # 只更新允许的字段，并进行类型换
                update_data = {}
                invalid_fields = []
                for key, value in data.items():
                    if key in allowed_fields:
                        if value is not None:
                            try:
                                if key == 'department_id':
                                    update_data[key] = int(value)
                                elif key in ['birth_date', 'entry_date', 'leave_date', 'contract_start_date', 'contract_end_date', 'contract_sign_date']:
                                    update_data[key] = datetime.strptime(value, '%Y-%m-%d').date()
                                elif key == 'base_salary':
                                    update_data[key] = float(value)
                                elif key == 'contract_duration':
                                    update_data[key] = int(value)
                                elif key in ['work_experience', 'education', 'training', 'position_changes', 'reward_punishments', 'attachments']:
                                    if not isinstance(value, list):
                                        raise ValueError(f'{key} must be a list')
                                    update_data[key] = value
                                else:
                                    update_data[key] = value
                            except (ValueError, TypeError) as e:
                                return jsonify({
                                    'code': 422,
                                    'message': f'字段 {key} 的值类型错误',
                                    'detail': {
                                        'field': key,
                                        'value': value,
                                        'error': str(e)
                                    }
                                }), 422
                    else:
                        invalid_fields.append(key)
                
                current_app.logger.info(f"过滤后的数据: {update_data}")
                if invalid_fields:
                    current_app.logger.warning(f"发现无效字段: {invalid_fields}")
                
                if not update_data:
                    return jsonify({
                        'code': 422,
                        'message': '没有可更新的有效字段',
                        'detail': {
                            'received_fields': list(data.keys()),
                            'allowed_fields': list(allowed_fields),
                            'invalid_fields': invalid_fields
                        }
                    }), 422
                
                # 更新员工信息
                try:
                    for key, value in update_data.items():
                        if key == 'department_id':
                            from ..models.department import Department
                            department = Department.query.get(value)
                            if department:
                                employee.department_id = value
                            else:
                                return jsonify({
                                    'code': 422,
                                    'message': f'部门 ID {value} 不存在',
                                    'detail': {
                                        'field': 'department_id',
                                        'value': value
                                    }
                                }), 422
                        else:
                            setattr(employee, key, value)
                    
                    db.session.commit()
                    current_app.logger.info(f"更新成功: employee_no={employee_no}")
                    
                    return jsonify({
                        'code': 200,
                        'data': employee.to_dict(),
                        'message': '更新成功'
                    }), 200
                    
                except Exception as e:
                    db.session.rollback()
                    current_app.logger.error(f"更新字段失败: {str(e)}")
                    return jsonify({
                        'code': 422,
                        'message': '更新字段失败',
                        'detail': {
                            'error': str(e),
                            'update_data': update_data
                        }
                    }), 422
                
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"更新员工信息失败: {str(e)}")
                return jsonify({
                    'code': 422,
                    'message': '更新员工信息失败',
                    'detail': {
                        'error': str(e),
                        'error_type': type(e).__name__
                    }
                }), 422
            
    except Exception as e:
        current_app.logger.error(f"员工信息操作失败: {str(e)}")
        if request.method == 'PUT':
            db.session.rollback()
        return jsonify({
            'code': 500,
            'message': str(e)
        }), 500

@employee_bp.route('/no/<string:employee_no>', methods=['GET'])
@jwt_required()
@cross_origin()
def get_employee_by_no(employee_no):
    """根据工号获取员工详情（需认证）"""
    try:
        employee = Employee.query.filter_by(employee_no=employee_no).first_or_404()
        return jsonify({
            'code': 200,
            'data': employee.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': str(e)
        }), 500

@employee_bp.route('/detail/<string:employee_no>', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_employee_detail(employee_no):
    """根据工获取员工详情（公开接口）"""
    if request.method == 'OPTIONS':
        response = jsonify({'code': 200})
        return response

    try:
        employee = Employee.query.filter_by(employee_no=str(employee_no)).first()
        
        if not employee:
            return jsonify({
                'code': 404,
                'message': f'未找到工号为 {employee_no} 的员工'
            }), 404
            
        return jsonify({
            'code': 200,
            'data': employee.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取员工详情失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': str(e)
        }), 500

@employee_bp.route('/contract/<string:employee_no>/preview', methods=['GET', 'OPTIONS'])
@cross_origin(
    origins=["http://localhost:5173"],
    methods=['GET', 'OPTIONS'],
    allow_headers=['Content-Type', 'Authorization'],
    expose_headers=['Content-Disposition'],
    supports_credentials=True,
    max_age=600
)
def preview_contract(employee_no):
    """预览员工合同"""
    if request.method == 'OPTIONS':
        response = jsonify({'code': 200})
        return response
        
    try:
        employee = Employee.query.filter_by(employee_no=employee_no).first()
        if not employee:
            return jsonify({
                'code': 404,
                'message': '工不存在'
            }), 404
            
        # 这里应该根据实际情况生成或获取合同文件
        # 示例：假设合同文件存储在 uploads/contracts 目录下
        contract_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'contracts')
        contract_file = os.path.join(contract_dir, f'contract_{employee_no}.pdf')
        
        if not os.path.exists(contract_file):
            return jsonify({
                'code': 404,
                'message': '合同文件不存在'
            }), 404
            
        return send_file(
            contract_file,
            mimetype='application/pdf',
            as_attachment=False,
            download_name=f'contract_{employee_no}.pdf'
        )
        
    except Exception as e:
        current_app.logger.error(f"预览合同失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'预览合同失败: {str(e)}'
        }), 500

@employee_bp.route('/contract/<string:employee_no>/download', methods=['GET', 'OPTIONS'])
@cross_origin(
    origins=["http://localhost:5173"],
    methods=['GET', 'OPTIONS'],
    allow_headers=['Content-Type', 'Authorization'],
    expose_headers=['Content-Disposition'],
    supports_credentials=True,
    max_age=600
)
def download_contract(employee_no):
    """下载员工合同"""
    if request.method == 'OPTIONS':
        response = jsonify({'code': 200})
        return response
        
    try:
        employee = Employee.query.filter_by(employee_no=employee_no).first()
        if not employee:
            return jsonify({
                'code': 404,
                'message': '员工不存在'
            }), 404
            
        # 这里应该根据实际情况获取合同文件
        contract_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'contracts')
        contract_file = os.path.join(contract_dir, f'contract_{employee_no}.pdf')
        
        if not os.path.exists(contract_file):
            return jsonify({
                'code': 404,
                'message': '合同文件不存在'
            }), 404
            
        return send_file(
            contract_file,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'contract_{employee_no}.pdf'
        )
        
    except Exception as e:
        current_app.logger.error(f"下载合同失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'下载合同失败: {str(e)}'
        }), 500

@employee_bp.route('/<string:employee_no>/contract', methods=['POST', 'PUT', 'OPTIONS'])
@cross_origin(
    origins=["http://localhost:5173"],
    methods=['POST', 'PUT', 'OPTIONS'],
    allow_headers=['Content-Type', 'Authorization'],
    expose_headers=['Content-Disposition'],
    supports_credentials=True,
    max_age=600
)
def handle_contract(employee_no):
    """处理员工合同上传"""
    if request.method == 'OPTIONS':
        response = jsonify({'code': 200})
        return response
        
    try:
        employee = Employee.query.filter_by(employee_no=employee_no).first()
        if not employee:
            return jsonify({
                'code': 404,
                'message': '员工不存在'
            }), 404
            
        # 获取表单数据
        print("Form data:", request.form)
        print("Files:", request.files)
        
        contract_file = request.files.get('file')
        contract_data = {
            'number': request.form.get('number'),
            'type': request.form.get('type'),
            'duration': request.form.get('duration'),
            'start_date': request.form.get('start_date'),
            'end_date': request.form.get('end_date'),
            'sign_date': request.form.get('sign_date'),
            'status': request.form.get('status')
        }
        
        print("Contract data:", contract_data)
        
        # 证必填字段
        required_fields = ['number', 'type', 'duration', 'start_date', 'end_date', 'sign_date', 'status']
        missing_fields = [field for field in required_fields if not contract_data.get(field)]
        if missing_fields:
            return jsonify({
                'code': 422,
                'message': '缺少必填字段',
                'detail': {
                    'missing_fields': missing_fields,
                    'received_data': contract_data
                }
            }), 422
            
        # 处合同文件
        if contract_file:
            if contract_file.filename == '':
                return jsonify({
                    'code': 422,
                    'message': '未选择文件'
                }), 422
                
            if not contract_file.filename.lower().endswith('.pdf'):
                return jsonify({
                    'code': 422,
                    'message': '只能上传 PDF 文件'
                }), 422
                
            # 保存合同文件
            filename = f'contract_{employee_no}.pdf'
            contract_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'contracts')
            os.makedirs(contract_dir, exist_ok=True)
            contract_path = os.path.join(contract_dir, filename)
            contract_file.save(contract_path)
            
        try:
            # 更新员工合同信息
            employee.contract_number = contract_data['number']
            employee.contract_type = contract_data['type']
            employee.contract_duration = int(contract_data['duration'])
            employee.contract_start_date = contract_data['start_date']
            employee.contract_end_date = contract_data['end_date']
            employee.contract_sign_date = contract_data['sign_date']
            employee.contract_status = contract_data['status']
            
            db.session.commit()
            
            # 返回更新后的合同信息
            contract_info = {
                'id': employee.id,  # 这里使用员工ID作为合同ID
                'number': employee.contract_number,
                'type': employee.contract_type,
                'duration': employee.contract_duration,
                'start_date': str(employee.contract_start_date),
                'end_date': str(employee.contract_end_date),
                'sign_date': str(employee.contract_sign_date),
                'status': employee.contract_status,
                'file_url': f'/api/employee/contract/{employee_no}/preview'  # 添加文件预览URL
            }
            
            return jsonify({
                'code': 200,
                'message': '合同保存成功',
                'data': contract_info
            })
        except ValueError as e:
            return jsonify({
                'code': 422,
                'message': '数据格式错误',
                'detail': str(e)
            }), 422
            
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"处理合同失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'处理合同失败: {str(e)}'
        }), 500

@employee_bp.route('/<string:employee_no>/education', methods=['GET', 'POST', 'OPTIONS'])
@cross_origin(
    origins=["http://localhost:5173"],
    methods=['GET', 'POST', 'OPTIONS'],
    allow_headers=['Content-Type', 'Authorization'],
    expose_headers=['Content-Range', 'X-Total-Count'],
    supports_credentials=True,
    max_age=600
)
def handle_education(employee_no):
    """处理员工教育经历"""
    if request.method == 'OPTIONS':
        response = jsonify({'code': 200})
        return response
        
    try:
        employee = Employee.query.filter_by(employee_no=employee_no).first()
        if not employee:
            return jsonify({
                'code': 404,
                'message': '员工不存在'
            }), 404
            
        if request.method == 'GET':
            # 获取教育经历列表
            try:
                education_list = [edu.to_dict() for edu in employee.education.all()]
                current_app.logger.debug(f"获取教育经历列表: {education_list}")
                return jsonify({
                    'code': 200,
                    'data': education_list
                })
            except Exception as e:
                current_app.logger.error(f"获取教育经历列表失败: {str(e)}")
                return jsonify({
                    'code': 500,
                    'message': f'获取教育经历列表失败: {str(e)}'
                }), 500
            
        elif request.method == 'POST':
            # 添加教育经历
            data = request.get_json()
            current_app.logger.debug(f"接收到的教育经历数据: {data}")
            
            if not data:
                return jsonify({
                    'code': 422,
                    'message': '无效的请求数据'
                }), 422
                
            # 验证必填字段
            required_fields = ['start_date', 'end_date', 'school', 'major', 'degree']
            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                return jsonify({
                    'code': 422,
                    'message': '缺少必填字段',
                    'detail': {
                        'missing_fields': missing_fields
                    }
                }), 422
                
            try:
                # 创建教育经历记录
                education = EmployeeEducation(
                    employee_no=employee_no,
                    start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
                    end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date(),
                    school=data['school'],
                    major=data['major'],
                    degree=data['degree'],
                    description=data.get('description')
                )
                
                db.session.add(education)
                db.session.commit()
                
                result = education.to_dict()
                current_app.logger.debug(f"添加教育经历成功: {result}")
                return jsonify({
                    'code': 200,
                    'message': '添加教育经历成功',
                    'data': result
                })
                
            except ValueError as e:
                current_app.logger.error(f"数据格式错误: {str(e)}")
                return jsonify({
                    'code': 422,
                    'message': '数据格式错误',
                    'detail': str(e)
                }), 422
                
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"处理教育经历失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'处理教育经历失败: {str(e)}'
        }), 500

@employee_bp.route('/<string:employee_no>/education/<int:education_id>', methods=['PUT', 'DELETE', 'OPTIONS'])
@cross_origin(
    origins=["http://localhost:5173"],
    methods=['PUT', 'DELETE', 'OPTIONS'],
    allow_headers=['Content-Type', 'Authorization'],
    expose_headers=['Content-Range', 'X-Total-Count'],
    supports_credentials=True,
    max_age=600
)
def handle_education_detail(employee_no, education_id):
    """处理单个教育经历"""
    if request.method == 'OPTIONS':
        response = jsonify({'code': 200})
        return response
        
    try:
        education = EmployeeEducation.query.filter_by(
            employee_no=employee_no,
            id=education_id
        ).first()
        
        if not education:
            return jsonify({
                'code': 404,
                'message': '教育经历不存在'
            }), 404
            
        if request.method == 'PUT':
            # 更新教育经历
            data = request.get_json()
            current_app.logger.debug(f"接收到的更新数据: {data}")
            
            if not data:
                return jsonify({
                    'code': 422,
                    'message': '无效的请求数据'
                }), 422
                
            try:
                # 更新字段
                if 'start_date' in data:
                    education.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
                if 'end_date' in data:
                    education.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
                if 'school' in data:
                    education.school = data['school']
                if 'major' in data:
                    education.major = data['major']
                if 'degree' in data:
                    education.degree = data['degree']
                if 'description' in data:
                    education.description = data['description']
                    
                db.session.commit()
                
                result = education.to_dict()
                current_app.logger.debug(f"更新教育经历成功: {result}")
                return jsonify({
                    'code': 200,
                    'message': '更新教育经历成功',
                    'data': result
                })
                
            except ValueError as e:
                current_app.logger.error(f"数据格式错误: {str(e)}")
                return jsonify({
                    'code': 422,
                    'message': '数据格式错误',
                    'detail': str(e)
                }), 422
                
        elif request.method == 'DELETE':
            # 删除教育经历
            try:
                db.session.delete(education)
                db.session.commit()
                current_app.logger.debug(f"删除教育经历成功: id={education_id}")
                
                return jsonify({
                    'code': 200,
                    'message': '删除教育经历成功'
                })
            except Exception as e:
                current_app.logger.error(f"删除教育经历失败: {str(e)}")
                db.session.rollback()
                return jsonify({
                    'code': 500,
                    'message': f'删除教育经历失败: {str(e)}'
                }), 500
            
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"处理教育经历失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'处理教育经历失败: {str(e)}'
        }), 500

@employee_bp.route('/<string:employee_no>/education/debug', methods=['GET'])
@cross_origin()
def debug_education(employee_no):
    """调试教育经历数据"""
    try:
        # 检查员工是否存在
        employee = Employee.query.filter_by(employee_no=employee_no).first()
        if not employee:
            return jsonify({
                'code': 404,
                'message': '员工不存在'
            }), 404

        # 直接从数据库查询教育经历
        education_records = db.session.query(EmployeeEducation).filter_by(
            employee_no=employee_no
        ).all()
        
        # 获取原始数据
        raw_data = [{
            'id': edu.id,
            'employee_no': edu.employee_no,
            'start_date': str(edu.start_date),
            'end_date': str(edu.end_date),
            'school': edu.school,
            'major': edu.major,
            'degree': edu.degree,
            'description': edu.description,
            'created_at': str(edu.created_at),
            'updated_at': str(edu.updated_at)
        } for edu in education_records]
        
        # 获取关系数
        relationship_data = [edu.to_dict() for edu in employee.education.all()]
        
        return jsonify({
            'code': 200,
            'data': {
                'employee': {
                    'id': employee.id,
                    'employee_no': employee.employee_no,
                    'name': employee.name
                },
                'raw_education_data': raw_data,
                'relationship_education_data': relationship_data
            }
        })
    except Exception as e:
        current_app.logger.error(f"调试教育经历数据失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'调试教育经历数据失败: {str(e)}'
        }), 500

@employee_bp.route('/<string:employee_no>/training', methods=['GET', 'POST', 'OPTIONS'])
@cross_origin(
    origins=["http://localhost:5173"],
    methods=['GET', 'POST', 'OPTIONS'],
    allow_headers=['Content-Type', 'Authorization'],
    expose_headers=['Content-Range', 'X-Total-Count'],
    supports_credentials=True,
    max_age=600
)
def handle_training(employee_no):
    """处理员工培训记录"""
    if request.method == 'OPTIONS':
        response = jsonify({'code': 200})
        return response
        
    try:
        employee = Employee.query.filter_by(employee_no=employee_no).first()
        if not employee:
            return jsonify({
                'code': 404,
                'message': '员工不存在'
            }), 404
            
        if request.method == 'GET':
            # 获取培训记录列表
            try:
                training_list = [training.to_dict() for training in employee.training.all()]
                current_app.logger.debug(f"获取培训记录列表: {training_list}")
                return jsonify({
                    'code': 200,
                    'data': training_list
                })
            except Exception as e:
                current_app.logger.error(f"获取培训记录列表失败: {str(e)}")
                return jsonify({
                    'code': 500,
                    'message': f'获取培训记录列表失败: {str(e)}'
                }), 500
            
        elif request.method == 'POST':
            # 添加培训记录
            data = request.get_json()
            current_app.logger.debug(f"接收到的培训记录数据: {data}")
            
            if not data:
                return jsonify({
                    'code': 422,
                    'message': '无效的请求数据'
                }), 422
                
            # 验证必填字段
            required_fields = ['course_name', 'type', 'start_date', 'end_date', 'trainer']
            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                return jsonify({
                    'code': 422,
                    'message': '缺少必填字段',
                    'detail': {
                        'missing_fields': missing_fields
                    }
                }), 422
                
            try:
                # 创建培训记录
                training = EmployeeTraining(
                    employee_no=employee_no,
                    course_name=data['course_name'],
                    type=data['type'],
                    start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
                    end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date(),
                    trainer=data['trainer'],
                    score=data.get('score'),
                    status=data.get('status', 'not_started'),
                    description=data.get('description')
                )
                
                db.session.add(training)
                db.session.commit()
                
                result = training.to_dict()
                current_app.logger.debug(f"添加培训记录成功: {result}")
                return jsonify({
                    'code': 200,
                    'message': '添加培训记录成功',
                    'data': result
                })
                
            except ValueError as e:
                current_app.logger.error(f"数据格式错误: {str(e)}")
                return jsonify({
                    'code': 422,
                    'message': '数据格式错误',
                    'detail': str(e)
                }), 422
                
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"处理培训记录失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'处理培训记录失败: {str(e)}'
        }), 500

@employee_bp.route('/<string:employee_no>/training/<int:training_id>', methods=['PUT', 'DELETE', 'OPTIONS'])
@cross_origin(
    origins=["http://localhost:5173"],
    methods=['PUT', 'DELETE', 'OPTIONS'],
    allow_headers=['Content-Type', 'Authorization'],
    expose_headers=['Content-Range', 'X-Total-Count'],
    supports_credentials=True,
    max_age=600
)
def handle_training_detail(employee_no, training_id):
    """处理单个培训记录"""
    if request.method == 'OPTIONS':
        response = jsonify({'code': 200})
        return response
        
    try:
        training = EmployeeTraining.query.filter_by(
            employee_no=employee_no,
            id=training_id
        ).first()
        
        if not training:
            return jsonify({
                'code': 404,
                'message': '培训记录不存在'
            }), 404
            
        if request.method == 'PUT':
            # 更新培训记录
            data = request.get_json()
            current_app.logger.debug(f"接收到的更新数据: {data}")
            
            if not data:
                return jsonify({
                    'code': 422,
                    'message': '无效的请求数据'
                }), 422
                
            try:
                # 更新字段
                if 'course_name' in data:
                    training.course_name = data['course_name']
                if 'type' in data:
                    training.type = data['type']
                if 'start_date' in data:
                    training.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
                if 'end_date' in data:
                    training.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
                if 'trainer' in data:
                    training.trainer = data['trainer']
                if 'score' in data:
                    training.score = data['score']
                if 'status' in data:
                    training.status = data['status']
                if 'description' in data:
                    training.description = data['description']
                    
                db.session.commit()
                
                result = training.to_dict()
                current_app.logger.debug(f"更新培训记录成功: {result}")
                return jsonify({
                    'code': 200,
                    'message': '更新培训记录成功',
                    'data': result
                })
                
            except ValueError as e:
                current_app.logger.error(f"数据格式错误: {str(e)}")
                return jsonify({
                    'code': 422,
                    'message': '数据格式错误',
                    'detail': str(e)
                }), 422
                
        elif request.method == 'DELETE':
            # 删除培训记录
            try:
                db.session.delete(training)
                db.session.commit()
                current_app.logger.debug(f"删除培训记录成功: id={training_id}")
                
                return jsonify({
                    'code': 200,
                    'message': '删除培训记录成功'
                })
            except Exception as e:
                current_app.logger.error(f"删除培训记录失败: {str(e)}")
                db.session.rollback()
                return jsonify({
                    'code': 500,
                    'message': f'删除培训记录失败: {str(e)}'
                }), 500
            
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"处理培训记录失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'处理培训记录失败: {str(e)}'
        }), 500

# 添加培训记录
@employee_bp.route('/<employee_no>/training', methods=['POST'])
@jwt_required()
def add_training(employee_no):
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['course_name', 'type', 'start_date', 'end_date', 'trainer', 'status']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'code': 400,
                    'message': f'缺少必填字段: {field}'
                }), 400
        
        # 验证日期格式
        try:
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
            if end_date < start_date:
                return jsonify({
                    'code': 400,
                    'message': '结束日期不能早于开始日期'
                }), 400
        except ValueError:
            return jsonify({
                'code': 400,
                'message': '日期格式错误，应为 YYYY-MM-DD'
            }), 400
        
        # 验证状态值
        valid_status = ['not_started', 'in_progress', 'completed']
        if data['status'] not in valid_status:
            return jsonify({
                'code': 400,
                'message': '无效的状态值'
            }), 400
        
        # 插入数据
        with db.cursor() as cursor:
            sql = """
                INSERT INTO employee_training (
                    employee_no, course_name, type, start_date, end_date,
                    trainer, score, status, description
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            cursor.execute(sql, (
                employee_no,
                data['course_name'],
                data['type'],
                data['start_date'],
                data['end_date'],
                data['trainer'],
                data.get('score'),
                data['status'],
                data.get('description')
            ))
            training_id = cursor.lastrowid
        
        db.commit()
        
        # 返回新创建的培训记录
        with db.cursor() as cursor:
            sql = "SELECT * FROM employee_training WHERE id = %s"
            cursor.execute(sql, (training_id,))
            training = cursor.fetchone()
        
        return jsonify({
            'code': 200,
            'message': '添加培训记录成功',
            'data': format_training(training)
        })
        
    except Exception as e:
        db.rollback()
        print('添加培训记录失败:', str(e))
        return jsonify({
            'code': 500,
            'message': '添加培训记录失败'
        }), 500

# 更新培训记录
@employee_bp.route('/<employee_no>/training/<int:training_id>', methods=['PUT'])
@jwt_required()
def update_training(employee_no, training_id):
    try:
        data = request.get_json()
        
        # 验证培训记录是否存在
        with db.cursor() as cursor:
            sql = """
                SELECT * FROM employee_training 
                WHERE id = %s AND employee_no = %s
            """
            cursor.execute(sql, (training_id, employee_no))
            training = cursor.fetchone()
            
            if not training:
                return jsonify({
                    'code': 404,
                    'message': '培训记录不存'
                }), 404
        
        # 验证日期格式
        if 'start_date' in data or 'end_date' in data:
            try:
                start_date = datetime.strptime(
                    data.get('start_date', training['start_date']), 
                    '%Y-%m-%d'
                )
                end_date = datetime.strptime(
                    data.get('end_date', training['end_date']), 
                    '%Y-%m-%d'
                )
                if end_date < start_date:
                    return jsonify({
                        'code': 400,
                        'message': '结束日期不能早于开始日期'
                    }), 400
            except ValueError:
                return jsonify({
                    'code': 400,
                    'message': '日期格式错误，应为 YYYY-MM-DD'
                }), 400
        
        # 验证状态值
        if 'status' in data:
            valid_status = ['not_started', 'in_progress', 'completed']
            if data['status'] not in valid_status:
                return jsonify({
                    'code': 400,
                    'message': '无效的状态值'
                }), 400
        
        # 更新数据
        update_fields = []
        params = []
        for field in ['course_name', 'type', 'start_date', 'end_date', 
                     'trainer', 'score', 'status', 'description']:
            if field in data:
                update_fields.append(f"{field} = %s")
                params.append(data[field])
        
        if update_fields:
            with db.cursor() as cursor:
                sql = f"""
                    UPDATE employee_training 
                    SET {', '.join(update_fields)}
                    WHERE id = %s AND employee_no = %s
                """
                params.extend([training_id, employee_no])
                cursor.execute(sql, params)
            
            db.commit()
            
            # 返回更新后的培训记录
            with db.cursor() as cursor:
                sql = "SELECT * FROM employee_training WHERE id = %s"
                cursor.execute(sql, (training_id,))
                updated_training = cursor.fetchone()
            
            return jsonify({
                'code': 200,
                'message': '更新培训记录成功',
                'data': format_training(updated_training)
            })
        else:
            return jsonify({
                'code': 400,
                'message': '没有提供要更新的字段'
            }), 400
            
    except Exception as e:
        db.rollback()
        print('更新培训记录失败:', str(e))
        return jsonify({
            'code': 500,
            'message': '更新培训记录失败'
        }), 500

# 删除培训记录
@employee_bp.route('/<employee_no>/training/<int:training_id>', methods=['DELETE'])
@jwt_required()
def delete_training(employee_no, training_id):
    try:
        # 验证培训记录是否存在
        with db.cursor() as cursor:
            sql = """
                SELECT * FROM employee_training 
                WHERE id = %s AND employee_no = %s
            """
            cursor.execute(sql, (training_id, employee_no))
            if not cursor.fetchone():
                return jsonify({
                    'code': 404,
                    'message': '培训记录不存在'
                }), 404
            
            # 删除培训记录
            sql = """
                DELETE FROM employee_training 
                WHERE id = %s AND employee_no = %s
            """
            cursor.execute(sql, (training_id, employee_no))
        
        db.commit()
        
        return jsonify({
            'code': 200,
            'message': '删除培训记录成功'
        })
        
    except Exception as e:
        db.rollback()
        print('删除培训记录失败:', str(e))
        return jsonify({
            'code': 500,
            'message': '删除培训记录失败'
        }), 500

# 格式化培训记录
def format_training(training):
    if not training:
        return None
    
    return {
        'id': training['id'],
        'course_name': training['course_name'],
        'type': training['type'],
        'start_date': training['start_date'].strftime('%Y-%m-%d'),
        'end_date': training['end_date'].strftime('%Y-%m-%d'),
        'trainer': training['trainer'],
        'score': training['score'],
        'status': training['status'],
        'description': training['description']
    }
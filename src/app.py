from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
app = Flask(__name__)
token = '123456'
conn = mysql.connector.connect(
    host="localhost", 
    user="datapool",
    password="91OBBlRmTCSU5XcUs3VCjFgF7QrCibU1",
    database="campusresourcerms",
    autocommit=False
)
CORS(app)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/login", methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    cursor = conn.cursor()
    query = "SELECT * FROM User WHERE username = %s AND password = %s"
    cursor.execute(query, (username, password))
    
    user = cursor.fetchone()
    
    if user:
        # 用户存在; 返回 json { "status": "success", "user": user }
        user_data = {
            "id": user[0],
            "username": user[1],
            "role_id": user[4],
            "student_id": user[5],
            "teacher_id": user[6],
        }
        response = jsonify({"status": "success", "user": user_data})
        response.headers['Authorization'] = 'Bearer ' + token
        return response
    else:
        # 用户不存在; 返回 json { "status": "error", "message": "用户名或密码错误" }
        return jsonify({"status": "error", "message": "用户名或密码错误"})

@app.route("/get-all-locations", methods=['GET'])
def get_all_locations():
    # 查询所有不重复的地点信息
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT location FROM Resource")
    locations = [row[0] for row in cursor.fetchall()]

    # 构建返回的 JSON 数据
    response = {
        "status": "success",
        "locations": locations
    }

    # 将结果转换为 JSON 格式并返回
    return jsonify(response)

@app.route("/get-all-resource-types", methods=['GET'])
def get_all_resource_types():
    # 查询所有不重复的资源类型信息
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT type_name FROM resourcetype")
    resource_types = [row[0] for row in cursor.fetchall()]
    # 构建返回的 JSON 数据
    response = {
        "status": "success",
        "resource_types": resource_types
    }
    return jsonify(response)

@app.route("/get-all-resources-capacity", methods=['GET'])
def get_all_res_caps():
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT capacity FROM resource")
    caps = [row[0] for row in cursor.fetchall()]
    response = {
        "status": "success",
        "caps": caps
    }
    return jsonify(response)

@app.route("/search", methods=['GET'])
def search():
    name = request.args.get('name')
    location = request.args.get('location')
    capacity = request.args.get('capacity')
    type_name = request.args.get('type')

    cursor = conn.cursor()

    # 构建查询语句
    query = "SELECT r.resource_id, r.name, r.description, r.location, r.capacity, r.status, rt.type_name " \
            "FROM resource r " \
            "JOIN resourcetype rt ON r.type_id = rt.type_id " \
            "WHERE r.name LIKE %s AND r.location = %s AND r.capacity = %s AND rt.type_name = %s"

    # 执行查询
    cursor.execute(query, ('%' + name + '%', location, capacity, type_name))
    resources = cursor.fetchall()

    # 构建返回的 JSON 数据
    response = {
        "status": "success",
        "resources": []
    }

    for resource in resources:
        resource_data = {
            "resource_id": resource[0],
            "name": resource[1],
            "description": resource[2],
            "location": resource[3],
            "capacity": resource[4],
            "status": resource[5],
            "type_name": resource[6]
        }
        response["resources"].append(resource_data)

    return jsonify(response)


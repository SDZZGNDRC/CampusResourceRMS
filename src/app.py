from flask import Flask, jsonify, request
from datetime import datetime
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

@app.route("/get-all-resources-capacities", methods=['GET'])
def get_all_res_caps():
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT capacity FROM resource")
    caps = sorted([row[0] for row in cursor.fetchall()])
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
    start_date: str = request.args.get('start_date') # str; maybe null or empty; ISO 8601 格式
    end_date: str = request.args.get('end_date') # str; maybe null or empty; ISO 8601 格式

    cursor = conn.cursor()

    # 构建查询语句
    query = "SELECT r.resource_id, r.name, r.description, r.location, r.capacity, r.status, rt.type_name " \
            "FROM resource r " \
            "JOIN resourcetype rt ON r.type_id = rt.type_id"
    
    filters = []
    params = []
    if name:
        filters.append("r.name LIKE %s")
        params.append('%' + name + '%')
    if location:
        filters.append("r.location = %s")
        params.append(location)
    if type_name:
        filters.append("rt.type_name = %s")
        params.append(type_name)

    if capacity:
        filters.append("r.capacity >= %s")
        params.append(capacity)

    # 如果`start_date`和`end_date`不为空，则添加时间范围条件: 在`reservation`表中查询`start_date`和`end_date`之间的记录并过滤掉
    if start_date and end_date:
        start_datetime = datetime.fromisoformat(start_date)
        end_datetime = datetime.fromisoformat(end_date)
        filters.append("""
            r.resource_id NOT IN (
                SELECT resource_id
                FROM reservation
                WHERE (start_time <= %s AND end_time >= %s)
                OR (start_time <= %s AND end_time >= %s)
            )
        """)
        params.extend([end_datetime, start_datetime, start_datetime, end_datetime])
    
    if filters:
        query += " WHERE " + " AND ".join(filters)

    # 执行查询
    cursor.execute(query, params)
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

@app.route("/reserve", methods=['POST'])
def reserve():
    # 获取POST请求的JSON数据
    data = request.json
    resource_id = data.get('resource_id')
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    description = data.get('description')
    public = data.get('public')
    user_id = data.get('user_id') 

    # 检查`start_time`和`end_time`; 并转换为datetime对象
    if not start_time or not end_time:
        return jsonify({"status": "error", "message": "start_time和end_time不能为空"})
    try:
        start_time = datetime.fromisoformat(start_time)
        end_time = datetime.fromisoformat(end_time)
    except ValueError:
        return jsonify({"status": "error", "message": "start_time和end_time格式不正确"})

    # 检查`description`
    if not description:
        return jsonify({"status": "error", "message": "description不能为空"})

    # 设置status为“审核中”
    status = "审核中"

    cursor = conn.cursor()

    # 查询当前最大的reservation_id
    cursor.execute("SELECT MAX(reservation_id) FROM Reservation")
    max_reservation_id = cursor.fetchone()[0]

    if max_reservation_id is None:
        new_reservation_id = 1
    else:
        new_reservation_id = max_reservation_id + 1

    # 插入预约记录
    insert_query = "INSERT INTO reservation (reservation_id, start_time, end_time, resource_id, status, description, public) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(insert_query, (new_reservation_id, start_time, end_time, resource_id, status, description, public))

    # 插入usage_record表
    cursor.execute("SELECT MAX(record_id) FROM UsageRecord")
    max_record_id = cursor.fetchone()[0]
    if max_record_id is None:
        new_record_id = 1
    else:
        new_record_id = max_record_id + 1
    insert_usage_record_query = "INSERT INTO UsageRecord (record_id, user_id, reservation_id) VALUES (%s, %s, %s)"
    cursor.execute(insert_usage_record_query, (new_record_id, user_id, new_reservation_id))

    # 提交事务
    conn.commit()

    response = {
        "status": "success",
        "message": "预约记录插入成功"
    }

    return jsonify(response)

@app.route("/get-my-reservations", methods=['GET'])
def get_my_reservations():
    user_id = request.args.get('userID')

    # 检查`user_id`
    if not user_id:
        return jsonify({"status": "error", "message": "userID不能为空"})

    cursor = conn.cursor()
    
    # 查询该用户的预约记录
    query = "SELECT r.reservation_id, r.start_time, r.end_time, r.resource_id, r.status, r.description, r.public " \
            "FROM reservation r " \
            "JOIN usageRecord ur ON r.reservation_id = ur.reservation_id " \
            "WHERE ur.user_id = %s"
    
    cursor.execute(query, (user_id,))
    reservations = cursor.fetchall()

    response = {
        "status": "success",
        "reservations": []
    }

    # 查询资源名称
    resource_query = "SELECT name FROM Resource WHERE resource_id = %s"
    for reservation in reservations:
        cursor.execute(resource_query, (reservation[3],))  # reservation[3] 是 resource_id
        resource_name = cursor.fetchone()[0]  # 获取资源名称

        start_time_str = reservation[1].strftime('%Y-%m-%d %H:%M')  # 将开始时间转化为`YY-MM-DD-HH:mm`的格式
        end_time_str = reservation[2].strftime('%Y-%m-%d %H:%M')  # 将结束时间转化为`YY-MM-DD-HH:mm`的格式

        reservation_data = {
            "reservation_id": reservation[0],
            "start_time": start_time_str,
            "end_time": end_time_str,
            "resource_name": resource_name,  # 将资源名称添加到返回数据中
            "status": reservation[4],
            "description": reservation[5],
            "public": '是' if reservation[6] else '否'
        }
        response["reservations"].append(reservation_data)
    return jsonify(response)

@app.route("/get-recent-reservations", methods=['GET'])
def get_recent_reservations():
    start_time = request.args.get('start_time')
    if start_time:
        start_datetime = datetime.fromisoformat(start_time)
    else:
        start_datetime = None

    cursor = conn.cursor()

    if start_datetime:
        query = """
            SELECT r.reservation_id, r.start_time, r.end_time, r.description, u.username, res.name
            FROM Reservation r
            JOIN UsageRecord ur ON r.reservation_id = ur.reservation_id
            JOIN Resource res ON r.resource_id = res.resource_id
            JOIN User u ON ur.user_id = u.user_id
            WHERE r.end_time > %s AND r.status = '审核通过' AND r.public = 1
        """
        cursor.execute(query, (start_datetime,))
    else:
        query = """
            SELECT r.reservation_id, r.start_time, r.end_time, r.description, u.username, res.name
            FROM Reservation r
            JOIN UsageRecord ur ON r.reservation_id = ur.reservation_id
            JOIN Resource res ON r.resource_id = res.resource_id
            JOIN User u ON ur.user_id = u.user_id
            WHERE r.status = '审核通过' AND r.public = 1
        """
        cursor.execute(query)

    reservations = cursor.fetchall()

    response = {
        "status": "success",
        "reservations": []
    }

    for reservation in reservations:
        start_time_str = reservation[1].strftime('%Y-%m-%d %H:%M')
        end_time_str = reservation[2].strftime('%Y-%m-%d %H:%M')

        reservation_data = {
            "reservation_id": reservation[0],
            "start_time": start_time_str,
            "end_time": end_time_str,
            "description": reservation[3],
            "user_name": reservation[4],
            "resource_name": reservation[5]
        }
        response["reservations"].append(reservation_data)
    print(f'recent activities: {response["reservations"]}')
    return jsonify(response)




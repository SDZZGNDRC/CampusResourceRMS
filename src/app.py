from typing import List
from flask import Flask, jsonify, request
from datetime import timedelta
import json
from dateutil.parser import parse
import threading
from flask_cors import CORS
import mysql.connector

config = {}
with open('../config.json', 'r') as file:
    config = json.load(file)


app = Flask(__name__)
token = config['token']
conn = mysql.connector.connect(
    host=config['db']['host'], 
    user=config['db']['user'],
    password=config['db']['password'],
    database=config['db']['database'],
    autocommit=False
)
CORS(app)


# 在全局范围内创建一个互斥锁对象
mutex = threading.Lock()

def get_cursor():
    global conn
    try:
        # 尝试获取游标
        cursor = conn.cursor()
        
        # 如果连接有效，直接返回游标
        return cursor
    except mysql.connector.errors.OperationalError as e:
        # 如果连接断开，重新连接数据库并返回新的游标
        conn.reconnect()
        cursor = get_cursor()
        return cursor

@app.route("/login", methods=['POST'])
def login():
    global mutex
    username = request.form['username']
    password = request.form['password']
    mutex.acquire()
    cursor = get_cursor()
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
    else:
        # 用户不存在; 返回 json { "status": "error", "message": "用户名或密码错误" }
        response = jsonify({"status": "error", "message": "用户名或密码错误"})
    mutex.release()
    return response

@app.route("/get-all-roles", methods=['GET'])
def get_all_roles():
    global mutex
    mutex.acquire()
    cursor = get_cursor()

    query = "SELECT role_id, role_name, description FROM Role"
    cursor.execute(query)
    roles = cursor.fetchall()

    response = {
        "status": "success",
        "roles": []
    }

    for role in roles:
        role_data = {
            "role_id": role[0],
            "role_name": role[1],
            "description": role[2]
        }
        response["roles"].append(role_data)
    mutex.release()
    return jsonify(response)

@app.route("/get-all-users", methods=['GET'])
def get_all_users():
    global mutex
    mutex.acquire()
    cursor = get_cursor()

    query = """
        SELECT u.user_id, u.username, u.password, u.role_id, r.role_name, u.email
        FROM User u
        JOIN Role r ON u.role_id = r.role_id
    """
    cursor.execute(query)
    users = cursor.fetchall()

    response = {
        "status": "success",
        "users": []
    }

    for user in users:
        user_data = {
            "user_id": user[0],
            "username": user[1],
            "password": user[2],
            "role_id": user[3],
            # "role_name": user[4],
            "email": user[5]
        }
        response["users"].append(user_data)
    mutex.release()
    return jsonify(response)

@app.route("/add-user", methods=['POST'])
def add_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role_id = data.get('role_id')
    email = data.get('email')
    global mutex
    mutex.acquire()
    cursor = get_cursor()
    
    # 获取下一个可用的user_id
    cursor.execute("SELECT MAX(user_id) FROM User")
    max_id = cursor.fetchone()[0]
    new_user_id = max_id + 1 if max_id is not None else 1

    insert_query = "INSERT INTO User (user_id, username, password, email, role_id) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(insert_query, (new_user_id, username, password, email, role_id))

    conn.commit()

    response = {
        "status": "success",
        "message": "用户添加成功"
    }
    mutex.release()
    return jsonify(response)


@app.route("/update-user", methods=['POST'])
def update_user():
    global mutex
    mutex.acquire()
    data = request.json
    user_id = data.get('user_id')
    username = data.get('username')
    password = data.get('password')
    role_id = data.get('role_id')
    email = data.get('email')

    cursor = get_cursor()

    update_query = "UPDATE User SET username = %s, password = %s, email = %s, role_id = %s WHERE user_id = %s"
    cursor.execute(update_query, (username, password, email, role_id, user_id))

    conn.commit()

    response = {
        "status": "success",
        "message": "用户信息更新成功"
    }
    mutex.release()
    return jsonify(response)

@app.route("/delete-user", methods=['POST'])
def delete_user():
    data = request.json
    user_id = data.get('user_id')
    global mutex
    mutex.acquire()
    
    cursor = get_cursor()

    delete_query = "DELETE FROM User WHERE user_id = %s"
    cursor.execute(delete_query, (user_id,))

    conn.commit()

    response = {
        "status": "success",
        "message": "用户删除成功"
    }
    mutex.release()
    return jsonify(response)

@app.route("/get-all-locations", methods=['GET'])
def get_all_locations():
    global mutex
    mutex.acquire()
    # 查询所有不重复的地点信息
    cursor = get_cursor()
    cursor.execute("SELECT DISTINCT location FROM Resource")
    locations = [row[0] for row in cursor.fetchall()]

    # 构建返回的 JSON 数据
    response = {
        "status": "success",
        "locations": locations
    }

    # 将结果转换为 JSON 格式并返回
    mutex.release()
    return jsonify(response)

@app.route("/get-all-resource-types", methods=['GET'])
def get_all_resource_types():
    # 查询所有的资源类型信息
    global mutex
    mutex.acquire()
    cursor = get_cursor()
    cursor.execute("SELECT * FROM resourcetype")
    resource_types = []
    for row in cursor.fetchall():
        resource_types.append({
            'type_id': row[0],
            'type_name': row[1],
            'description': row[2],
        })
    # 构建返回的 JSON 数据
    response = {
        "status": "success",
        "resource_types": resource_types
    }
    mutex.release()
    return jsonify(response)

@app.route("/get-all-resources-capacities", methods=['GET'])
def get_all_res_caps():
    global mutex
    mutex.acquire()
    cursor = get_cursor()
    cursor.execute("SELECT DISTINCT capacity FROM resource")
    caps = sorted([row[0] for row in cursor.fetchall()])
    response = {
        "status": "success",
        "caps": caps
    }
    mutex.release()
    return jsonify(response)

@app.route("/search", methods=['GET'])
def search():
    global mutex
    mutex.acquire()
    name = request.args.get('name')
    location = request.args.get('location')
    capacity = request.args.get('capacity')
    type_id = request.args.get('type')
    
    cursor = get_cursor()

    # 构建查询语句
    query = "SELECT r.resource_id, r.name, r.description, r.location, r.capacity, r.status, rt.type_id " \
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
    if type_id:
        filters.append("rt.type_id = %s")
        params.append(type_id)

    if capacity:
        filters.append("r.capacity >= %s")
        params.append(capacity)

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
            "type_id": resource[6]
        }
        response["resources"].append(resource_data)
    mutex.release()
    return jsonify(response)

@app.route("/statistics", methods=['GET'])
def statistics():
    global mutex
    mutex.acquire()
    name = request.args.get('name')
    location = request.args.get('location')
    capacity = request.args.get('capacity')
    type_id = request.args.get('type')
    start_date: str = request.args.get('start_date')  # str; maybe null or empty; ISO 8601 格式
    end_date: str = request.args.get('end_date')  # str; maybe null or empty; ISO 8601 格式

    cursor = get_cursor()

    # 构建查询语句
    query = "SELECT r.resource_id, r.name, r.description, r.location, r.capacity, r.status, rt.type_id, " \
            "COALESCE(SUM(CASE WHEN res.status IN ('审核通过', '已完成') THEN 1 ELSE 0 END), 0) AS count, " \
            "COALESCE(SUM(CASE WHEN res.status IN ('审核通过', '已完成') THEN TIMESTAMPDIFF(MINUTE, ur.start_time, ur.end_time) ELSE 0 END), 0) AS duration " \
            "FROM resource r " \
            "JOIN resourcetype rt ON r.type_id = rt.type_id " \
            "LEFT JOIN reservation res ON r.resource_id = res.resource_id " \
            "LEFT JOIN usagerecord ur ON res.reservation_id = ur.reservation_id"

    filters = []
    params = []
    if name:
        filters.append("r.name LIKE %s")
        params.append('%' + name + '%')
    if location:
        filters.append("r.location = %s")
        params.append(location)
    if type_id:
        filters.append("rt.type_id = %s")
        params.append(type_id)
    if capacity:
        filters.append("r.capacity >= %s")
        params.append(capacity)
    if start_date and end_date:
        filters.append("res.start_time >= %s AND res.end_time <= %s")
        params.extend([start_date, end_date])

    if filters:
        query += " WHERE " + " AND ".join(filters)

    query += " GROUP BY r.resource_id"

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
            "type_id": resource[6],
            "count": resource[7],  # 预约次数
            "duration": resource[8]  # 总时长
        }
        response["resources"].append(resource_data)
    mutex.release()
    return jsonify(response)


@app.route("/add-resource", methods=['POST'])
def add_resource():
    global mutex
    mutex.acquire()
    name = request.json.get('name')
    description = request.json.get('description')
    location = request.json.get('location')
    capacity = request.json.get('capacity')
    type_id = request.json.get('type_id')

    cursor = get_cursor()

    # 查询当前最大的resource_id
    cursor.execute("SELECT MAX(resource_id) FROM Resource")
    result = cursor.fetchone()
    max_resource_id = result[0] if result[0] else 0
    next_resource_id = max_resource_id + 1

    insert_query = "INSERT INTO Resource (resource_id, name, description, location, capacity, status, type_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(insert_query, (next_resource_id, name, description, location, capacity, 'available', type_id))

    conn.commit()

    response = {
        "status": "success",
        "message": "资源添加成功"
    }
    mutex.release()
    return jsonify(response)


@app.route("/delete-resource", methods=['POST'])
def delete_resource():
    global mutex
    mutex.acquire()
    resource_id = request.json.get('resource_id')

    cursor = get_cursor()

    delete_query = "DELETE FROM Resource WHERE resource_id = %s"
    cursor.execute(delete_query, (resource_id,))

    conn.commit()

    response = {
        "status": "success",
        "message": "资源删除成功"
    }
    mutex.release()
    return jsonify(response)

@app.route("/update-resource", methods=['POST'])
def update_resource():
    global mutex
    mutex.acquire()
    resource_id = request.json.get('resource_id')
    name = request.json.get('name')
    description = request.json.get('description')
    location = request.json.get('location')
    capacity = request.json.get('capacity')
    type_id = request.json.get('type_id')

    cursor = get_cursor()

    update_query = "UPDATE Resource SET name = %s, description = %s, location = %s, capacity = %s, type_id = %s WHERE resource_id = %s"
    cursor.execute(update_query, (name, description, location, capacity, type_id, resource_id))

    conn.commit()

    response = {
        "status": "success",
        "message": "资源信息更新成功"
    }
    mutex.release()
    return jsonify(response)

@app.route("/reserve", methods=['POST'])
def reserve():
    # 获取POST请求的JSON数据
    global mutex
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
        start_time = parse(start_time)
        end_time = parse(end_time)
    except ValueError:
        return jsonify({"status": "error", "message": "start_time和end_time格式不正确"})

    # 检查`description`
    if not description:
        return jsonify({"status": "error", "message": "description不能为空"})

    # 设置status为“审核中”
    status = "审核中"
    mutex.acquire()
    cursor = get_cursor()

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
    insert_usage_record_query = "INSERT INTO UsageRecord (record_id, user_id, reservation_id, `primary`, start_time, end_time) VALUES (%s, %s, %s, %s, %s, %s)"
    cursor.execute(insert_usage_record_query, (new_record_id, user_id, new_reservation_id, 1, start_time, end_time))

    # 提交事务
    conn.commit()

    response = {
        "status": "success",
        "message": "预约记录插入成功"
    }
    mutex.release()
    return jsonify(response)

@app.route("/cancel-reserve", methods=['GET'])
def cancel_reserve():
    global mutex
    reservation_id = request.args.get('reservation_id')
    user_id = request.args.get('userID')
    print(type(reservation_id))
    print(reservation_id)
    print(type(user_id))
    print(user_id)
    if not (user_id and reservation_id):
        return jsonify({"status": "error", "message": "userID和reservationID均不能为空"})
    mutex.acquire()
    cursor = get_cursor()

    # 删除`usageRecord`表中的记录
    delete_usage_record_query = "DELETE FROM UsageRecord WHERE user_id = %s AND reservation_id = %s"
    cursor.execute(delete_usage_record_query, (user_id, reservation_id))

    # 删除`reservation`表中的记录
    delete_reservation_query = "DELETE FROM Reservation WHERE reservation_id = %s"
    cursor.execute(delete_reservation_query, (reservation_id,))

    # 提交事务
    conn.commit()

    response = {
        "status": "success",
        "message": "预约记录删除成功"
    }
    mutex.release()
    return jsonify(response)

@app.route("/is-reserved", methods=['GET'])
def is_reserved():
    global mutex
    resource_id = request.args.get('resource_id')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    
    if not (resource_id and start_time and end_time):
        return jsonify({"status": "error", "message": "resource_id, start_time和end_time均不能为空"})
    
    start_time = parse(start_time)
    end_time = parse(end_time)
    
    mutex.acquire()
    cursor = get_cursor()
    
    query = "SELECT reservation_id FROM Reservation WHERE resource_id = %s AND ((start_time <= %s AND end_time >= %s) OR (start_time <= %s AND end_time >= %s))"
    cursor.execute(query, (resource_id, end_time, end_time, start_time, start_time))
    conflicting_reservations = [row[0] for row in cursor.fetchall()]
    
    mutex.release()
    
    if conflicting_reservations:
        return jsonify({"status": "reserved", "conflicting_reservation_ids": conflicting_reservations})
    else:
        return jsonify({"status": "not_reserved"})

@app.route("/is-conflict", methods=['GET'])
def is_conflict():
    global mutex
    reservation_id = request.args.get('reservation_id')
    
    if not reservation_id:
        return jsonify({"status": "error", "message": "reservation_id不能为空"})
    
    mutex.acquire()
    cursor = get_cursor()
    
    # 获取提供的预约信息
    cursor.execute("SELECT resource_id, start_time, end_time FROM Reservation WHERE reservation_id = %s", (reservation_id,))
    current_reservation = cursor.fetchone()
    
    if not current_reservation:
        mutex.release()
        return jsonify({"status": "error", "message": "未找到提供的预约记录"})
    
    resource_id = current_reservation[0]
    start_time = current_reservation[1]
    end_time = current_reservation[2]
    
    # 检查是否存在重叠的预约,排除当前预约自身
    query = "SELECT reservation_id FROM Reservation WHERE resource_id = %s AND reservation_id != %s AND ((start_time <= %s AND end_time >= %s) OR (start_time <= %s AND end_time >= %s))"
    cursor.execute(query, (resource_id, reservation_id, end_time, end_time, start_time, start_time))
    conflicting_reservations = [row[0] for row in cursor.fetchall()]
    
    mutex.release()
    
    if conflicting_reservations:
        return jsonify({"status": "conflict", "conflicting_reservation_ids": conflicting_reservations})
    else:
        return jsonify({"status": "no_conflict", "conflicting_reservation_ids": []})


@app.route("/get-my-reservations", methods=['GET'])
def get_my_reservations():
    global mutex
    user_id = request.args.get('userID')
    mutex.acquire()
    cursor = get_cursor()
    if user_id:
        # 查询该用户的预约记录
        query = "SELECT r.reservation_id, r.start_time, r.end_time, r.resource_id, r.status, r.description, r.public, u.username  " \
                "FROM reservation r " \
                "JOIN usageRecord ur ON r.reservation_id = ur.reservation_id " \
                "JOIN User u ON ur.user_id = u.user_id " \
                "WHERE ur.user_id = %s"
        cursor.execute(query, (user_id,))
    else:
        query = "SELECT r.reservation_id, r.start_time, r.end_time, r.resource_id, r.status, r.description, r.public, u.username " \
                "FROM reservation r " \
                "JOIN usageRecord ur ON r.reservation_id = ur.reservation_id " \
                "JOIN User u ON ur.user_id = u.user_id"
        cursor.execute(query)

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

        # 查询与当前预约冲突的预约ID
        query_conflicts = "SELECT reservation_id FROM Reservation WHERE resource_id = %s AND reservation_id != %s AND ((start_time <= %s AND end_time >= %s) OR (start_time <= %s AND end_time >= %s))"
        cursor.execute(query_conflicts, (reservation[3], reservation[0], reservation[2], reservation[2], reservation[1], reservation[1]))
        conflict_ids = [row[0] for row in cursor.fetchall()]  # 存储冲突的预约ID列表

        # 新增一个`conflict_ids`字段，存储和当前预约冲突的所有预约ID
        reservation_data = {
            "reservation_id": reservation[0],
            "start_time": start_time_str,
            "end_time": end_time_str,
            "resource_name": resource_name,  # 将资源名称添加到返回数据中
            "username": reservation[7],
            "status": reservation[4],
            "description": reservation[5],
            "public": '是' if reservation[6] else '否',
            "conflict_ids": conflict_ids  # 冲突的预约ID列表
        }
        response["reservations"].append(reservation_data)
    mutex.release()
    return jsonify(response)

@app.route("/get-recent-reservations", methods=['GET'])
def get_recent_reservations():
    global mutex
    start_time = request.args.get('start_time')
    if start_time:
        start_datetime = parse(start_time)
    else:
        start_datetime = None
    mutex.acquire()
    cursor = get_cursor()

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
    mutex.release()
    return jsonify(response)

@app.route("/update-conflicting-reservations", methods=['POST'])
def update_conflicting_reservations():
    global mutex
    data = request.json
    reservation_ids = data.get('reservation_ids')
    status = data.get('status')
    mutex.acquire()
    cursor = get_cursor()

    # 构建逗号分隔的预约ID字符串
    reservation_ids_str = ','.join(map(str, reservation_ids))

    # 更新冲突的预约记录的状态
    update_query = f"UPDATE Reservation SET status = '{status}' WHERE reservation_id IN ({reservation_ids_str})"
    cursor.execute(update_query)

    conn.commit()

    response = {
        "status": "success",
        "message": "冲突预约记录状态更新成功"
    }
    mutex.release()
    return jsonify(response)


@app.route("/update-reservation", methods=['POST'])
def update_reservation():
    global mutex
    data = request.json
    reservation_id = data.get('reservation_id')
    status = data.get('status')
    mutex.acquire()
    cursor = get_cursor()

    # 更新预约记录的状态
    update_query = "UPDATE Reservation SET status = %s WHERE reservation_id = %s"
    cursor.execute(update_query, (status, reservation_id))

    conn.commit()

    response = {
        "status": "success",
        "message": "预约记录状态更新成功"
    }
    mutex.release()
    return jsonify(response)



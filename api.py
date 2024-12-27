from flask import Flask, jsonify, request
import pymssql
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

try:
    conn = pymssql.connect(server=os.getenv("SECRET_SERVER"), user='', password='', database='GingerView')
    cursor = conn.cursor()
    print("Connection successful!")
except pymssql.Error as e:
    print("Error while connecting to MSSQL:", e)
finally:
    if 'conn' in locals() and conn:
        conn.close()
        print("Connection closed.")

conn = pymssql.connect(server=os.getenv("SECRET_SERVER"), user='', password='', database='GingerView')


@app.route('/users', methods=['GET'])
def get_Users():
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, useremail, userid, isActive FROM users")
        rows = cursor.fetchall()
        data = [
            {column[0]: value for column,
                value in zip(cursor.description, row)}
            for row in rows
        ]
        return jsonify(data)
    except pymssql.Error as e:
        return jsonify(e)


@app.route('/users/<int:id>', methods=['POST'])
def get_User(id):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT username, useremail, userid, isActive FROM users where id = %s", (id))
        rows = cursor.fetchall()
        data = [
            {column[0]: value for column,value in zip(cursor.description, row)} for row in rows
        ]
        return jsonify(data)
    except pymssql.Error as e:
        return jsonify(e)


def Check_User(type):
    try:
        reqData = request.json
        cursor = conn.cursor()
        if type == 'register':
            cursor.execute("SELECT * FROM users where useremail = %s or userid = %s",
                           (reqData['useremail'], reqData['userid']))
        if type == 'login':
            cursor.execute("SELECT * FROM users where useremail = %s and userpassword = %s",
                           (reqData['useremail'], reqData['userpassword']))
        rows = cursor.fetchall()

        data = [
            {column[0]: value for column,
                value in zip(cursor.description, row)}
            for row in rows
        ]

        if type == 'register':
            if len(data) == 0:
                return 'success'
            for i in data:
                if i['useremail'] == reqData['useremail']:
                    return "Email already exist."
            for i in data:
                if i['userid'] == reqData['userid']:
                    return "Userid already exist."

        if type == 'login':
            if len(data) == 0:
                return 'Invalid Credentials.'
            else:
                return 'success'
    except pymssql.Error as e:
        return jsonify(e)


@app.route('/register', methods=['POST'])
def register_User():
    if Check_User("register") == 'success':
        reqData = request.json
        cursor = conn.cursor()
        cursor.execute("insert into users(useremail,userid,username,userpassword, isActive) values(%s, %s, %s, %s, %s)",
                       (reqData['useremail'], reqData['userid'], reqData['username'], reqData['userpassword'], 0))
        conn.commit()
        return jsonify("User register successfully!"), 201
    else:
        return jsonify(Check_User("register")), 409


@app.route('/login', methods=['POST'])
def login_User():
    if Check_User('login') == 'success':
        reqData = request.json
        cursor = conn.cursor()
        cursor.execute(
            "update users set isActive = %s where useremail=%s", (1, reqData['useremail']))
        conn.commit()
        return jsonify("User login successfully!"), 201
    else:
        return jsonify(Check_User('login')), 409


@app.route('/logout', methods=['POST'])
def logout_User():
    try:
        reqData = request.json
        cursor = conn.cursor()
        cursor.execute(
            "update users set isActive = %s where useremail=%s", (0, reqData['useremail']))
        conn.commit()
        return jsonify("User logout successfully!"), 201
    except pymssql.Error as e:
        return jsonify(e)


@app.route('/users/<int:id>', methods=['PUT'])
def update_User(id):
    try:
        reqData = request.json
        cursor = conn.cursor()
        cursor.execute("update users set username = %s where id=%s",
                       (reqData['username'], id))
        conn.commit()
        return jsonify("User updated successfully!"), 201
    except pymssql.Error as e:
        return jsonify(e)


@app.route('/users/<int:id>', methods=['DELETE'])
def delete_User(id):
    cursor = conn.cursor()
    cursor.execute("delete from users where id=%s", (id))
    conn.commit()
    return jsonify("User deleted successfully!"), 201


if __name__ == '__main__':
    app.run(debug=True)

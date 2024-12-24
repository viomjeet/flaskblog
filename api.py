from flask import Flask, jsonify, request
import pymssql

server = 'DESKTOP-B7RVLLM'
database = 'GingerView'
username = ''
password = ''
conn = pymssql.connect(
    server=server,
    user=username,
    password=password,
    database=database
)

try:
    cursor = conn.cursor()
    print("Connection successful!")
except pymssql.Error as e:
    print("Error while connecting to MSSQL:", e)
finally:
    if 'conn' in locals() and conn:
        conn.close()
        print("Connection closed.")
app = Flask(__name__)
items = []
conn = pymssql.connect(server=server, user=username,
                       password=password, database=database)


@app.route('/items', methods=['GET'])
def get_items():
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        data = [
            {column[0]: value for column,
                value in zip(cursor.description, row)}
            for row in rows
        ]
        return jsonify(data)
    except pymssql.Error as e:
        return jsonify(e)


@app.route('/items/<int:id>', methods=['GET'])
def get_item(id):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users where id = %s", (id))
        rows = cursor.fetchall()
        data = [
            {column[0]: value for column,
                value in zip(cursor.description, row)}
            for row in rows
        ]
        return jsonify(data)
    except pymssql.Error as e:
        return jsonify(e)


@app.route('/items', methods=['POST'])
def create_item():
    try:
        reqData = request.json
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users where useremail = %s or userid = %s",
                       (reqData['useremail'], reqData['userid']))
        rows = cursor.fetchall()
        data = [
            {column[0]: value for column,
                value in zip(cursor.description, row)}
            for row in rows
        ]
        if len(data) == 0:
            cursor = conn.cursor()
            cursor.execute("insert into users(useremail,userid,username,userpassword) values(%s, %s, %s, %s)",
                           (reqData['useremail'], reqData['userid'], reqData['username'], reqData['userpassword']))
            conn.commit()
            return jsonify("Data inserted successfully!"), 201
        for i in data:
            if i['useremail'] == reqData['useremail']:
                return jsonify("Email already exist."), 409
        for i in data:
            if i['userid'] == reqData['userid']:
                return jsonify("Userid already exist."), 409
    except pymssql.Error as e:
        return jsonify(e)


@app.route('/items/<int:id>', methods=['PUT'])
def update_item(id):
    reqData = request.json
    cursor = conn.cursor()
    cursor.execute("update users set username = %s where id=%s",(reqData['username'], id))
    conn.commit()
    return jsonify("User updated successfully!"), 201


@app.route('/items/<int:id>', methods=['DELETE'])
def delete_item(id):
    cursor = conn.cursor()
    cursor.execute("delete from users where id=%s",(id))
    conn.commit()
    return jsonify("User deleted successfully!"), 201

if __name__ == '__main__':
    app.run(debug=True)

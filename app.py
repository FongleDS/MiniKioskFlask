from flask import Flask, render_template, request, g, jsonify, Response
import sqlite3
import requests

app = Flask(__name__)
DATABASE = './static/DSCafeteria.db'
app.config['JSON_AS_ASCII'] = False


# db 가져오기
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.text_factory = str
    return db


# db 연결 끊기
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# sql문 받아와서 database 반환
@app.route('/dbupload')
def dbupload():
    url = "http://127.0.0.1:5000/sqlupload"

    response = requests.get(url)

    data = response.text
    sql = str(data)

    cur = get_db().cursor()
    cur.execute(sql)

    data = cur.fetchall()
    return jsonify(data)


# 식당별 대기 인원 카운트
@app.route('/restCount')
def restCount():
    sql_string = "SELECT R.RestID, COUNT(O.menuID) AS order_count FROM Restaurant R LEFT JOIN Menu M ON R.RestID = M.RestID LEFT JOIN OrderDetail O ON O.menuID = M.menuID AND O.orderstats = 'NO'GROUP BY R.RestID;"
    cur = get_db().cursor()
    cur.execute(sql_string)

    data = cur.fetchall()
    return jsonify(data)


# 로그인 할 때 학번 받아와서 패스워드 반환
@app.route('/get_password', methods=['POST'])
def get_password():
    std_id = request.form['stdID']
    # 데이터베이스 쿼리를 통해 해당 std_id의 비밀번호 검색
    print(std_id)

    cur = get_db().cursor()
    cur.execute("SELECT stdPW FROM Student WHERE stdID=?", (std_id,))
    password = cur.fetchone()
    print(password)

    if password:
        return jsonify({"password": password[0]})
    else:
        return jsonify({"error": "Student ID not found"}), 404

@app.route("/getOrderInfo", methods=['POST'])
def getOrderInfo():
    std_id = request.form['stdID']
    # 데이터베이스 쿼리를 통해 해당 std_id의 비밀번호 검색
    print(std_id)

    cur = get_db().cursor()
    cur.execute("SELECT orderID,orderDate,seatID FROM Orders WHERE Orders.stdID=?", (std_id,))
    info = cur.fetchone()
    print(info)

    if info:
        return jsonify({"orderid": info[0]}, {"orderdate": info[1]}, {"seatid": info[2]})
    else:
        return jsonify({"error": "Student ID not found"}), 404


# sql문 업로드
@app.route('/sqlupload')
def sqlupload():
    sql_string = "SELECT Orders.orderID, Menu.menuName, Menu.menuPrice FROM Orders, OrderDetail, Student, Menu WHERE Student.stdID = '20210796' and Student.stdID = Orders.stdID and Orders.orderID = OrderDetail.orderID and OrderDetail.menuID = Menu.menuID;"

    return str(sql_string)

# 시작 페이지 연결
@app.route("/")
def home():
    return render_template('startScreen.html')

# QR코드 리더기 페이지 연결
@app.route("/QRScreen")
def qrscreen():
    return render_template('QRScreen.html')

# bill 페이지 연결과 동시에 주문 내역 반환
@app.route('/billScreen', methods=['GET','POST'])
def bill():
    url = "http://127.0.0.1:5000/dbupload"

    response = requests.get(url)
    data = response.json()

    quantity = len(data)
    orderID = data[0][0]
    menu = data[0][1]
    price = data[0][2]

    total = price

    #total = sum(price)

    #cur = get_db().cursor()
    #cur.execute("INSERT INTO your_table_name (name, age) VALUES (?, ?)", (name, age))
    #get_db().commit()

    return render_template('billScreen.html', orderID=orderID, menu=menu, price=price, quantitiy = quantity, total = total)

@app.route("/paymentScreen")
def payment():
    return render_template('paymentScreen.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

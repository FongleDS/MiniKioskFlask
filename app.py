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
@app.route('/kioskbilldb')
def dbupload():
    sql = ("SELECT Orders.orderID, Menu.menuName, Menu.menuPrice FROM Orders, OrderDetail, Student, Menu WHERE Student.stdID = '20210796' and Student.stdID = Orders.stdID and Orders.orderID = OrderDetail.orderID and OrderDetail.menuID = Menu.menuID;")

    cur = get_db().cursor()
    cur.execute(sql)

    data = cur.fetchall()
    cur.close()
    return jsonify(data)


# 식당별 대기 인원 카운트
@app.route('/restCount')
def restCount():
    sql_string = "SELECT R.RestID, COUNT(O.menuID) AS order_count FROM Restaurant R LEFT JOIN Menu M ON R.RestID = M.RestID LEFT JOIN OrderDetail O ON O.menuID = M.menuID AND O.orderstats = 'NO'GROUP BY R.RestID;"
    cur = get_db().cursor()
    cur.execute(sql_string)

    data = cur.fetchall()
    cur.close()
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
    cur.close()
    print(password)

    if password:
        return jsonify({"password": password[0]})
    else:
        return jsonify({"error": "Student ID not found"}), 404

@app.route("/getOrderInfo", methods=['POST'])
def getOrderInfo():
    order_id = request.form['orderID']
    # 데이터베이스 쿼리를 통해 해당 std_id의 비밀번호 검색
    print(order_id)

    cur = get_db().cursor()
    cur.execute("SELECT Student.stdName, Orders.orderDate, Orders.seatID, Menu.menuName FROM Orders JOIN Student ON Orders.stdID = Student.stdIDJOIN OrderDetail ON Orders.orderID = OrderDetail.orderIDJOIN Menu ON OrderDetail.menuID = Menu.menuIDWHERE Orders.orderID = ?;", (order_id, ))
    info = cur.fetchone()
    cur.close()
    print(info)

    if info:
        return jsonify({"stdName": info[0]}, {"orderdate": info[1]}, {"seatid": info[2]}, {"menuName" : info[3]})
    else:
        return jsonify({"error": "Student ID not found"}), 404




@app.route('/orderUpdate', methods=['POST'])
def orderUpdate():
    std_id = request.form['stdID']
    menu_id = request.form['menuID']
    seat_id = request.form['seatID']
    order_date = request.form['orderDate']

    cur = get_db().cursor()

    last_inserted_id = ""

    try:
        # orderid 테이블에 데이터 삽입
        cur.execute("INSERT INTO Orders (stdID, orderDate, seatID) VALUES (?, ?, ?)", (std_id, order_date, seat_id))

        # 마지막에 삽입된 데이터의 ID를 가져옴
        last_inserted_id = cur.lastrowid
        print(last_inserted_id)
        # last_inserted_id = str(last_inserted_id)

        # orderdetail 테이블에 삽입
        cur.execute("INSERT INTO OrderDetail (orderID, menuID) VALUES (?, ?)",
                    (last_inserted_id, menu_id))
        get_db().commit()

    except Exception as e:
        print("Error:", e)
        get_db().rollback()

    finally:
        cur.close()

    cur.close()
    print("last_inserted_id : ", last_inserted_id)

    if last_inserted_id:
        return jsonify({"orderID": last_inserted_id})
    else:
        return jsonify({"error": "Student ID not found"}), 404



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
    url = "http://127.0.0.1:5000/kioskbilldb"

    response = requests.get(url)
    data = response.json()

    quantity = len(data)
    orderID = data[0][0]
    menu = data[0][1]
    price = data[0][2]

    total = price

    return render_template('billScreen.html', orderID=orderID, menu=menu, price=price, quantitiy = quantity, total = total)

@app.route("/paymentScreen")
def payment():
    return render_template('paymentScreen.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

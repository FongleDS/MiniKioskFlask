from flask import Flask, render_template, request, g, jsonify, Response
import sqlite3
import requests
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)
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

# 식당별 대기 인원 카운트
@app.route('/restCount')
def restCount():
    sql_string = "SELECT R.RestID, COUNT(O.menuID) AS order_count FROM Restaurant R LEFT JOIN Menu M ON R.RestID = M.RestID LEFT JOIN OrderDetail O ON O.menuID = M.menuID AND O.orderstats = '0' GROUP BY R.RestID;"
    cur = get_db().cursor()
    cur.execute(sql_string)

    data = cur.fetchall()
    cur.close()
    return jsonify(data)


# 좌석 정보 가져오기
@app.route('/seatInfo')
def seatInfo():
    sql_string = "SELECT seatID, seatUse FROM Seat;"
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
    cur.execute("SELECT stdPW, stdName FROM Student WHERE stdID=?;", (std_id,))
    data = cur.fetchone()
    cur.close()
    print(data)

    result = {
        "password": data[0],
        "name": data[1],
    }

    if result:
        return jsonify(result)
    else:
        return jsonify({"error": "Student ID not found"}), 404


# 로그인하기 위한 비밀 번호 가져오기
@app.route('/getRestPassword', methods=['POST'])
def getRestPW():
    RestID = request.form['RestID']
    # 데이터베이스 쿼리를 통해 해당 std_id의 비밀번호 검색
    print(RestID)

    cur = get_db().cursor()
    cur.execute("SELECT RestPW FROM Restaurant WHERE RestID=?", (RestID,))
    password = cur.fetchone()
    cur.close()
    print(password)

    if password:
        return jsonify({"password": password[0]})
    else:
        return jsonify({"error": "Student ID not found"}), 404

# 주문 정보 가져오기
@app.route("/getOrderInfo", methods=['POST'])
def getOrderInfo():
    order_id = request.form['orderID']
    # 데이터베이스 쿼리를 통해 해당 std_id의 비밀번호 검색
    print(order_id)

    cur = get_db().cursor()
    cur.execute("SELECT Student.stdName, Orders.orderDate, Orders.seatID, Orders.orderID FROM Orders JOIN Student ON Orders.stdID = Student.stdID JOIN OrderDetail ON Orders.orderID = OrderDetail.orderID JOIN Menu ON OrderDetail.menuID = Menu.menuID WHERE Orders.orderID = ?;", (order_id, ))
    info = cur.fetchone()
    cur.close()
    print(info)

    if info:
        return jsonify({"stdName": info[0]}, {"orderdate": info[1]}, {"seatid": info[2]},{"orderID": info[3]}, {"menuName" : "None"})
    else:
        return jsonify({"error": "Student ID not found"}), 404

# 잔여 좌석 가져오기
@app.route("/countSeat")
def countSeat():
    cur = get_db().cursor()
    cur.execute("SELECT COUNT(*) FROM seat WHERE seatUse = 'NO';")
    info = cur.fetchone()
    cur.close()
    print(info)

    return jsonify({"leftseat": info[0]})

# 장바구니 초기화
@app.route("/basketInit")
def basketInit():
    cur = get_db().cursor()
    cur.execute("DELETE FROM Basket;")
    get_db().commit()
    cur.close()
    return jsonify({"Result": "TRUE"})

# 장바구니에 메뉴 추가
@app.route("/basketUpdate", methods=['POST'])
def basketUpdate():
    menuID = request.form['menuID']

    cur = get_db().cursor()
    cur.execute("INSERT INTO Basket(menuID) VALUES (?);", (menuID, ));
    get_db().commit()

    cur.close()

    print(menuID)

    return jsonify({"Result": "TRUE"})

# 장바구니 정보 가져오기
@app.route("/getBasket")
def getBasket():
    total_info = []
    cur = get_db().cursor()
    cur.execute("SELECT menuID FROM Basket;")
    menus = cur.fetchall()
    print(menus)
    print(type(menus))

    for i in range(len(menus)):
        cur.execute("SELECT Menu.MenuName, Menu.menuprice, Restaurant.RestName, Menu.menuID FROM Restaurant, Menu WHERE Menu.MenuID = ? and Menu.RestID = Restaurant.RestID;", (menus[i][0], ))
        info = cur.fetchall()
        print(info)
        total_info.append(info)
        print(total_info)

    cur.close()

    return jsonify(total_info)

# 식당 별 대기인원 카운트
@app.route("/countWaiting")
def countWaiting():
    cur = get_db().cursor()
    cur.execute("SELECT COUNT(*) FROM OrderDetail WHERE orderstats = '0';")
    info = cur.fetchone()
    cur.close()
    print(info)

    return jsonify({"waiting": info[0]})


@app.route("/seatON", methods=['POST'])
def seatON():
    seatID = request.form['seatID']
    # 데이터베이스 쿼리를 통해 해당 std_id의 비밀번호 검색
    print(seatID)

    cur = get_db().cursor()
    cur.execute("UPDATE Seat SET seatUse = 'YES' WHERE seatID = ?;", (seatID, ))
    get_db().commit()
    cur.close()

    return jsonify({"Result": "TRUE"})


@app.route("/seatOFF", methods=['POST'])
def seatOFF():
    seatID = request.form['seatID']
    # 데이터베이스 쿼리를 통해 해당 std_id의 비밀번호 검색
    print(seatID)

    cur = get_db().cursor()
    cur.execute("UPDATE Seat SET seatUse = 'NO' WHERE seatID = ?;", (seatID, ))
    get_db().commit()
    cur.close()

    return jsonify({"Result": "FALSE"})


@app.route("/getSeatInfo", methods=['POST'])
def getSeatInfo():
    seatID = request.form['seatID']
    # 데이터베이스 쿼리를 통해 해당 std_id의 비밀번호 검색
    print(seatID)

    cur = get_db().cursor()
    cur.execute("SELECT seatUse FROM Seat WHERE seatID=?;", (seatID, ))
    info = cur.fetchone()
    cur.close()
    print(info)

    return jsonify({"Result": info[0]})


@app.route("/getmenuName", methods=['POST'])
def getmenuName():
    menuID = request.form['menuID']
    # 데이터베이스 쿼리를 통해 해당 std_id의 비밀번호 검색
    print(menuID)

    cur = get_db().cursor()
    cur.execute("SELECT menuName FROM menu WHERE menuID=?;", (menuID, ))
    info = cur.fetchone()
    cur.close()
    print(info)
    print("=========")

    return jsonify({"Menu": info[0]})

@app.route("/updateOrderStat", methods=['POST'])
def updateOrderStat():
    stat = request.form['stat']
    print(stat)
    orderID = request.form['orderID']
    print(orderID)
    realorderID = orderID.split(" ")
    print(realorderID[1])
    cur = get_db().cursor()

    if stat == "1":
        print("Send!")
        socketio.emit('pickup_alarm', "ALARM")
        cur.execute("SELECT COUNT(*) FROM OrderDetail, Orders WHERE OrderDetail.orderID=? and Orders.orderID=OrderDetail.orderID and OrderDetail.orderstats = '0';", (realorderID[1],))
        count = cur.fetchone()
        counts = str(count[0])
        print(counts)
        if counts == "0":
            print("LAST")
            socketio.emit('lastOrderAlarm', "LASTALARM")

    cur.execute("UPDATE OrderDetail SET orderstats = ? WHERE orderID = ?;", (stat, realorderID[1]))
    get_db().commit()
    cur.close()

    return jsonify({"Result": "ALARM"})


@app.route('/orderUpdate', methods=['POST'])
def orderUpdate():
    std_id = request.form['stdID']
    menu_id = request.form['menuID']
    print("menuID : ", menu_id)
    seat_id = request.form['seatID']
    order_date = request.form['orderDate']

    restID = [];
    response = [];

    menu_id = str(menu_id)
    menu_id = menu_id.replace(" ", "")
    menu_id = menu_id.replace("[", "")
    menu_id = menu_id.replace("]", "")

    menus = menu_id.split(",")
    print("menus : ", menus)


    cur = get_db().cursor()

    try:
        # orderid 테이블에 데이터 삽입
        cur.execute("INSERT INTO Orders (stdID, orderDate, seatID) VALUES (?, ?, ?)", (std_id, order_date, seat_id))

        # 마지막에 삽입된 데이터의 ID를 가져옴
        last_inserted_id = cur.lastrowid

        cur.execute("UPDATE Seat SET seatUse = 'YES' WHERE seatID = ?;", (seat_id, ))
        get_db().commit()

        for i in range(len(menus)):
            # orderdetail 테이블에 삽입
            cur.execute("INSERT INTO OrderDetail (orderID, menuID, orderStats) VALUES (?, ?, ?)",
                        (last_inserted_id, menus[i], '0'))
            get_db().commit()

            cur.execute("SELECT RestID FROM Menu WHERE menuID=?;", (menus[i],))
            info = cur.fetchall()
            restID.append(info[0])

    except Exception as e:
        print("Error:", e)
        get_db().rollback()

    print("last_inserted_id : ", last_inserted_id)
    print("restID : ", restID)
    print(type(restID))
    print(len(restID))

    results = {
        "orderID": last_inserted_id,
    }

    if last_inserted_id:
        for i in range(len(restID)):
            print(restID[i][0])
            result = {
                "orderID": last_inserted_id,
                "MenuID": menus[i],
                "StdID": std_id,
                "RestID": restID[i][0]
            }
            print("========")
            #socketio.emit('order_updated', result, broadcast=True)
            socketio.emit('order_updated', result)
            response.append(result)
            print(result)

        print(response)
        cur.close()

        # return jsonify(response)
        return jsonify(results)
    else:
        return jsonify({"error": "Student ID not found"}), 404


####################################### KIOSK 관련 CODE #######################################

billdata = []

# 시작 페이지 연결
@app.route("/")
def home():
    return render_template('startScreen.html')

# QR코드 리더기 페이지 연결
@app.route("/QRScreen")
def qrscreen():
    return render_template('QRScreen.html')


#QR코드 읽고 정보 가져오기
@app.route("/getQRInfo", methods=['POST', 'GET'])
def QRInfo():

    qrdata = request.json['qrData']
    info = qrdata.split("_")
    print(info)

    stdID = str(info[1])
    orderID = str(info[0])
    sql = "SELECT Orders.orderID, Menu.menuName, Menu.menuPrice, Orders.quantity FROM Orders JOIN OrderDetail ON Orders.orderID = OrderDetail.orderID JOIN Menu ON OrderDetail.menuID = Menu.menuID JOIN Student ON Student.stdID = Orders.stdID WHERE Student.stdID = ? AND Orders.orderID = ?;"

    cur = get_db().cursor()
    cur.execute(sql, (stdID, orderID))
    data_list = cur.fetchall()
    print(data_list)
    cur.close()

    # 기존 billdata 초기화
    billdata.clear()

    for item in data_list:
        billdata.append({
            "orderID": item[0],
            "menu": item[1],
            "price": item[2],
            "quantity" : item[3]
        })

    print(billdata)

    return jsonify(data_list)


# bill 페이지 연결과 동시에 주문 내역 반환
@app.route('/billScreen', methods=['GET','POST'])
def bill():
    total = sum(menu["price"] for menu in billdata)
    print(billdata)
    print(total)
    return render_template('billScreen.html', billdata=billdata, total = total)


# 결제창 연결
@app.route("/paymentScreen", methods=['GET', 'POST'])
def payment():
    total = sum(menu["price"] for menu in billdata)
    return render_template('paymentScreen.html', total = total)


# 결제 완료창 연결
@app.route("/completeScreen")
def complete():
    stat = 2
    print(stat)
    orderID = billdata[0]["orderID"]
    print(orderID)
    # realorderID = orderID.split(" ")
    # print(realorderID[1])
    cur = get_db().cursor()

    cur.execute("UPDATE OrderDetail SET orderstats = ? WHERE orderID = ?;", (stat, orderID))
    get_db().commit()

    cur.execute("SELECT seatID FROM Orders WHERE orderID = ?;", (orderID,))
    seatIDs = cur.fetchall()
    print(seatIDs)


    # seatIDs 리스트의 각 seatID에 대해 업데이트 수행
    for seatID in seatIDs:
        cur.execute("UPDATE Seat SET seatUse = 'NO' WHERE seatID = ?;", (seatID[0],))

    # 커밋
    get_db().commit()
    cur.close()

    return render_template('completeScreen.html')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
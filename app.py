import json

from flask import Flask, render_template, request, g, jsonify, Response
import sqlite3
import requests

app = Flask(__name__)
DATABASE = './static/DSCafeteria.db'
app.config['JSON_AS_ASCII'] = False

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.text_factory = str
    return db

def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

#database불러오기
@app.route('/dbupload')
def some_endpoint():
    cur = get_db().cursor()
    cur.execute("SELECT * FROM Student")
    data = cur.fetchall()
    return jsonify(data)

@app.route("/")
def home():
    return render_template('startScreen.html')

@app.route("/QRScreen")
def qrscreen():
    return render_template('QRScreen.html')

# html로 변수 전달
@app.route('/billScreen', methods=['GET','POST'])
def bill():
    url = "http://127.0.0.1:5000/dbupload"

    # 해당 URL로 GET 요청 수행
    response = requests.get(url)

    # JSON 데이터로 변환
    data = response.json()

    name = data[0][1]
    id = data[0][0]

    #cur = get_db().cursor()
    #cur.execute("INSERT INTO your_table_name (name, age) VALUES (?, ?)", (name, age))
    #get_db().commit()

    return render_template('billScreen.html', name = name, id = id)

@app.route("/paymentScreen")
def payment():
    return render_template('paymentScreen.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

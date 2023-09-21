from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('startScreen.html')

@app.route("/QRScreen")
def qrscreen():
    return render_template('QRScreen.html')

# html로 변수 전달
@app.route('/billScreen', methods=['GET','POST'])
def bill():
    value = 'hello, world'
    return render_template('billScreen.html', value=value)

@app.route("/paymentScreen")
def payment():
    return render_template('paymentScreen.html')


@app.route('/post', methods=['GET','POST'])
def post():
    if request.method == 'POST':
        value = request.form['id_name']
        value = str(value)
        print(value)
    return render_template('post.html')




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

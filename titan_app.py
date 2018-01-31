from flask import Flask, render_template
from flask import request
from flask_debugtoolbar import DebugToolbarExtension
from core import titan_main

app = Flask(__name__)

app.config['SECRET_KEY'] = '100'
app.debug = True
toolbar = DebugToolbarExtension(app)


@app.route("/")
def mainpage():
    return render_template('main.html')


@app.route("/initialize_bot", methods=['POST'])
def initialize_bot():
    user_exchange = request.form['exchange']
    user_basecurrency = request.form['basecurrency']
    user_quotecurrency = request.form['quotecurrency']
    user_candleinterval = request.form['candleinterval']
    user_simulationtrade = 1

    user_input = [user_exchange.lower(), user_basecurrency.upper(), user_quotecurrency.upper(), user_candleinterval, bool(user_simulationtrade)]

    titan_main.main(user_input)

    return render_template('results.html')


@app.route("/contact")
def contactpage():
    return render_template('main.html')


@app.route("/about")
def aboutpage():
    return render_template('main.html')


@app.route("/github")
def githubpage():
    return render_template('main.html')


if __name__ == "__main__":
    app.run(port=5555)

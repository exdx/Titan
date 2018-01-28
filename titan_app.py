from flask import Flask, render_template
from flask import request
from flask_debugtoolbar import DebugToolbarExtension
from flask.json import jsonify
from core import titan_main

app = Flask(__name__)

app.config['SECRET_KEY'] = 'asdfg'
app.debug = True
toolbar = DebugToolbarExtension(app)


@app.route("/")
def mainpage():
    return render_template('main.html')


@app.route("/", methods=['POST'])
def trading_settings_form_post():
    user_exchange = request.form['exchange']
    user_basecurrency = request.form['basecurrency']
    user_quotecurrency = request.form['quotecurrency']
    user_candleinterval = request.form['candleinterval']
    user_simulationtrade = request.form['simulation_setting']

    user_input = [user_exchange.lower(), user_basecurrency.lower(), user_quotecurrency.lower(), user_candleinterval.lower(), bool(user_simulationtrade)]

    return jsonify(user_input)


@app.route("/forward", methods=['GET', 'POST'])
def move_forward():
    titan_main.main(d)
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

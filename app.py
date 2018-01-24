from flask import Flask, render_template
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)

app.config['SECRET_KEY'] = 'asdfg'
app.debug = True
toolbar = DebugToolbarExtension(app)


@app.route("/")
def hello():
    return render_template('main.html')


if __name__ == "__main__":
    app.run(port=5555)

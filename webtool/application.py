from flask import Flask
from flask import render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/set-enabled/<enabled>')
def set_enabled(enabled):
    return render_template('set_enabled.html', enabled=enabled)

@app.route('/activate')
def activate():
    return set_enabled(True)

@app.route('/deactivate')
def deactivate():
    return set_enabled(False)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
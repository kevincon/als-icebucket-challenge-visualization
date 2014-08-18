from flask import Flask, render_template
from als import get_updates, process_stream
from thread import start_new_thread

app = Flask(__name__)

app.debug = True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_updates')
def updates():
    u = get_updates()
    return u

if __name__ == '__main__':
    start_new_thread(process_stream, ())
    app.run()
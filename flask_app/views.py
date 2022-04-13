from flask import render_template

from flask_app import app


@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/upload', methods=['GET'])
def upload_get():
    return render_template('upload.html')


@app.errorhandler(500)
def server_error(e):
    r = render_template('error.html', body=str(e.original_exception))
    return r, 500

from flask import Flask
app = Flask(__name__)

INCLUDE_VIEWS = False

from . import models

if INCLUDE_VIEWS:
    from . import views
else:
    @app.route('/')
    def hello():
        return models.render_template('', error_code=0, message='Hello World')

    @app.errorhandler(500)
    def server_error(e):
        return models.render_template('', error_code=-1, body=dict(exception=f'{type(e)}: {str(e)}'))

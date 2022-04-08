from flask import Flask
app = Flask(__name__)

INCLUDE_VIEWS = False

from . import models

if INCLUDE_VIEWS:
    from . import views
else:
    @app.route('/')
    def hello():
        return dict(message='Hello World')

    @app.errorhandler(500)
    def server_error(e):
        return dict(exception=f'{type(e)}: {str(e)}')

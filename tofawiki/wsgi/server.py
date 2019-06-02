import os

from flask import Blueprint, Flask

from . import routes


def configure(config):
    directory = os.path.dirname(os.path.realpath(__file__))
    app = Flask('tofawiki')
    bp = Blueprint('tofawiki', __name__,
                   static_folder=os.path.join(directory, 'static'))
    bp = routes.configure(config, bp)
    app.register_blueprint(bp, url_prefix=config['wsgi']['url_prefix'])
    return app

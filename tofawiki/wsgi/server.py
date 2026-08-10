import logging
import traceback
from typing import Any, Mapping, Optional

from flask import Blueprint, Flask, jsonify
from werkzeug.exceptions import HTTPException

from ..config import load_config
from . import routes

logger = logging.getLogger(__name__)


def create_app(config: Optional[Mapping[str, Any]] = None) -> Flask:
    """Build the tofawiki Flask application.

    Called without arguments the config is read from the usual places, so a
    WSGI server can boot the app with ``tofawiki.wsgi:create_app()``.
    """
    if config is None:
        config = load_config()

    app = Flask('tofawiki')
    app.config['TOFAWIKI'] = config

    bp = Blueprint('tofawiki', __name__)
    routes.configure(config, bp)
    app.register_blueprint(bp, url_prefix=config['wsgi'].get('url_prefix') or None)

    register_error_handlers(app)
    return app


def register_error_handlers(app: Flask) -> None:
    """Answer with JSON rather than HTML, since this is a JSON API."""

    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        response = jsonify({'error': error.description})
        response.status_code = error.code or 500
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

    @app.errorhandler(Exception)
    def handle_unexpected_exception(error: Exception):
        if app.debug:
            # Let the interactive debugger take over on the dev server.
            raise error
        logger.exception('Unhandled error while serving a request')
        response = jsonify({
            'error': 'Unable to translate. Copy paste this for Amir: ' + traceback.format_exc()
        })
        response.status_code = 500
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response


def configure(config: Mapping[str, Any]) -> Flask:
    """Deprecated alias kept for existing WSGI entry points."""
    return create_app(config)

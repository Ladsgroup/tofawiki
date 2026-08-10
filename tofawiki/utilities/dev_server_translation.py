"""Starts a development web server for the translation service.

This is the development server only; in production the app is served through a
WSGI server, e.g. ``gunicorn 'tofawiki.wsgi:create_app()'``.
"""
import argparse
import logging
from typing import List, Optional

from ..config import load_config
from ..wsgi import create_app


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog='tofawiki dev_server_translation',
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--host', default='127.0.0.1',
                        help='The interface to bind to (default: %(default)s)')
    parser.add_argument('--port', type=int, default=8080,
                        help='The port number to start the server on (default: %(default)s)')
    parser.add_argument('--config', default=None,
                        help='The path to a directory containing config files')
    parser.add_argument('--ssl', action='store_true',
                        help='If set, run the server on ad-hoc SSL (https)')
    parser.add_argument('--verbose', action='store_true',
                        help='Print logging information')
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    app = create_app(load_config(args.config))
    app.run(
        host=args.host,
        port=args.port,
        debug=True,
        ssl_context='adhoc' if args.ssl else None,
    )

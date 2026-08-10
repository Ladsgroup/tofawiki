# Tofawiki
It's source of the tofawiki service at tofawiki.wmcloud.org


## Server
The flask app is an application factory, `tofawiki.wsgi:create_app`, so in
production it is served by any WSGI server:

    $ gunicorn 'tofawiki.wsgi:create_app()'

Config is read from the directory named by `$TOFAWIKI_CONFIG`, falling back to
`config/`.

### Installation

#### Dependencies
Installation will require some additional packages to be available.

  `sudo apt-get install python3-dev`

#### Installing tofawiki
Packaging metadata lives in `pyproject.toml`; Python 3.9 or newer is required.

    $ pip install .

or, for development, an editable install:

    $ pip install -e .

Runtime dependencies are declared in `requirements.txt`, which `pyproject.toml`
reads, so `pip install -r requirements.txt` and the package metadata cannot
drift apart. The version is read from `tofawiki/__init__.py`, so that is the
only place to bump it for a release.

To build a wheel and an sdist:

    $ pip install build
    $ python -m build

### Starting the dev server

    $ tofawiki dev_server_translation --config config/

Useful flags: `--host`, `--port` (default 8080), `--ssl`, `--verbose`. The dev
server binds to localhost only; pass `--host 0.0.0.0` to expose it.

## See also
* [WP:tofawiki](https://fa.wikipedia.org/wiki/%D9%88%DB%8C%DA%A9%DB%8C%E2%80%8C%D9%BE%D8%AF%DB%8C%D8%A7:%D8%AA%D9%88%D9%81%D8%A7%D9%88%DB%8C%DA%A9%DB%8C)

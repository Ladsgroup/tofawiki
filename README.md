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

### Talking to the wikis
`tofawiki/mediawiki/` is a small client for the MediaWiki Action API built on
`requests`; it replaced pywikibot. It offers just the surface this service
uses, under the names the domain code already called:

| | |
| --- | --- |
| `Site(code, family)` | an endpoint; `dbName()`, `data_repository()` |
| `Page(site, title)` | `get()`, `.text`, `title()`, `namespace()`, `isRedirectPage()`, `getRedirectTarget()`, `permalink()` |
| `ItemPage` / `Claim` | `fromPage()`, `get()`, `.claims`, `getTarget()` |
| `Request(site=…, **params).submit()` | a raw Action API call returning parsed JSON |
| `extract_templates_and_params()` | template parsing, via `mwparserfromhell` |

`Page.get()` raises `NoPageError` or `IsRedirectPageError`, while `.text`
returns `''` for a missing page — the same split pywikibot made, which
`Translate.validate()` depends on. `Request` defaults to `formatversion=1`
because the langlink handling reads the legacy `'*'` keys.

Every request identifies itself with a `User-Agent` naming the project; the
Wikimedia cluster answers `403` without one.

#### Linting
Linting is done with [ruff](https://docs.astral.sh/ruff/), configured under
`[tool.ruff]` in `pyproject.toml` (it replaced flake8, whose config used to live
in `setup.cfg`).

    $ pip install ruff
    $ ruff check .
    $ ruff check --fix .

The enabled rule sets are `E`/`F`/`W` (the pycodestyle and pyflakes checks
flake8 ran), plus `I` for import sorting, `UP` for Python-version upgrades and
`B` for bugbear checks.

### Starting the dev server

    $ tofawiki dev_server_translation --config config/

Useful flags: `--host`, `--port` (default 8080), `--ssl`, `--verbose`. The dev
server binds to localhost only; pass `--host 0.0.0.0` to expose it.

## See also
* [WP:tofawiki](https://fa.wikipedia.org/wiki/%D9%88%DB%8C%DA%A9%DB%8C%E2%80%8C%D9%BE%D8%AF%DB%8C%D8%A7:%D8%AA%D9%88%D9%81%D8%A7%D9%88%DB%8C%DA%A9%DB%8C)

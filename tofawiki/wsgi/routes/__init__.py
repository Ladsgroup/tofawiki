from collections.abc import Mapping
from typing import Any

from flask import Blueprint, Response

from . import translate


def configure(config: Mapping[str, Any], bp: Blueprint) -> Blueprint:

    @bp.after_request
    def allow_cross_origin_reads(response: Response) -> Response:
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

    @bp.route('/')
    def root() -> str:
        return 'Hey, In order to use the service use tofawiki.wmcloud.org/' \
               'translate/enwiki/Article_Name</br>Source code in ' \
               '<a href="https://github.com/Ladsgroup/tofawiki">github</a>'

    return translate.configure(bp, config)

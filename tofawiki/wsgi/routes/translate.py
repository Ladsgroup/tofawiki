import json

from flask import Response

from ...services.translation.translate import Translate


def configure(bp, config):

    @bp.route('/translate/<wiki>/')
    def with_wiki(wiki):
        return 'Give me article name please'

    @bp.route('/translate/<wiki>/<article>/<faname>')
    def translation_service(wiki, article, faname):
        # We use disposable services, we do caching other ways
        service = Translate(wiki, article, faname, config)
        resp = Response(json.dumps(service.run()),
                        mimetype="application/json")
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

    return bp

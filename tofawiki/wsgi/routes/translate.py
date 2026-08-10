from typing import Any, Mapping

from flask import Blueprint, Response, jsonify

from ...services.translation.translate import Translate


def configure(bp: Blueprint, config: Mapping[str, Any]) -> Blueprint:

    @bp.route('/translate/<wiki>/')
    def with_wiki(wiki: str) -> str:
        return 'Give me article name please'

    @bp.route('/translate/<wiki>/<article>/<faname>')
    def translation_service(wiki: str, article: str, faname: str) -> Response:
        wiki_config = config.get(wiki)
        if not isinstance(wiki_config, Mapping) or 'code_lang' not in wiki_config:
            return jsonify({'error': f'Unknown wiki: {wiki}'})
        # We use disposable services, we do caching other ways
        service = Translate(wiki, article, faname, config)
        return jsonify(service.run())

    return bp

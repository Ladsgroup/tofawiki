"""Wikitext parsing helpers.

``extract_templates_and_params`` keeps the pywikibot signature and semantics;
pywikibot implemented it on top of mwparserfromhell too, so results match,
including the detail that positional parameters are not stripped.
"""
from collections import OrderedDict
from typing import Optional

import mwparserfromhell


def extract_templates_and_params(
    text: str,
    remove_disabled_parts: Optional[bool] = False,
    strip: bool = False,
) -> list[tuple[str, 'OrderedDict[str, str]']]:
    """Return ``(template name, params)`` for every template in *text*.

    Unnamed parameters are keyed by their position as strings, as MediaWiki
    does. Parser functions (``{{#if:}}``) are skipped.
    """
    if remove_disabled_parts:
        text = remove_disabled(text)

    result = []
    parsed = mwparserfromhell.parse(text)
    templates = parsed.ifilter_templates(
        matches=lambda node: not str(node.name).lstrip().startswith('#'),
        recursive=True,
    )

    for template in templates:
        params: OrderedDict[str, str] = OrderedDict()
        for param in template.params:
            value = str(param.value)
            if strip:
                key = str(param.name).strip()
                # Positional values keep their whitespace, as in MediaWiki.
                if param.showkey:
                    value = str(param.value).strip()
            else:
                key = str(param.name)
            params[key] = value
        result.append((str(template.name).strip(), params))
    return result


def remove_disabled(text: str) -> str:
    """Drop comments, nowiki and pre blocks."""
    parsed = mwparserfromhell.parse(text)
    for node in parsed.ifilter_comments(recursive=True):
        try:
            parsed.remove(node)
        except ValueError:
            continue
    for node in parsed.ifilter_tags(recursive=True):
        if str(node.tag).lower() in ('nowiki', 'pre'):
            try:
                parsed.remove(node)
            except ValueError:
                continue
    return str(parsed)

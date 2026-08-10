"""Errors raised by the MediaWiki client.

The names mirror the pywikibot exceptions this package replaced, since the
service distinguishes "no such page" from "that is a redirect" when it decides
whether an article can be translated.
"""


class MediaWikiError(Exception):
    """Base class for every error raised by this package."""


class APIError(MediaWikiError):
    """The API replied with an ``error`` object."""

    def __init__(self, code: str, info: str):
        self.code = code
        self.info = info
        super().__init__(f'{code}: {info}')


class NoPageError(MediaWikiError):
    """The requested page (or Wikidata item) does not exist."""

    def __init__(self, title: str):
        self.title = title
        super().__init__(f'{title} does not exist')


class IsRedirectPageError(MediaWikiError):
    """The requested page is a redirect."""

    def __init__(self, title: str):
        self.title = title
        super().__init__(f'{title} is a redirect page')

"""Wiki endpoints, addressed the way pywikibot's ``Site`` was."""
from typing import Optional
from urllib.parse import urlparse

import requests

from .api import ApiClient

WIKIDATA_URL = 'https://www.wikidata.org/w/api.php'
COMMONS_URL = 'https://commons.wikimedia.org/w/api.php'

# One connection pool for the whole process; every Site shares it.
_SESSION = requests.Session()


class Site:
    """A single wiki, e.g. ``Site('en')`` for the English Wikipedia."""

    def __init__(self, code: str, family: str = 'wikipedia',
                 session: Optional[requests.Session] = None):
        self.code = code
        self.family = family
        self.client = ApiClient(self.api_url(), session=session or _SESSION)

    def api_url(self) -> str:
        if self.family == 'wikidata':
            return WIKIDATA_URL
        if self.family == 'commons':
            return COMMONS_URL
        return f'https://{self.code}.{self.family}.org/w/api.php'

    def dbName(self) -> str:  # noqa: N802 - kept from the pywikibot API
        """The database name, e.g. ``enwiki``, used as a Wikidata site id."""
        if self.family == 'wikidata':
            return 'wikidatawiki'
        if self.family == 'commons':
            return 'commonswiki'
        # Wikipedias are <code>wiki; the other families spell themselves out,
        # e.g. enwiktionary.
        suffix = 'wiki' if self.family == 'wikipedia' else self.family
        return f'{self.code}{suffix}'.replace('-', '_')

    def protocol(self) -> str:
        return 'https'

    def hostname(self) -> str:
        return urlparse(self.api_url()).netloc

    def scriptpath(self) -> str:
        """The wiki's script path, e.g. ``/w``."""
        return urlparse(self.api_url()).path.rsplit('/', 1)[0]

    def data_repository(self) -> 'Site':
        """The Wikibase repository holding this wiki's items."""
        return Site('wikidata', 'wikidata')

    def __repr__(self) -> str:
        return f'Site({self.code!r}, {self.family!r})'

    def __eq__(self, other: object) -> bool:
        return (isinstance(other, Site)
                and (self.code, self.family) == (other.code, other.family))

    def __hash__(self) -> int:
        return hash((self.code, self.family))

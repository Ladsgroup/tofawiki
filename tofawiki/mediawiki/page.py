"""Wiki pages, addressed the way pywikibot's ``Page`` was."""
from typing import Any, Optional
from urllib.parse import quote

from .exceptions import IsRedirectPageError, NoPageError

# Only the namespaces this service actually branches on. `namespace()` prefers
# the number the API reports; this map is the fallback before a page is loaded.
NAMESPACES = {
    'media': -2, 'special': -1, 'talk': 1, 'user': 2, 'user talk': 3,
    'project': 4, 'project talk': 5, 'file': 6, 'image': 6, 'file talk': 7,
    'mediawiki': 8, 'mediawiki talk': 9, 'template': 10, 'template talk': 11,
    'help': 12, 'help talk': 13, 'category': 14, 'category talk': 15,
}


class Page:
    """A page on a :class:`Site`, loaded lazily."""

    def __init__(self, site, title: str):
        self.site = site
        self._title = self.normalize_title(title)
        self._text: Optional[str] = None
        self._info: Optional[dict[str, Any]] = None

    @staticmethod
    def normalize_title(title: str) -> str:
        """Underscores become spaces and the first letter is capitalised.

        MediaWiki does this server-side too, but titles are compared and
        embedded in wikitext before any request is made.
        """
        title = title.replace('_', ' ').strip()
        if ':' in title:
            prefix, _, rest = title.partition(':')
            if prefix.strip().lower() in NAMESPACES:
                rest = rest.strip()
                return f'{prefix.strip().capitalize()}:{rest[:1].upper()}{rest[1:]}'
        return title[:1].upper() + title[1:]

    def title(self, underscore: bool = False, withNamespace: bool = True,  # noqa: N803
              as_url: bool = False) -> str:
        title = self._title
        if not withNamespace and ':' in title:
            prefix, _, rest = title.partition(':')
            if prefix.lower() in NAMESPACES:
                title = rest
        if underscore or as_url:
            title = title.replace(' ', '_')
        if as_url:
            title = quote(title.encode('utf-8'), safe='')
        return title

    def _load(self) -> dict[str, Any]:
        """Fetch content and metadata, following nothing."""
        if self._info is None:
            data = self.site.client.request({
                'action': 'query',
                'prop': 'revisions|info',
                'rvprop': 'content|ids',
                'rvslots': 'main',
                'titles': self._title,
                'formatversion': '2',
            })
            pages = data.get('query', {}).get('pages', [])
            self._info = pages[0] if pages else {'missing': True}
            # Adopt the title the server normalised to.
            if self._info.get('title'):
                self._title = self._info['title']
        return self._info

    def exists(self) -> bool:
        return not self._load().get('missing', False)

    def isRedirectPage(self) -> bool:  # noqa: N802 - kept from the pywikibot API
        return bool(self._load().get('redirect', False))

    def namespace(self) -> int:
        info = self._load()
        if 'ns' in info:
            return info['ns']
        prefix = self._title.partition(':')[0].lower()
        return NAMESPACES.get(prefix, 0)

    def get(self, get_redirect: bool = False) -> str:
        """Return the wikitext.

        :raises NoPageError: the page does not exist.
        :raises IsRedirectPageError: the page is a redirect and *get_redirect*
            was not requested.
        """
        info = self._load()
        if info.get('missing'):
            raise NoPageError(self._title)
        if info.get('redirect') and not get_redirect:
            raise IsRedirectPageError(self._title)
        if self._text is None:
            revisions = info.get('revisions') or [{}]
            self._text = revisions[0].get('slots', {}).get('main', {}).get('content', '')
        return self._text

    @property
    def text(self) -> str:
        """The wikitext, or '' when the page is missing.

        Unlike :meth:`get` this never raises, matching how the callers use it.
        """
        try:
            return self.get(get_redirect=True)
        except NoPageError:
            return ''

    @property
    def latest_revision_id(self) -> Optional[int]:
        """The revid of the current revision."""
        revisions = self._load().get('revisions') or [{}]
        return revisions[0].get('revid')

    def permalink(self, oldid: Optional[int] = None, percent_encoded: bool = True,
                  with_protocol: bool = False) -> str:
        """A permanent link to this revision, in pywikibot's format."""
        if percent_encoded:
            title = self.title(as_url=True)
        else:
            title = self.title().replace(' ', '_')
        protocol = f'{self.site.protocol()}:' if with_protocol else ''
        revid = oldid if oldid is not None else self.latest_revision_id
        return (f'{protocol}//{self.site.hostname()}{self.site.scriptpath()}'
                f'/index.php?title={title}&oldid={revid}')

    def getRedirectTarget(self) -> 'Page':  # noqa: N802 - kept from the pywikibot API
        """Resolve one step of redirection, server-side."""
        data = self.site.client.request({
            'action': 'query',
            'titles': self._title,
            'redirects': '1',
            'formatversion': '2',
        })
        redirects = data.get('query', {}).get('redirects', [])
        for redirect in redirects:
            if redirect.get('from') == self._title:
                return Page(self.site, redirect['to'])
        if redirects:
            return Page(self.site, redirects[-1]['to'])
        raise IsRedirectPageError(f'{self._title} has no redirect target')

    def __repr__(self) -> str:
        return f'Page({self.site!r}, {self._title!r})'

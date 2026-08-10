"""Wikidata items and claim values, addressed the way pywikibot's were."""
import re
from typing import Any, Optional, Union

from .exceptions import NoPageError
from .page import Page
from .site import Site

TIMESTR_RE = re.compile(
    r'^(?P<sign>[-+])(?P<year>\d+)-(?P<month>\d+)-(?P<day>\d+)'
    r'T(?P<hour>\d+):(?P<minute>\d+):(?P<second>\d+)Z$'
)


class WbTime:
    """A Wikidata time value."""

    # pywikibot's format: the year is zero-padded to 11 digits after the sign.
    FORMATSTR = '{0:+012d}-{1:02d}-{2:02d}T{3:02d}:{4:02d}:{5:02d}Z'

    def __init__(self, year: int, month: int = 0, day: int = 0, hour: int = 0,
                 minute: int = 0, second: int = 0, precision: Optional[int] = None,
                 calendarmodel: Optional[str] = None):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
        self.precision = precision
        self.calendarmodel = calendarmodel

    @classmethod
    def fromTimestr(cls, timestr: str, **kwargs) -> 'WbTime':  # noqa: N802
        match = TIMESTR_RE.match(timestr)
        if not match:
            raise ValueError(f'Invalid Wikibase timestamp: {timestr!r}')
        year = int(match.group('year'))
        if match.group('sign') == '-':
            year = -year
        return cls(year, int(match.group('month')), int(match.group('day')),
                   int(match.group('hour')), int(match.group('minute')),
                   int(match.group('second')), **kwargs)

    def toTimestr(self) -> str:  # noqa: N802 - kept from the pywikibot API
        return self.FORMATSTR.format(self.year, self.month, self.day,
                                     self.hour, self.minute, self.second)

    def __repr__(self) -> str:
        return f'WbTime({self.toTimestr()})'


class WbQuantity:
    """A Wikidata quantity; only its truthiness is used."""

    def __init__(self, amount: str, unit: Optional[str] = None):
        self.amount = amount
        self.unit = unit

    def __repr__(self) -> str:
        return f'WbQuantity({self.amount})'


class Coordinate:
    """A Wikidata globe coordinate; only its truthiness is used."""

    def __init__(self, lat: float, lon: float, globe: Optional[str] = None):
        self.lat = lat
        self.lon = lon
        self.globe = globe

    def __repr__(self) -> str:
        return f'Coordinate({self.lat}, {self.lon})'


class WbMonolingualText:
    """A Wikidata monolingual text value."""

    def __init__(self, text: str, language: str):
        self.text = text
        self.language = language

    def __str__(self) -> str:
        return self.text


class FilePage(Page):
    """A file description page, as commonsMedia claims resolve to."""

    def __init__(self, site: Optional[Site], title: str):
        # commonsMedia values are bare filenames, but tolerate a File: prefix.
        if title.lower().startswith('file:'):
            title = title[len('file:'):]
        super().__init__(site or Site('commons', 'commons'), f'File:{title}')


class ItemPage:
    """A Wikidata item."""

    def __init__(self, repo: Optional[Site], item_id: str):
        self.repo = repo or Site('wikidata', 'wikidata')
        self.id = item_id
        self.claims: dict[str, list[Claim]] = {}
        self.labels: dict[str, str] = {}
        self.sitelinks: dict[str, Any] = {}
        self._loaded = False

    @classmethod
    def fromPage(cls, page: Page) -> 'ItemPage':  # noqa: N802 - kept from pywikibot
        """The item connected to *page*.

        :raises NoPageError: the page has no Wikidata item.
        """
        data = page.site.client.request({
            'action': 'query',
            'prop': 'pageprops',
            'ppprop': 'wikibase_item',
            'titles': page.title(),
            'formatversion': '2',
        })
        pages = data.get('query', {}).get('pages', [])
        item_id = None
        if pages:
            item_id = pages[0].get('pageprops', {}).get('wikibase_item')
        if not item_id:
            raise NoPageError(f'Wikidata item for {page.title()}')
        return cls(page.site.data_repository(), item_id)

    def getID(self, numeric: bool = False) -> Union[str, int]:  # noqa: N802
        return int(self.id[1:]) if numeric else self.id

    def title(self, **kwargs) -> str:
        return self.id

    def get(self, force: bool = False) -> dict[str, Any]:
        """Load claims, labels and sitelinks.

        :raises NoPageError: the item does not exist.
        """
        if self._loaded and not force:
            return {'claims': self.claims, 'labels': self.labels}

        data = self.repo.client.request({
            'action': 'wbgetentities',
            'ids': self.id,
            'props': 'claims|labels|sitelinks',
        })
        entity = data.get('entities', {}).get(self.id, {})
        if 'missing' in entity:
            raise NoPageError(self.id)

        self.claims = {
            prop: [Claim(self.repo, snak) for snak in snaks]
            for prop, snaks in entity.get('claims', {}).items()
        }
        self.labels = {
            lang: value['value'] for lang, value in entity.get('labels', {}).items()
        }
        self.sitelinks = entity.get('sitelinks', {})
        self._loaded = True
        return {'claims': self.claims, 'labels': self.labels}

    def __repr__(self) -> str:
        return f'ItemPage({self.id})'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ItemPage) and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


class Claim:
    """One statement on an item."""

    def __init__(self, repo: Site, data: dict[str, Any]):
        self.repo = repo
        self.data = data
        self.snak = data.get('mainsnak', data)

    def getTarget(self) -> Any:  # noqa: N802 - kept from the pywikibot API
        """The claim's value, as the matching Python object.

        ``None`` for ``novalue``/``somevalue`` snaks, matching pywikibot.
        """
        snak = self.snak
        if snak.get('snaktype') != 'value':
            return None

        datatype = snak.get('datatype')
        datavalue = snak.get('datavalue', {})
        value = datavalue.get('value')
        if value is None:
            return None

        value_type = datavalue.get('type')
        if value_type == 'wikibase-entityid':
            entity_id = value.get('id') or f"Q{value.get('numeric-id')}"
            return ItemPage(self.repo, entity_id)
        if value_type == 'time':
            return WbTime.fromTimestr(value['time'], precision=value.get('precision'),
                                      calendarmodel=value.get('calendarmodel'))
        if value_type == 'globecoordinate':
            return Coordinate(value.get('latitude'), value.get('longitude'),
                              value.get('globe'))
        if value_type == 'quantity':
            return WbQuantity(value.get('amount'), value.get('unit'))
        if value_type == 'monolingualtext':
            return WbMonolingualText(value.get('text', ''), value.get('language', ''))
        if datatype == 'commonsMedia':
            return FilePage(None, value)
        return value

    def __repr__(self) -> str:
        return f'Claim({self.snak.get("property")})'

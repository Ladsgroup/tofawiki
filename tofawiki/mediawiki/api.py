"""A thin requests-based client for the MediaWiki Action API."""
import logging
import time
from typing import Any, Optional
from urllib.parse import urlencode

import requests

from .. import __version__
from .exceptions import APIError

logger = logging.getLogger(__name__)

# The Wikimedia cluster rejects requests that do not identify themselves.
USER_AGENT = (
    f'tofawiki/{__version__} '
    '(https://github.com/Ladsgroup/tofawiki; ladsgroup@gmail.com) '
    f'python-requests/{requests.__version__}'
)

# Above this many characters of query string, switch from GET to POST. Batches
# of 50 titles overflow the practical URL length otherwise.
POST_THRESHOLD = 1800

RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504})


class ApiClient:
    """Talks to one ``api.php`` endpoint."""

    def __init__(self, api_url: str, session: Optional[requests.Session] = None,
                 timeout: int = 30, max_retries: int = 3,
                 user_agent: str = USER_AGENT):
        self.api_url = api_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = session or requests.Session()
        # Must be assigned, not setdefault: Session ships with its own
        # User-Agent, and Wikimedia rejects the requests default with a 403.
        self.session.headers['User-Agent'] = user_agent

    def request(self, params: dict, use_post: Optional[bool] = None) -> dict[str, Any]:
        """Perform an API call and return the decoded JSON body.

        ``format`` and ``formatversion`` are filled in by the caller so that
        both the legacy (``*``-keyed) and the modern response shapes can be
        requested deliberately.
        """
        query = {k: v for k, v in params.items() if v is not None}
        query.setdefault('format', 'json')

        if use_post is None:
            use_post = len(urlencode(query)) > POST_THRESHOLD

        last_error: Optional[Exception] = None
        for attempt in range(self.max_retries):
            if attempt:
                delay = 2 ** attempt
                logger.warning('Retrying %s in %ss (%s)', self.api_url, delay, last_error)
                time.sleep(delay)
            try:
                if use_post:
                    response = self.session.post(self.api_url, data=query, timeout=self.timeout)
                else:
                    response = self.session.get(self.api_url, params=query, timeout=self.timeout)
            except requests.RequestException as e:
                last_error = e
                continue

            if response.status_code in RETRYABLE_STATUS:
                last_error = APIError('http', f'HTTP {response.status_code}')
                continue

            response.raise_for_status()
            try:
                data = response.json()
            except ValueError as e:
                last_error = e
                continue

            if 'error' in data:
                error = data['error']
                raise APIError(error.get('code', 'unknown'), error.get('info', ''))
            return data

        raise APIError('http', f'{self.api_url} failed after {self.max_retries} attempts: '
                               f'{last_error}')


class Request:
    """pywikibot-shaped wrapper: ``Request(site=site, **params).submit()``.

    Defaults to ``formatversion=1`` because the callers read the legacy
    ``'*'`` keys out of langlinks.
    """

    def __init__(self, site, **params):
        self.site = site
        self.params = params

    def submit(self) -> dict[str, Any]:
        params = dict(self.params)
        params.setdefault('formatversion', '1')
        return self.site.client.request(params)

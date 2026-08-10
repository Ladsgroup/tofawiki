"""A small requests-based MediaWiki client.

Replaces the pywikibot API surface this service used: sites, pages, Wikidata
items and raw Action API calls.
"""
from .api import ApiClient, Request
from .exceptions import APIError, IsRedirectPageError, MediaWikiError, NoPageError
from .page import Page
from .site import Site
from .textlib import extract_templates_and_params
from .wikibase import (
    Claim,
    Coordinate,
    FilePage,
    ItemPage,
    WbMonolingualText,
    WbQuantity,
    WbTime,
)

__all__ = [
    'APIError',
    'ApiClient',
    'Claim',
    'Coordinate',
    'FilePage',
    'IsRedirectPageError',
    'ItemPage',
    'MediaWikiError',
    'NoPageError',
    'Page',
    'Request',
    'Site',
    'WbMonolingualText',
    'WbQuantity',
    'WbTime',
    'extract_templates_and_params',
]

import re
import sys

import pywikibot
from pywikibot import ItemPage
from SPARQLWrapper import JSON, SPARQLWrapper


class WikidataTranslator:
    def __init__(self, repo, cache=None):
        self.repo = repo
        self.cache = cache
        self.endpoint_url = "https://query.wikidata.org/sparql"
        self.user_agent = "Tofawiki Python/%s.%s" % (sys.version_info[0], sys.version_info[1])

    def data2fa(self, number, strict=False, loose=False):
        if not number:
            return ''
        if isinstance(number, ItemPage):
            number = number.getID(True)
        cache_key = 'translate:fawiki:wikidatawiki:linktrans:'
        if strict:
            cache_key += 'strict:'
        else:
            cache_key += 'no_strict:'
        cache_key += str(number)
        if self.cache and self.cache.get_value(cache_key):
            return self.cache.get_value(cache_key)
        item_id = 'Q%d' % int(number)
        params = {
            'action': 'wbgetentities',
            'ids': item_id,
            'props': 'sitelinks|labels',
            'languages': 'fa|en'
        }
        query_res = pywikibot.data.api.Request(site=self.repo, **params).submit()['entities'][item_id]
        if query_res.get('sitelinks', {}).get('fawiki'):
            name = query_res['sitelinks']['fawiki']['title']
            if self.cache:
                self.cache.write_new_cache(cache_key, name)
            return name
        if strict:
            return ''
        if query_res.get('labels', {}).get('fa'):
            name = query_res['labels']['fa']['value']
            if self.cache:
                self.cache.write_new_cache(cache_key, name)
            return name
        if not loose:
            return ''
        if query_res.get('labels', {}).get('en'):
            name = query_res['labels']['en']['value']
            return name
        return ''

    def getRefferedItems(self, item, property_):
        res = []
        query = """SELECT ?item ?itemLabel
WHERE
{
  ?item wdt:""" + property_ + """ wd:"""+item.title()+""".
  SERVICE wikibase:label { bd:serviceParam wikibase:language "fa". }
}"""
        sparql = SPARQLWrapper(self.endpoint_url, agent=self.user_agent)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        result = []
        for case in [i['itemLabel']['value'] for i in sparql.query().convert()["results"]["bindings"]]:
            if re.search(r'^Q\d+$', case):
                continue
            result.append(case)
        return result

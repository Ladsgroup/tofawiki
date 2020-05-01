import re

import pywikibot

from tofawiki.util.translate_util import linker


class TextTranslator:
    def __init__(self, source, target, cache=None):
        self.source = source
        self.target = target
        self.cache = cache

    def seealsoer(self, text):
        re_see = re.compile(r"== *?[Ss]ee [Aa]lso *?==(.+?)==", re.DOTALL)
        res_see = re_see.findall(text)
        if not res_see:
            return ''
        re_see2 = re.compile(r"\* *?\[\[(.+?)(?:\||\]\])")
        text_see = "\n\n== جستارهای وابسته =="

        for line_see in re_see2.findall(res_see[0]):
            line_see2 = self.translator_taki(linker(line_see), True)
            if line_see2:
                text_see += "\n*" + line_see2
        if text_see == "\n\n== جستارهای وابسته ==":
            return ""
        return text_see

    def catadder(self, text):
        cats = u""
        res = self.link_translator(re.findall(r'\[\[([Cc]ategory:.+?)(?:\]\]|\|)', text))
        res = list(res.values())
        res.sort()
        for name in res:
            cats = cats + u"\n[[" + name + "]]"
        return cats

    def translator_taki(self, text, strict=False):
        b = text
        cache_prefix = 'translate:fawiki:enwiki:linktrans:'
        for name in re.findall("\[\[(.+?)(?:\||\]\])", text):
            if self.cache and self.cache.get_value(cache_prefix + name):
                res = self.cache.get_value(cache_prefix + name)
                b = re.sub(u"\[\[%s(?:\|.+?)?\]\]" %
                           re.escape(name), res, b)
            else:
                # TODO: Batch
                params = {
                    'action': 'query',
                    'redirects': '',
                    'titles': name,
                    'prop': 'langlinks',
                    'lllang': 'fa'
                }
                query_res = pywikibot.data.api.Request(site=self.source, **params).submit()['query']['pages']
                for page_id in query_res:
                    langlinks = query_res[page_id]['langlinks']
                if not langlinks:
                    continue
                fa_name = langlinks['*']
                if self.cache:
                    self.cache.write_new_cache(cache_prefix + name,
                                               linker(fa_name))
                return linker(fa_name)
        if strict:
            return ""
        return text

    def translator(self, text):
        if not text:
            return ''
        b = text
        names = re.findall("\[\[(.+?)(?:\||\]\])", text)
        res = self.link_translator(names)
        for name in names:
            if name in res:
                b = re.sub(u"\[\[%s(?:\|.+?)?\]\]" %
                           re.escape(name), linker(res[name]), b)
        return b

    def link_translator(self, batch):
        cache_prefix = 'translate:fawiki:enwiki:linktrans:'
        res = {}
        api_batch = []
        for name in batch:
            if self.cache and self.cache.get_value(cache_prefix + name):
                res[name] = self.cache.get_value(cache_prefix + name)
            else:
                api_batch.append(name)
        if not api_batch:
            return res

        api_res = {}
        for chunk in self.chunks(api_batch, 50):
            api_res.update(self.link_translator_api(chunk))

        for case in api_res:
            if self.cache:
                self.cache.write_new_cache(cache_prefix + case, api_res[case])
            if case in batch:
                res[case] = api_res[case]

        return res

    def link_translator_api(self, batch):
        """Note: batch size shouldn't exceed 50"""
        params = {
            'action': 'query',
            'redirects': '',
            'titles': '|'.join(batch)
        }
        query_res = pywikibot.data.api.Request(site=self.source, **params).submit()
        redirects = {i['from']: i['to'] for i in query_res['query'].get('redirects', [])}
        normalizeds = {i['from']: i['to'] for i in query_res['query'].get('normalized', [])}

        # Resolve normalized redirects and merge normalizeds dict into redirects at the same time
        for k, v in normalizeds.items():
            redirects[k] = redirects.get(v, v)

        wikidata = pywikibot.Site('wikidata', 'wikidata')

        params = {
            'action': 'wbgetentities',
            'sites': self.source.dbName(),
            'titles': '|'.join([redirects.get(i, i) for i in batch]),
            'props': 'sitelinks'
        }

        try:
            query_res = pywikibot.data.api.Request(site=wikidata, **params).submit()
        except:
            return {}

        matches_titles = {}
        entities = query_res.get('entities', {})
        endbName = self.source.dbName()
        fadbName = self.target.dbName()
        for qid, entity in entities.items():
            if fadbName in entity.get('sitelinks', {}):
                en_title = entity['sitelinks'][endbName]
                fa_title = entity['sitelinks'][fadbName]

                # for not updated since addition of badges on Wikidata items
                if not isinstance(en_title, str):
                    en_title = en_title['title']
                    fa_title = fa_title['title']

                matches_titles[en_title] = fa_title

        res = {}
        for i in batch:
            p = redirects[i] if (i in redirects) else i
            if p in matches_titles:
                if i in redirects:
                    res[p] = matches_titles[p]
                res[i] = matches_titles[p]

        return res

    @staticmethod
    def chunks(l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i + n]

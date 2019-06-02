from pywikibot import ItemPage, pagegenerators


class WikidataTranslator:
    def __init__(self, repo, cache=None):
        self.repo = repo
        self.cache = cache

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
        item = ItemPage(self.repo, 'Q%d' % int(number))
        try:
            item.get()
        except:
            return ''
        if isinstance(item.sitelinks, list):
            item.sitelinks = {}
        if 'fawiki' in item.sitelinks:
            name = item.sitelinks['fawiki']
            if self.cache:
                self.cache.write_new_cache(cache_key, name)
            return name
        if strict:
            return ''
        if isinstance(item.labels, list):
            item.labels = {}
        if 'fa' in item.labels:
            name = item.labels['fa']
            if self.cache:
                self.cache.write_new_cache(cache_key, name)
            return name
        if not loose:
            return ''
        try:
            return item.labels['en']
        except:
            return ''

    def getRefferedItems(self, item, property):
        gen = pagegenerators.ReferringPageGenerator(item)
        pregen = pagegenerators.PreloadingGenerator(gen)
        refs = []
        for page in pregen:
            if page.namespace() != 0:
                continue
            try:
                page.get()
                target_item = ItemPage(self.repo, page.title())
                target_item.get()
            except:
                continue
            if property not in target_item.claims:
                continue
            for claim in target_item.claims[property]:
                if not claim.getTarget():
                    continue
                if claim.getTarget().getID() == item.getID():
                    res = self.data2fa(int(target_item.title().replace("Q", '')))
                    if res:
                        refs.append(res)

        return refs

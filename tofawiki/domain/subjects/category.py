import traceback
from collections import defaultdict

import pywikibot
from pywikibot.textlib import extract_templates_and_params

from tofawiki.cache.redis_cache import RedisCache
from tofawiki.domain.subjects.subject import Subject
from tofawiki.domain.text_translator import TextTranslator
from tofawiki.domain.wikidata_translator import WikidataTranslator


class CatergorySubject(Subject):
    def __init__(self, service):
        """

        :type service: tofawiki.services.translation.translate.Translate
        """
        self.cache = RedisCache(service.config['cache']['redis_cache'])
        self.text_translator = TextTranslator(service.site,
                                              pywikibot.Site('fa'), self.cache)
        self.wikidata_translator = WikidataTranslator(service.site.data_repository(),
                                                      self.cache)
        self.service = service
        self.info = defaultdict(list)
        self.breaks = '\n\n'

    def get_lead(self):
        enwiki_lead = self.service.article.text.split("\n==")[0]
        text = ''
        for i in extract_templates_and_params(enwiki_lead, None, strip=True):
            title = i[0]
            if title.startswith('Template:'):
                title = title[len('Template:'):]
            text += self.text_translator.translator_taki('[[Template:' + title + ']]') + '\n'
        return text.replace('[[الگو:', '{{').replace(']]', '}}')

    def extract_info(self):
        for property_number in self.service.item.claims:
            for claim in self.service.item.claims[property_number]:
                self.info[int(property_number.split('P')[1])].append(claim.getTarget())

    def get_infobox(self):
        return ''

    def get_translation(self):
        try:
            self.extract_info()
            content = self.get_lead() + self.breaks + self.get_footer()
        except:
            return {
                'error': 'Unable to translate. Copy paste this for Amir: ' + traceback.format_exc()
            }
        return {'page_content': content}

    def get_footer(self):
        enpage = self.service.article
        entext = enpage.get()
        text = ''

        if self.info[373]:
           text += u"{{انبار-رده}}\n"
        if self.info[301]:
            text += "{{اصلی رده}}\n"

        text = text + self.text_translator.catadder(entext)
        return text + self.breaks + u"[[en:%s]]" % enpage.title()

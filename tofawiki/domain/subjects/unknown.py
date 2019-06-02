import re
import traceback
from collections import OrderedDict, defaultdict

import pywikibot
from jinja2 import Template
from pywikibot.textlib import extract_templates_and_params

from tofawiki.cache.redis_cache import RedisCache
from tofawiki.domain.subjects.subject import Subject
from tofawiki.domain.text_translator import TextTranslator
from tofawiki.domain.wikidata_translator import WikidataTranslator
from tofawiki.util.translate_util import dater, get_lang, sortcat


class UnknownSubject(Subject):
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
        self.breaks = '\n\n'
        self.info = defaultdict(list)
        self.infobox = OrderedDict()
        self.stub_type = 'موضوع'
        self.infobox_title = ''
        self.infobox_exceptions = ['embed']

    def get_lead(self):
        lang = get_lang(
            self.service.article.text.split("\n==")[0],
            self.service.article.title().split(" (")[0])
        template = Template("'''{{ fa_name }}''' ({{ lang }})")
        return template.render(
            fa_name=self.service.faname.split(' (')[0],
            lang=lang)

    def get_infobox(self):
        res = ''
        if self.infobox_title:
            res += '{{' + self.infobox_title
        if self.infobox:
            for i in self.infobox:
                i_test = i.replace('\n', '').replace('\t', '').strip()
                if i_test not in self.infobox_exceptions:
                    res += u"\n| " + i + u" = " + self.infobox[i]
            res += '\n}}'
        return self.text_translator.translator(res)

    def get_stub_type(self):
        return self.stub_type

    def get_translation(self):
        try:
            self.extract_infobox()
            self.run_infobox_fixes()
            content = self.get_infobox() + '\n' + self.get_lead() + self.breaks + self.get_footer()
        except:
            return {
                'error': 'Unable to translate. Copy paste this for Amir: ' + traceback.format_exc()
            }
        return {'page_content': self.run_fixes(content)}

    def get_footer(self):
        authority_controls = [214, 244, 213, 496, 227, 906, 269, 268, 651, 1053,
                              1015, 245, 902, 886, 434, 549, 409, 349, 1048, 691,
                              640, 396, 947, 428, 1222, 1223, 1157, 950, 271, 1362,
                              781, 1248, 650]
        enpage = self.service.article
        entext = enpage.get()
        faname = self.service.faname
        text = self.text_translator.seealsoer(entext)
        text += self.breaks + u"== منابع ==\n{{پانویس|چپ‌چین=بله}}"
        url = enpage.permalink().replace("&useskin=monobook", "")
        text += u"\n*{{یادکرد-ویکی|پیوند =" + url + \
                u"|عنوان = " + enpage.title().replace(u"_", u" ") + \
                u"|زبان =انگلیسی|بازیابی ={{جا:الان|پیوند=نه}}}}\n"

        if (self.info[373] or self.info['twitter'] or self.info['facebook'] or
                self.info['official'] or 434 in self.info):
            if self.info[373]:
                text += u"\n{{-}}\n"
            text += u"\n== پیوند به بیرون ==\n"
            if self.info[373]:
                text += u"{{انبار-رده}}\n"
            if self.info['official']:
                text += u"* {{رسمی|" + self.info['official'] + u"}}\n"
            if self.info['imdb']:
                text += u"* {{IMDb name|" + self.info['imdb'] + u"}}\n"
            if self.info['facebook']:
                text += u"* {{facebook|" + self.info['facebook'] + u"}}\n"
            if self.info['twitter']:
                text += u"* {{twitter|" + self.info['twitter'] + u"}}\n"
        if self.info['coord']:
            text += self.info['coord'][0] + "\n"
        for i in self.info:
            if i in authority_controls:
                text += "{{داده‌های کتابخانه‌ای}}\n"
                break
        text += u"\n{{" + self.get_stub_type() + "-خرد}}" + self.breaks
        text = text + sortcat(entext,
                              enpage.title().split(" (")[0], faname.split(" (")[0])
        text = text + self.text_translator.catadder(entext)
        return text + self.breaks + u"[[en:%s]]" % enpage.title()

    @staticmethod
    def run_fixes(text):
        final_fixes = {u"]], ": u"]]، ",
                       u"]] and [[": u"]] و [[",
                       u"]], and [[": u"]]، و [[", }
        for fix in final_fixes:
            text = text.replace(fix, final_fixes[fix])
        return text

    def extract_info(self):
        for property_number in self.service.item.claims:
            for claim in self.service.item.claims[property_number]:
                self.info[int(property_number.split('P')[1])].append(claim.getTarget())

    def extract_infobox(self):
        self.extract_info()
        # TODO: strip doesn't work in pywikibot 2.0rc5. We need to use master
        for i in extract_templates_and_params(self.service.article.text, None, strip=True):
            if not self.infobox and "infobox" in i[0].lower():
                self.infobox_title = i[0]
                for case in i[1]:
                    if case.strip() in self.infobox:
                        continue
                    if re.search(r'^\d+$', case):
                        continue
                    arg = i[1][case]
                    self.infobox[case.strip()] = arg
            if "twitter" in i[0].lower():
                if '1' in i[1]:
                    self.info['twitter'] = i[1]['1']
            if i[0].lower() == 'coord':
                if 'title' in i[1].get('display', 'title'):
                    coord = re.findall(r"({{[Cc]oord *?\|.+?\}\})", self.service.article.text)
                    if coord and "{{" not in coord[0]:
                        self.info['coord'] = coord
            if "imdb name" in i[0].lower():
                if '1' in i[1]:
                    self.info['imdb'] = i[1].get('id', "")
            if "facebook" in i[0].lower():
                if '1' in i[1]:
                    self.info['facebook'] = i[1]['1']
            if i[0].lower().startswith("official"):
                if '1' in i[1]:
                    self.info['official'] = i[1]['1']
            if "youtube" in i[0].lower():
                if '1' in i[1]:
                    self.info['youtube'] = i[1]['1']

    def run_infobox_fixes(self):
        for case in self.infobox:
            if case in ['name', 'title']:
                self.infobox[case] = self.service.faname
            if re.search("term_?(?:start|end)\d*", case):
                self.infobox[case] = dater(self.infobox[case])

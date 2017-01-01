import pywikibot
import traceback
import re

from .subject import Subject
from ....cache.file_cache import FileCache
from ....util.translate_util import seealsoer, sortcat, catadder, dater, translator

from jinja2 import Template
from collections import defaultdict, OrderedDict

class UnknownSubject(Subject):
    def __init__(self, service):
        self.cache = FileCache(service.config['cache']['path'])
        self.service = service
        self.breaks = '\n\n'
        self.info = defaultdict(list)
        self.infobox = OrderedDict()

    def get_lead(self):
        template = Template("'''{{ fa_name }}''' ({% raw %}{{lang-en|{% endraw %}{{en_name}}{% raw %}}}{% endraw %})")
        return template.render(
            fa_name=self.service.faname.split(' (')[0],
            en_name=self.service.article.title())

    def get_infobox(self):
        res = ''
        for i in pywikibot.extract_templates_and_params(self.service.article.text, strip=True):
            if not self.infobox and "infobox" in i[0].lower():
                for case in i[1]:
                    if case.strip() in self.infobox:
                        continue
                    arg = i[1][case]
                    if re.search("term_?(?:start|end)\d*", case):
                        arg = dater(arg)
                    self.infobox[case.strip()] = arg
            if "twitter" in i[0].lower():
                if '1' in i[1]:
                    self.info['twitter'] = i[1]['1']
            if i[0].lower() == 'coord':
                if 'title' in i[1].get('display', 'title'):
                    coord = re.findall(r"(\{\{[Cc]oord *?\|.+?\}\})", self.service.article.text)
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

        for i in self.infobox:
            res += u"\n| " + i + u" = " + self.infobox[i]
        return translator(res)

    def get_stub_type(self):
        return 'موضوع'

    def get_translation(self):
        try:
            content = self.get_lead() + self.breaks + self.get_footer()
        except:
            return {'error': 'Unable to translate. Copy paste this for Amir: ' + traceback.format_exc()}
        return {'page_content': self.run_fixes(content)}

    def get_footer(self):
        # TODO:Refactor for bacthing of linktranslator
        enpage = self.service.article
        entext = enpage.get()
        faname = self.service.faname
        fasite = pywikibot.Site('fa')
        text = seealsoer(entext, enpage.site, fasite, self.cache)
        text += u"\n\n== منابع ==\n{{پانویس|چپ‌چین=بله}}"
        text += u"\n*{{یادکرد-ویکی|پیوند =" + enpage.permalink().replace("&useskin=monobook", "") + \
               u"|عنوان = " + enpage.title().replace(u"_", u" ") + \
               u"|زبان =انگلیسی|بازیابی ={{جا:الان|پیوند=نه}}}}"
        self.extract_info()

        if self.info[373] or self.info['twitter'] or self.info['facebook'] or self.info['official'] or 434 in self.info:
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
        text += u"\n\n{{موضوع-خرد}}\n"
        if self.info['coord']:
            text += self.info['coord'][0] + "\n"
        text = text + sortcat(entext,
                              enpage.title().split(" (")[0], faname.split(" (")[0])
        text = text + catadder(entext, enpage.site)
        return text + u"\n\n[[en:%s]]" % enpage.title()

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
                self.info[int(property_number.split('P'))].append(claim.getTarget())
import pywikibot

from .subject import Subject
from ....cache.file_cache import FileCache
from ....util.translate_util import seealsoer, sortcat

from jinja2 import Template


class UnknownSubject(Subject):
    def __init__(self, service):
        self.cache = FileCache(service.config['cache']['path'])
        self.service = service
        self.breaks = '\n\n'

    def get_lead(self):
        template = Template("'''{{ fa_name }}''' ({% raw %}{{lang-en|{% endraw %}{{en_name}}{% raw %}}}{% endraw %})")
        return template.render(
            fa_name=self.service.faname.split(' (')[0],
            en_name=self.service.article.title())

    def get_infobox(self):
        return ''

    def get_stub_type(self):
        return 'موضوع'

    def get_translation(self):
        return {'page_content': self.get_lead() + self.breaks + self.get_footer()}

    def get_footer(self):
        #TODO:Refactor for bacthing of linktranslator
        enpage = self.service.article
        entext = enpage.get()
        faname = self.service.faname
        fasite = pywikibot.Site('fa')
        text = seealsoer(entext, enpage.site, fasite, self.cache)
        text = text + u"\n\n== منابع ==\n{{پانویس|چپ‌چین=بله}}"
        text = text + u"\n*{{یادکرد-ویکی|پیوند =" + enpage.permalink().replace("&useskin=monobook", "") + \
               u"|عنوان = " + enpage.title().replace(u"_", u" ") + \
               u"|زبان =انگلیسی|بازیابی ={{جا:الان|پیوند=نه}}}}"
        return text
        if info[373] or twitter or facebook or official or 434 in info:
            if info[373]:
                text = text + u"\n{{-}}\n"
            text = text + u"\n== پیوند به بیرون ==\n"
            if info[373]:
                text = text + u"{{انبار-رده}}\n"
            if official:
                text = text + u"* {{رسمی|" + official + u"}}\n"
            if imdb:
                text = text + u"* {{IMDb name|" + imdb + u"}}\n"
            if facebook:
                text = text + u"* {{facebook|" + facebook + u"}}\n"
            if twitter:
                text = text + u"* {{twitter|" + twitter + u"}}\n"
        text = text + u"\n\n{{موضوع-خرد}}\n"
        if coord:
            text += coord[0] + "\n"
        text = text + sortcat(entext,
                              enpage.title().split(" (")[0], faname.split(" (")[0])
        text = text + catsss
        for fix in final_fixes:
            text = text.replace(fix, final_fixes[fix])
        return text + u"\n\n[[en:%s]]" % enpage.title()
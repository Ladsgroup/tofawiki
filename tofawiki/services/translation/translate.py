import re

from tofawiki.domain.subjects.category import CatergorySubject
from tofawiki.domain.subjects.human import HumanSubject
from tofawiki.domain.subjects.unknown import UnknownSubject

from ...mediawiki import ItemPage, Page, Site
from ...mediawiki.exceptions import IsRedirectPageError, NoPageError
from ...services.service import Service


class Translate(Service):
    def __init__(self, wiki, article, faname, config):
        self.wiki = wiki
        self.site = Site(config[wiki]['code_lang'])
        self.article = Page(self.site, article)
        self.faname = self.normalize_fa(faname)
        self.config = config
        self.item = None

    def validate(self):
        fapage = Page(Site('fa'), self.faname)
        try:
            fapage.get()
        except NoPageError:
            pass
        except IsRedirectPageError:
            return {'error': 'Article in Perisan Wikipedia exist'}
        else:
            return {'error': 'Article in Perisan Wikipedia exist'}
        if self.article.isRedirectPage():
            self.article = self.article.getRedirectTarget()
            # Just once for goodness sake
            if self.article.isRedirectPage():
                self.article = self.article.getRedirectTarget()

        try:
            self.article.get()
        except NoPageError:
            return {'error': 'Article in English Wikipedia does not exist'}
        try:
            self.item = ItemPage.fromPage(self.article)
            self.item.get()
        except NoPageError:
            return {'error': 'The item in Wikidata does not exist'}

        return True

    def run(self):
        res = self.validate()
        if res is not True:
            return res
        self.subject = self.get_subject_callback()(self)
        return self.subject.get_translation()

    def get_subject_callback(self):
        if self.article.namespace() == 14:
            return CatergorySubject
        instances = self.get_instances()
        if 5 in instances or 'infobox person' in self.article.text.lower():
            return HumanSubject
        return UnknownSubject

    @staticmethod
    def normalize_fa(faname):
        return re.sub(r"([‌۱۲۳۴۵۶۷۸۹۰\)\(ادذرزژو])‌", "\1", faname).replace(
            "ي", "ی").replace("ك", "ک")

    def get_instances(self):
        res = []
        for claim in self.item.claims.get('P31', []):
            try:
                res.append(int(claim.getTarget().getID().split('Q')[1]))
            except Exception:
                continue
        return res

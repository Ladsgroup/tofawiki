import re

from tofawiki.domain.subjects.unknown import UnknownSubject
from tofawiki.util.translate_util import (FA_LETTERS, dater, en2fa, get_lang,
                                          khoshgeler, linker, officefixer)

BIRTH_DATE = 'birth_date'
DEATH_DATE = 'death_date'
OCCUPATION = 'occupation'


class HumanSubject(UnknownSubject):
    def __init__(self, service):
        super().__init__(service)
        self.stub_type = 'افراد'
        self.medals = [u'۰', u'۰', u'۰']
        self.national_teams = []
        self.clubs = ''
        self.awards = ''
        self.awards2 = ''
        self.infobox_title = ''
        self.occupation = ''

    def get_lead(self):
        occu_fixes = {
            u"[[اختراع]]": u"[[اختراع|مخترع]]",
            u"[[داستان کوتاه]]": u"نویسنده [[داستان کوتاه]]",
            u"[[میلیاردره]]": u"[[میلیاردر]]",
        }
        lang = get_lang(self.service.article.text.split("\n==")[0],
                        self.service.article.title().split(" (")[0])
        text = "'''" + self.service.faname.split(" (")[0] + u"''' (" + lang + u"؛ "
        if not self.infobox.get(DEATH_DATE, '').strip():
            text += u"زادهٔ "
        birth_date = self.infobox.get(BIRTH_DATE, '')
        if u"}}" in birth_date.replace("birth date and age", "birth date"):
            text += "}}".join(
                birth_date.lower().replace(
                    "birth date and age", "birth date").split(
                        "}}")[:])
        else:
            text += birth_date.replace("birth date and age", "birth date")
        death_date = self.infobox.get(DEATH_DATE, '')
        if death_date:
            text += u" – "
            if u"}}" in death_date.replace("death date and age", "death date"):
                text += "}}".join(death_date.lower().replace(
                    "death date and age", "death date").split(
                        "}}")[:])
            else:
                text = text + \
                    death_date.replace("death date and age", "death date")
        self.occupation = self.occupation.strip()
        if not self.occupation and u"امپراتور" in self.service.faname:
            self.occupation = u"امپراتور"
        if self.occupation.count("[") > self.occupation.count("]"):
            self.occupation += u"]"
        for fix in occu_fixes:
            self.occupation = self.occupation.replace(fix, occu_fixes[fix])
        text = text + u") " + self.occupation
        if self.infobox.get('nationality'):
            text += u" اهل " + self.infobox['nationality']
        if not self.infobox.get(DEATH_DATE, '').strip():
            text += u" است. "
        else:
            text += u" بود. "
        years_active = self.infobox.get('years_active', '').strip()
        if years_active and u"–" in years_active:
            startyear = years_active.split(u"–")[0]
            endyear = years_active.split(u"–")[1]
            if len(startyear) == 4 and (len(endyear) == 4 or endyear == u"اکنون"):
                text += u"وی "
                if endyear == u"اکنون":
                    text += u"از سال " + startyear + \
                        u" میلادی تاکنون مشغول فعالیت بوده‌است. "
                else:
                    text += u"بین سال‌های " + startyear + \
                        u" تا " + endyear + u" میلادی فعالیت می‌کرد."
        text = text + self.films()
        if self.awards:
            text += self.breaks + "وی همچنین برندهٔ جوایزی همچون " + \
                khoshgeler(self.awards) + u" شده است."
        elif self.awards2:
            text += self.breaks + u" همچنین برندهٔ جوایزی همچون " + \
                self.awards2 + u" شده است."
        if self.clubs:
            text += self.breaks + u"از باشگاه‌هایی که در آن بازی کرده‌است می‌توان به " + \
                khoshgeler(re.sub(r'\[\[تیم ملی.+?\]\]', '', self.clubs)) + u" اشاره کرد."
        if self.national_teams:
            national_teams_text = ''
            if len(self.national_teams) == 1:
                national_teams_text += u"\n\nوی همچنین در تیم ملی فوتبال " + \
                    self.national_teams[0] + u" بازی کرده است."
            else:
                national_teams_text += self.breaks + u"وی همچنین در تیم‌های ملی فوتبال " + \
                   khoshgeler(' '.join(self.national_teams)) + u" بازی کرده است."
            national_teams_text = self.text_translator.translator(national_teams_text)
            national_teams_text = re.sub(r'\[\[تیم ملی فوتبال (.+?)\]\]',
                                         r'[[تیم ملی فوتبال \1|\1]]',
                                         national_teams_text)
            text += national_teams_text
        if self.medals != [u'۰', u'۰', u'۰']:
            text += self.breaks + u'وی در مسابقات کشوری و بین‌المللی در مجموع برندهٔ '
            if self.medals[0] != u'۰':
                text += self.medals[0] + u' [[مدال طلا]]، '
            if self.medals[1] != u'۰':
                text += self.medals[1] + u' [[مدال نقره]]، '
            if self.medals[2] != u'۰':
                text += self.medals[2] + u' [[مدال برنز]]، '
            text = text[:-2] + u' شده‌است.'

        return text

    def run_infobox_fixes(self):
        self.infobox['name'] = self.service.faname.split(' (')[0]
        old_image = self.infobox.get('image')
        self.run_wikidata_fix("image", 18)
        if old_image != self.infobox.get('image'):
            self.infobox['caption'] = ''
        if not self.infobox.get(BIRTH_DATE):
            self.run_wikidata_fix(BIRTH_DATE, 569)
        self.run_wikidata_fix("birth_place", 19)
        self.run_wikidata_fix("sport", 641)
        if not self.infobox.get(DEATH_DATE):
            self.run_wikidata_fix(DEATH_DATE, 570)
        self.run_wikidata_fix("death_place", 20)
        self.run_wikidata_fix("nationality", 27)
        occupation = ''
        long_occupation = ''
        awardstext = ''
        if re.search(
                r"(sportsperson|swim|football|soccer|rugby|tennis|cyclist|"
                r"f1 driver|baseball|basketball| mlb| nba)",
                self.infobox_title.lower()):
            self.run_sport_fixes()
        else:
            for case in self.infobox:
                if re.search("term_?(?:start|end)\d*", case):
                    self.infobox[case] = dater(self.infobox[case])
                if "order" in case:
                    self.infobox[case] = en2fa(
                        re.sub(r"(\d+?)(th|st|nd|rd)", r"\1مین", self.infobox[case]))
                elif "office" in case:
                    self.infobox[case] = en2fa(
                        re.sub(r"(\d+?)(th|st|nd|rd)", r"\1مین", officefixer(self.infobox[case])))
                if case == "reign":
                    self.infobox[case] = dater(self.infobox[case])
                elif "succession" in case:
                    en_office = self.infobox[case]
                    self.infobox[case] = officefixer(en_office)
                    if self.infobox[case] != en_office:
                        long_occupation = self.infobox[case]
                if re.search(r'award|prize', case.lower()):
                    for awname in re.findall(r"\[\[(.+?)(?:\||\]\])", self.infobox[case]):
                        awardstext += u"[[" + awname + u"]]"

        self.date_cleaner(BIRTH_DATE)
        self.date_cleaner(DEATH_DATE)
        if "music" in self.infobox_title.lower():
            long_occupation = u"موسیقی‌دان"
            occupation = u"موسیقی‌دان"
        elif "military person" in self.infobox_title.lower():
            long_occupation = u"فرد نظامی"
            occupation = u"فرد نظامی"
        elif "officeholder" in self.infobox_title.lower():
            long_occupation = u"سیاست‌مدار"
            occupation = u"سیاست‌مدار"
        elif re.search(
                r"(sportsperson|swim|football|soccer|rugby|tennis|cyclist|"
                r"f1 driver|baseball|basketball| mlb| nba)",
                self.infobox_title.lower()):
            long_occupation = u"ورزشکار"
            occupations = {
                u"basketball": u"بازیکن بسکتبال",
                u" nba": u"بازیکن بسکتبال",
                u"football": u"بازیکن فوتبال",
                u" mlb": u"بازیکن بیس‌بال",
                u"baseball": u"بازیکن بیس‌بال",
                u"f1 driver": u"اتومبیل‌ران فرمول ۱",
                u"cyclist": u"دوچرخه‌سوار",
                u"tennis": u"تنیس‌باز"}
            for i in occupations:
                if i in self.infobox_title.lower():
                    long_occupation = linker(occupations[i])
                    occupation = occupations[i]
            if long_occupation == u"ورزشکار" and self.infobox.get('sport'):
                long_occupation = u"ورزشکار " + linker(self.infobox['sport'])
        elif "adult biography" in self.infobox_title.lower():
            long_occupation = u"بازیگر پورنوگرافی"
            occupation = u"بازیگر پورنوگرافی"
        elif " saint" in self.infobox_title.lower():
            long_occupation = u"قدیس مسیحی"
            occupation = u"قدیس مسیحی"
        elif "scientist" in self.infobox_title.lower():
            long_occupation = u"دانشمند"
            occupation = u"دانشمند"
            fields = []
            if 101 in self.info:
                fields = [
                    linker(self.wikidata_translator.data2fa(self.info[101][0]))
                ]
            if not fields:
                fields = [self.text_translator.translator(self.infobox.get('field', ''))]
            if fields:
                long_occupation += u" در زمینه " + khoshgeler(fields[0])

        if OCCUPATION in self.infobox:
            if '[[' not in self.infobox[OCCUPATION]:
                linked = '[[' + self.infobox[OCCUPATION].replace(', ', ']], [[') + ']]'
                self.infobox[OCCUPATION] = self.text_translator.translator(linked)
                long_occupation = self.infobox[OCCUPATION]

        if not long_occupation or not re.search(FA_LETTERS, long_occupation):
            long_occupation = self.occu(self.info[106], occupation)

        awards = u""
        if 166 in self.info:
            awards_list = []
            for i in self.info[166]:
                award = self.wikidata_translator.data2fa(i)
                if award:
                    awards_list.append(linker(award))
            # Clean up duplicates
            awards_list = list(set(awards_list))
            awards = " ".join(awards_list).strip()
        clubs = u""
        if 54 in self.info:
            clubs_list = []
            for i in self.info[54]:
                club = self.wikidata_translator.data2fa(i)
                if club:
                    clubs_list.append(linker(club))
            clubs = " ".join(list(set(clubs_list))).strip()
        awardstext2 = ''
        awardstext = self.text_translator.translator(awardstext)
        for awname in re.findall(r"\[\[(.+?)(?:\||\]\])", awardstext):
            if re.search(u"نشان|جایزه|مدال", awname):
                awardstext2 += linker(awname)
        awardstext2 = khoshgeler(awardstext2)

        if self.infobox.get('years_active'):
            self.infobox['years_active'] = en2fa(
                self.infobox['years_active']).replace("present", u"اکنون")
        if self.info.get('official'):
            self.infobox['official'] = self.info['official']
        if 109 in self.info:
            self.infobox['signature'] = self.info[109][0].title(
                underscore=True, withNamespace=False)

        if not self.infobox_title:
            self.infobox_title = "infobox person"

        if self.infobox.get(BIRTH_DATE) and isinstance(self.infobox[BIRTH_DATE], list):
            self.infobox[BIRTH_DATE] = en2fa(self.infobox[BIRTH_DATE][0])
        if self.infobox.get(DEATH_DATE) and isinstance(self.infobox[DEATH_DATE], list):
            self.infobox[DEATH_DATE] = en2fa(self.infobox[DEATH_DATE][0])
        if not self.infobox.get(BIRTH_DATE, '').strip():
            yearfa = re.findall(r"\[\[Category:(\d+?) births\]\]", self.service.article.text)
            if yearfa:
                self.infobox[BIRTH_DATE] = en2fa(yearfa[0])
        if not self.infobox.get(DEATH_DATE, '').strip():
            yearfa = re.findall(r"\[\[Category:(\d+?) deaths\]\]", self.service.article.text)
            if yearfa:
                self.infobox[DEATH_DATE] = yearfa[0]

        if not long_occupation.strip() and occupation.strip():
            long_occupation = self.text_translator.translator(occupation)
        if long_occupation.strip():
            self.occupation = long_occupation
        if occupation.strip():
            self.stub_type = occupation
        elif (long_occupation.strip() and '[[' in long_occupation and
                re.search(FA_LETTERS, long_occupation.split('[[')[1].split(']]')[0])):
            self.stub_type = long_occupation.split('[[')[1].split(']')[0]
        self.clubs = clubs
        self.awards = awards
        self.awards2 = awardstext2

    def run_sport_fixes(self):
        for case in self.infobox:
            if case.strip().endswith("update"):
                self.infobox[case] = dater(self.infobox[case])
            if case.lower() == 'playingstyle':
                self.infobox[case] = re.sub(r'[Rr]ight-?handed', 'راست‌دست', self.infobox[case])
                self.infobox[case] = re.sub(r'[Rr]ight-?handed', 'چپ‌دست', self.infobox[case])
            self.infobox[case] = self.infobox[case].replace(u"(loan)", u"(قرضی)")
            if self.infobox[case].strip().startswith('→'):
                self.infobox[case] = self.infobox[case].replace('→', '←')
            self.infobox[case] = re.sub(
                r"\[\[(تیم ملی فوتبال )(?:زنان )?(.+?)\]\]", r"[[\1\2|\2]]", self.infobox[case])
            self.infobox[case] = re.sub(
                r"\[\[(باشگاه فوتبال )(?:زنان )?(.+?)\]\]", r"[[\1\2|\2]]", self.infobox[case])
            if re.findall("(?:national|youth)?(?:years|caps|goals)\d\d?", case):
                self.infobox[case] = en2fa(self.infobox[case])
            self.infobox[case] = re.sub(
                r'(\{\{ *?Medal(?:Gold|Silver|Bronze) *?\|(.+?)\| *?)[tT]eam',
                r'\1تیمی',
                self.infobox[case])
            self.infobox[case] = re.sub(
                r'(\{\{ *?Medal(?:Gold|Silver|Bronze) *?\|(.+?)\| *?)[Ss]ingles',
                r'\1تک‌نفره',
                self.infobox[case])
            self.infobox[case] = re.sub(
                r'(\{\{ *?Medal(?:Gold|Silver|Bronze) *?\|(.+?)\| *?)[Dd]oubles',
                r'\1دونفره',
                self.infobox[case])
            if re.search(r'nationalteam\d*?', case):
                if self.infobox[case].strip() and 'update' not in case:
                    self.national_teams.append(self.infobox[case])

        values = ' '.join(self.infobox.values())
        medals = [
            en2fa(len(re.findall(r'\{\{ *?MedalGold', values))),
            en2fa(len(re.findall(r'\{\{ *?MedalSilver', values))),
            en2fa(len(re.findall(r'\{\{ *?MedalBronze', values)))]
        self.medals = medals

    def date_cleaner(self, name):
        if self.infobox.get(name) and self.infobox[name][0] == "0":
            clean_date = self.infobox[name].split("T")[0][7:]
            if clean_date.count('-') != 2:
                return
            if name.startswith('birth'):
                self.infobox[name] = '{{Birth date|'
            else:
                self.infobox[name] = '{{Death date|'
            self.infobox[name] += clean_date.replace('-', '|') + '}}'

    def run_wikidata_fix(self, name, wd_id):
        if self.info[wd_id]:
            self.infobox[name] = ''
            if wd_id == 18:
                self.infobox[name] = self.info[wd_id][0].title(underscore=True, withNamespace=False)
            elif wd_id in [569, 570]:
                self.infobox[name] = self.info[wd_id][0].toTimestr()[1:].split('T')[0]
            else:
                res = self.wikidata_translator.data2fa(self.info[wd_id][0], strict=True)
                if not res:
                    return
                self.infobox[name] = linker(res)

    def films(self):
        filmsandseries = self.wikidata_translator.getRefferedItems(self.service.item, 'P161')
        explanation = u"از فیلم‌ها یا برنامه‌های تلویزیونی که وی در آن نقش داشته است می‌توان به "
        film_text = self.breaks + explanation + " اشاره کرد."
        text = u''
        if filmsandseries:
            text = self.breaks + explanation
            films_count = 0
            for i in filmsandseries:
                if i:
                    films_count += 1
                    text += "''" + linker(i) + u"''، "
            if films_count > 2:
                text = ']]''، و '.join(text[:-2].rsplit("]]''، ", 1))
            else:
                text = text[:-2]
            text += u" اشاره کرد."
        if not text == film_text:
            return text
        return u''

    def occu(self, a, b):
        listoc = []
        if a:
            for i in a:
                ff = self.wikidata_translator.data2fa(i)
                if ff:
                    listoc.append(ff)
        if not listoc:
            links = self.text_translator.translator(u"[[" + b.replace(", ", u"]][[") + u"]]")
            for i in re.findall("\[\[(.+?)(?:\]\]|\|)", links):
                if re.search(FA_LETTERS, i):
                    if i:
                        listoc.append(i)
        textg = ''
        try:
            fff = listoc[-2]
        except IndexError:
            fff = None
        for i in listoc:
            textg += u"[[" + i + u"]]، "
            if i == fff:
                textg += u"و "
        if textg.count(u"،") == 1:
            textg = textg.replace(u"،", u"")
        return textg[:-2] + u" "

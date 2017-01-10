import re
import pywikibot

# Disclaimer: This codes are super old and creepy, we need to rewrite them altogether

months = {"January": u"ژانویه",
          "February": u"فوریه",
          "March": u"مارس",
          "April": u"آوریل",
          "May": u"مه",
          "June": u"ژوئن",
          "July": u"ژوئیه",
          "August": u"اوت",
          "September": u"سپتامبر",
          "October": u"اکتبر",
          "November": u"نوامبر",
          "December": u"دسامبر"}


def linker(a):
    if not a:
        return a
    if u"[[" in a:
        return a
    if "(" in a:
        return u"[[" + a + u"|]]"
    return u"[[%s]]" % a


def khoshgeler(a):
    if not a:
        return a
    rerkhosh = re.compile("\[\[(.+?)(?:\]\]|\|)")
    textg = u""
    listoc = rerkhosh.findall(a)
    try:
        fff = listoc[-2]
    except IndexError:
        fff = None
    for i in listoc:
        textg = textg + u"[[" + i + u"]]، "
        if i == fff:
            textg = textg + u"و "
    if textg:
        textg = textg[:-2]
    if textg.count(u"،") == 1:
        textg = textg.replace(u"،", u"")
    return textg


def en2fa(i):
    fachars = u"۰۱۲۳۴۵۶۷۸۹"
    try:
        b = str(i)
    except:
        b = i
    for i in range(0, 10):
        b = b.replace(str(i), fachars[i])
    return b


def translator(a, ensite, fasite, cache):
    if not a:
        return ''
    b = a
    rerf = re.compile("\[\[(.+?)(?:\||\]\])")
    for name in rerf.findall(a):
        if cache.get_value('translate:fawiki:enwiki:linktrans:' + name):
            res = cache.get_value('translate:fawiki:enwiki:linktrans:' + name)
            b = re.sub(u"\[\[%s(?:\|.+?)?\]\]" %
                       re.escape(name), res, b)
        else:
            try:
                pagename = pywikibot.Page(ensite, name)
                pagename.isRedirectPage()
            except:
                continue
            if pagename.isRedirectPage():
                pagename = pagename.getRedirectTarget()
            try:
                item = pywikibot.ItemPage.fromPage(pagename)
                item.get()
            except:
                continue
            if not item.sitelinks.get('fawiki'):
                continue
            if cache:
                cache.write_new_cache('translate:fawiki:enwiki:linktrans:' + name, linker(item.sitelinks['fawiki']))
            b = re.sub(u"\[\[%s(?:\|.+?)?\]\]" %
                        re.escape(name), linker(item.sitelinks['fawiki']), b)
    return b


def translator_taki(a, ensite, fasite, strict=False, cache=None):
    b = a
    for name in re.findall("\[\[(.+?)(?:\||\]\])", a):
        if cache and cache.get_value('translate:fawiki:enwiki:linktrans:' + name):
            res = cache.get_value('translate:fawiki:enwiki:linktrans:' + name)
            b = re.sub(u"\[\[%s(?:\|.+?)?\]\]" %
                       re.escape(name), res, b)
        else:
            try:
                pagename = pywikibot.Page(ensite, name)
            except:
                continue
            if pagename.isRedirectPage():
                pagename = pagename.getRedirectTarget()
            try:
                item = pywikibot.ItemPage.fromPage(pagename)
                item.get()
            except:
                continue
            if not item.sitelinks.get('fawiki'):
                continue
            if cache:
                cache.write_new_cache('translate:fawiki:enwiki:linktrans:' + name, linker(item.sitelinks['fawiki']))
            return linker(item.sitelinks['fawiki'])
    if strict:
        return ""
    return a


def sortcat(entext, entitle, title):
    if u"{{DEFAULTSORT:" in entext:
        enok = entext.split(u"{{DEFAULTSORT:")[1].split(u"}}")[0]
        mapok = enok
        thelist = entitle.split(u" ")
        for i in range(0, len(thelist)):
            mapok = mapok.replace(thelist[i], u"(((" + str(i) + u")))", 1)
        if re.search(u"[A-Za-z]", mapok):
            return ""
        mapok = mapok.replace(u",", u"،")
        thefalist = title.split(u" ")
        ok = mapok
        for i in range(0, len(thefalist)):
            ok = ok.replace(u"(((" + str(i) + u")))", thefalist[i], 1)
        return u"\n{{ترتیب‌پیش‌فرض:" + ok + u"}}"
    return ""


def catadder(entext, ensite, fasite, cache=None):
    cats = u""
    cache_prefix = 'translate:fawiki:enwiki:cattrans:'
    for name in re.findall(r'\[\[[Cc]ategory:(.+?)(?:\]\]|\|)', entext):
        if cache and cache.get_value(cache_prefix + name):
            res = cache.get_value(cache_prefix + name)
            cats = cats + u"\n[[%s]]" % res
        else:
            catpage = pywikibot.Page(ensite, u"Category:" + name)
            try:
                item = pywikibot.ItemPage.fromPage(catepage)
                item.get()
            except:
                continue
            if not item.sitelinks.get('fawiki'):
                continue
            fa_name = item.sitelinks['fawiki']
            if cache:
                cache.write_new_cache(cache_prefix + name, fa_name)
            cats = cats + u"\n[[" + fa_name + "]]"
    return cats


def seealsoer(entext, ensite, fasite, cache=None):
    re_see = re.compile(r"\=\= *?[Ss]ee [Aa]lso *?\=\=(.+?)\=\=", re.DOTALL)
    res_see = re_see.findall(entext)
    if not res_see:
        return ''
    re_see2 = re.compile(r"\* *?\[\[(.+?)(?:\||\]\])")
    text_see = u"\n\n== جستارهای وابسته =="

    for line_see in re_see2.findall(res_see[0]):
        line_see2 = translator_taki(linker(line_see), ensite, fasite, True, cache)
        if line_see2:
            text_see += u"\n*" + line_see2
    if text_see == u"\n\n== جستارهای وابسته ==":
        return u""
    return text_see


def dater(a):
    a = re.sub(
        r"(January|February|March|April|May|June|July|August|September|October|November|December)"
        r" (\d+)(?:th|st|nd|rd)?, (\d+)(\D|$)",
        r"\2 \1 \3\4",
        a)
    b = a
    for month in months:
        b = b.replace(month, months[month])
    return en2fa(b)


def get_lang(a, b):
    b = b.replace(u"_", u" ").split(" (")[0]
    if re.search(u"\{\{lang(-|\|)", a):
        return u"{{lang" + a.split("{{lang")[1].split("}}")[0] + u"}}"
    else:
        return u"{{lang-en|" + b + u"}}"


def data2fa(number, repo, cache=None, strict=False, ff=False):
    cache_key = 'translate:fawiki:wikidatawiki:linktrans:'
    if strict:
        cache_key += 'strict:'
    else:
        cache_key += 'no_strict:'
    cache_key += str(number)
    if cache and cache.get_value(cache_key):
        return cache.get_value(cache_key)
    item = pywikibot.ItemPage(repo, 'Q%d' % int(number))
    try:
        item.get()
    except:
        return ''
    if isinstance(item.sitelinks, list):
        item.sitelinks = {}
    if 'fawiki' in item.sitelinks:
        name = item.sitelinks['fawiki']
        if cache:
            cache.write_new_cache(cache_key, name)
        return name
    if strict:
        return ''
    if isinstance(item.labels, list):
        item.labels = {}
    if 'fa' in item.labels:
        name = item.labels['fa']
        if cache:
            cache.write_new_cache(cache_key, name)
        return name
    if not ff:
        return ''
    try:
        return item.labels['en']
    except:
        return ''


def occu(a, b, ensite, fasite, repo, cache=None):
    listoc = []
    if a:
        for i in a:
            ff = data2fa(int(i), repo, cache)
            if ff:
                listoc.append(ff)
    if not listoc:
        links = translator(u"[[" + b.replace(", ", u"]][[") + u"]]", ensite, fasite, cache)
        for i in re.findall("\[\[(.+?)(?:\]\]|\|)", links):
            if re.search(u"[آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی]", i):
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

def officefixer(text):
    #TODO: Make this work
    return text
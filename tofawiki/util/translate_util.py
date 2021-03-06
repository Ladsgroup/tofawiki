import re

# Disclaimer: This codes are super old and creepy, we need to rewrite them altogether
FA_LETTERS = r"[آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی]"

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
    c = []
    for line in a.split('\n'):
        if not line.strip() or line.strip()[0] in ['[', '{', '|']:
            continue
        c.append(line)
    a = '\n'.join(c)
    if re.search(u"\{\{lang(-|\|)", a):
        return u"{{lang" + a.split("{{lang")[1].split("}}")[0] + u"}}"
    else:
        return u"{{lang-en|" + b + u"}}"


def officefixer(text):
    # TODO: Make this work
    return text

import re

# Disclaimer: This codes are super old and creepy, we need to rewrite them altogether
FA_LETTERS = r"[آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی]"

months = {"January": "ژانویه",
          "February": "فوریه",
          "March": "مارس",
          "April": "آوریل",
          "May": "مه",
          "June": "ژوئن",
          "July": "ژوئیه",
          "August": "اوت",
          "September": "سپتامبر",
          "October": "اکتبر",
          "November": "نوامبر",
          "December": "دسامبر"}


def linker(a):
    if not a:
        return a
    if "[[" in a:
        return a
    if "(" in a:
        return "[[" + a + "|]]"
    return f"[[{a}]]"


def khoshgeler(a):
    if not a:
        return a
    rerkhosh = re.compile(r"\[\[(.+?)(?:\]\]|\|)")
    textg = ""
    listoc = rerkhosh.findall(a)
    try:
        fff = listoc[-2]
    except IndexError:
        fff = None
    for i in listoc:
        textg = textg + "[[" + i + "]]، "
        if i == fff:
            textg = textg + "و "
    if textg:
        textg = textg[:-2]
    if textg.count("،") == 1:
        textg = textg.replace("،", "")
    return textg


def en2fa(i):
    fachars = "۰۱۲۳۴۵۶۷۸۹"
    try:
        b = str(i)
    except Exception:
        b = i
    for i in range(0, 10):
        b = b.replace(str(i), fachars[i])
    return b


def sortcat(entext, entitle, title):
    if "{{DEFAULTSORT:" in entext:
        enok = entext.split("{{DEFAULTSORT:")[1].split("}}")[0]
        mapok = enok
        thelist = entitle.split(" ")
        for i in range(0, len(thelist)):
            mapok = mapok.replace(thelist[i], "(((" + str(i) + ")))", 1)
        if re.search("[A-Za-z]", mapok):
            return ""
        mapok = mapok.replace(",", "،")
        thefalist = title.split(" ")
        ok = mapok
        for i in range(0, len(thefalist)):
            ok = ok.replace("(((" + str(i) + ")))", thefalist[i], 1)
        return "\n{{ترتیب‌پیش‌فرض:" + ok + "}}"
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
    b = b.replace("_", " ").split(" (")[0]
    c = []
    for line in a.split('\n'):
        if not line.strip() or line.strip()[0] in ['[', '{', '|']:
            continue
        c.append(line)
    a = '\n'.join(c)
    if re.search(r"\{\{lang(-|\|)", a):
        return "{{lang" + a.split("{{lang")[1].split("}}")[0] + "}}"
    else:
        return "{{lang-en|" + b + "}}"


def officefixer(text):
    # TODO: Make this work
    return text

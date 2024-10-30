from django import template

register = template.Library()


@register.filter
def pretty(string):
    s = string.__str__()
    from bs4 import BeautifulSoup as bs

    soup = bs(s)  # make BeautifulSoup

    for tag in [t for t in soup.find_all(True) if t.name in ("body", "html", "head")]:
        if tag.name == "head":
            tag.decompose()
        else:
            tag.unwrap()
    prettyHTML = soup.prettify()  # prettify the html
    return prettyHTML

import requests
from bs4 import BeautifulSoup
from hashlib import sha1
from urllib.parse import urlparse
from dataclasses import dataclass

"""
urls = {
    "https://www.argenprop.com/departamento-alquiler-barrio-palermo-orden-masnuevos",
    "https://www.argenprop.com/departamento-alquiler-barrio-san-telmo-orden-masnuevos",
    "https://www.argenprop.com/departamento-alquiler-barrio-almagro-orden-masnuevos",
}
"""


@dataclass
class Parser:
    website: str
    link_regex: str

    def extract_links(self, contents: str):
        soup = BeautifulSoup(contents, "lxml")
        ads = soup.select(self.link_regex)
        for ad in ads:
            href = ad["href"]
            _id = sha1(href.encode("utf-8")).hexdigest()
            yield {"id": _id, "url": "{}{}".format(self.website, href)}


parsers = [
    Parser(website="https://www.zonaprop.com.ar", link_regex="a.go-to-posting"),
    Parser(website="https://www.argenprop.com", link_regex="div.listing__items div.listing__item a"),
    Parser(website="https://inmuebles.mercadolibre.com.ar", link_regex="li.results-item .rowItem.item a"),
]


def scrap_for_unseen(urls, history):
    for url in urls:
        res = requests.get(url)
        ads = list(extract_ads(url, res.text))
        seen, unseen = split_seen_and_unseen(ads, history)

        # print("{} seen, {} unseen".format(len(seen), len(unseen)))
        return seen, unseen


def extract_ads(url, text):
    uri = urlparse(url)
    parser = next(p for p in parsers if uri.hostname in p.website)
    return parser.extract_links(text)


def split_seen_and_unseen(ads, history):
    seen = [a for a in ads if a["id"] in history]
    unseen = [a for a in ads if a["id"] not in history]
    return seen, unseen

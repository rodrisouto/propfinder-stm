import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
import logging
import configparser
import pymongo
import configparser
import requests
from bs4 import BeautifulSoup
from hashlib import sha1
from urllib.parse import urlparse
from dataclasses import dataclass

# MongoDB
#########################################
DB_PROPFINDER = 'propfinder'
COL_SEEN_BY_USER = 'seenByUser'

config = configparser.ConfigParser()
config.read('sensitive.conf')
mongodb_password = config['mongodb.com']['password']

client = pymongo.MongoClient('mongodb+srv://rodrisouto:' + mongodb_password + '@propfinder-stm-0uhxi.mongodb.net/test?retryWrites=true&w=majority')

col = client[DB_PROPFINDER][COL_SEEN_BY_USER]

def create_user(userId):
    query = {'userId': userId}
    update = {'$set': {'userId': userId}}

    col.update_one(query, update, upsert=True)

def add_seen(userId, seen):
    query = {'userId': userId}
    update = {'$addToSet': {'seen': {'$each': [1, 2, 3, 4]}}}

    col.update_one(query, update)

def add_url(userId, url):
    query = {'userId': userId}
    update = {'$addToSet': {'urls': url}}

    col.update_one(query, update)

def get_urls(userId):
    query = {'userId': userId}

    return col.find_one(query)['urls']

def delete_url(userId, url):
    query = {'userId': userId}
    update = {'$pull': {'urls': url}}

    col.update_one(query, update)

# Service
#########################################

urls = {
#    "https://www.argenprop.com/departamento-alquiler-barrio-chacarita-hasta-25000-pesos-orden-masnuevos",
#    "https://www.zonaprop.com.ar/departamento-alquiler-villa-crespo-con-terraza-orden-publicado-descendente.html",
    "https://www.argenprop.com/departamento-alquiler-barrio-palermo-orden-masnuevos",
    "https://www.argenprop.com/departamento-alquiler-barrio-san-telmo-orden-masnuevos",
    "https://www.argenprop.com/departamento-alquiler-barrio-almagro-orden-masnuevos",
}


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


def _main():
    for url in urls:
        res = requests.get(url)
        ads = list(extract_ads(url, res.text))
        seen, unseen = split_seen_and_unseen(ads)

        print("{} seen, {} unseen".format(len(seen), len(unseen)))

        for u in unseen:
            notify(u)

        mark_as_seen(unseen)


def extract_ads(url, text):
    uri = urlparse(url)
    parser = next(p for p in parsers if uri.hostname in p.website)
    return parser.extract_links(text)


def split_seen_and_unseen(ads):
    history = get_history()
    seen = [a for a in ads if a["id"] in history]
    unseen = [a for a in ads if a["id"] not in history]
    return seen, unseen


def get_history():
    try:
        with open("seen.txt", "r") as f:
            return {l.rstrip() for l in f.readlines()}
    except:
        return set()


def notify(ad):
    bot = "1018987868:AAFiau5do1kkqI6BcEk6rHDgFRuHNq2g46I"
    room = "-493227444"
    url = "https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(bot, room, ad["url"])
    try:
        r = requests.get(url)
        print(r)
    except:
        print('Error in request')


def mark_as_seen(unseen):
    with open("seen.txt", "a+") as f:
        ids = ["{}\n".format(u["id"]) for u in unseen]
        f.writelines(ids)

# Controller
#########################################

COMMAND_ADD_URL = 'add_url'
COMMAND_GET_URLS = 'get_urls'
COMMAND_DELETE_URL = 'delete_url'

def controller_start(bot, update):
    try:
        chat_id = update.message.chat_id
        bot.send_message(chat_id=chat_id, text='Creating your user, wait for a confirmation message')
        create_user(chat_id)
        bot.send_message(chat_id=chat_id, text='User successfully created!')
    except Exception as e:
        bot.send_message(chat_id=chat_id, text='There was an error while creating your user')

def controller_add_url(bot, update):
    try:
        chat_id = update.message.chat_id
        url = update.message.text.replace('/'+COMMAND_ADD_URL, '', 1).strip()
        add_url(chat_id, url)

        bot.send_message(chat_id=chat_id, text='Successfully added new url!')
    except Exception as e:
        bot.send_message(chat_id=chat_id, text='There was an error adding the url: ' + url)

def controller_get_urls(bot, update):
    try:
        chat_id = update.message.chat_id
        urls = get_urls(chat_id)

        bot.send_message(chat_id=chat_id, text=str(', '.join(urls)))
    except Exception as e:
        bot.send_message(chat_id=chat_id, text='There was an error getting the urls')

def controller_delete_url(bot, update):
    try:
        chat_id = update.message.chat_id
        url = update.message.text.replace('/'+COMMAND_DELETE_URL, '', 1).strip()
        delete_url(chat_id, url)

        bot.send_message(chat_id=chat_id, text='Successfully deleted url')
    except Exception as e:
        bot.send_message(chat_id=chat_id, text='There was an error deleting the url: ' + url)

def echo(bot, update):
    update.message.reply_text(update.message.text)

def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)

def main():

    config = configparser.ConfigParser()
    config.read('sensitive.conf')
    botId = config['telegram.com']['bot-id']

    updater = Updater(botId)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", controller_start))
    dp.add_handler(CommandHandler(COMMAND_ADD_URL, controller_add_url))
    dp.add_handler(CommandHandler(COMMAND_GET_URLS, controller_get_urls))
    dp.add_handler(CommandHandler(COMMAND_DELETE_URL, controller_delete_url))
    dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

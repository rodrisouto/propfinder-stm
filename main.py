import database as db
import unseen_scrapper as scrapper

import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
import configparser
import logging
import requests
import traceback

# Controller
#########################################

COMMAND_ADD_URL = 'add_url'
COMMAND_GET_URLS = 'get_urls'
COMMAND_DELETE_URL = 'delete_url'


def start(bot, update):
    chat_id = update.message.chat_id

    try:
        send_message(bot, chat_id, 'Creating your user, wait for a confirmation message')
        db.create_user(chat_id)
        send_message(bot, chat_id, 'User successfully created!')
    except Exception as e:
        send_message(bot, chat_id, 'There was an error while creating your user')


def add_url(bot, update):
    chat_id = update.message.chat_id

    try:
        url = get_text_from_command(update.message.text, COMMAND_ADD_URL)

        if len(url) == 0:
            send_message(bot, chat_id, 'Cannot add empty url :(')
            return

        db.add_url(chat_id, url)

        send_message(bot, chat_id, 'Successfully added new url!')
    except Exception as e:
        send_message(bot, chat_id, 'There was an error adding the url: ' + url)


def get_urls(bot, update):
    chat_id = update.message.chat_id

    try:
        urls = db.get_urls(chat_id)
        
        if len(urls) == 0:
            send_message(bot, chat_id, 'There are no registered urls')
            return

        for url in urls:
            send_message(bot, chat_id, url)

    except Exception as e:
        send_message(bot, chat_id, 'There was an error getting the urls')


def delete_url(bot, update):
    chat_id = update.message.chat_id

    try:
        url = get_text_from_command(update.message.text, COMMAND_DELETE_URL)
        db.delete_url(chat_id, url)

        send_message(bot, chat_id, 'Successfully deleted url')
    except Exception as e:
        send_message(bot, chat_id, 'There was an error deleting the url: ' + url)


def update_unseen(bot, update):
    chat_id = update.message.chat_id

    try:
        urls = db.get_urls(chat_id)
        history = list(map(lambda ad: ad['id'], db.get_history(chat_id)))

        if len(urls) == 0:
            send_message(bot, chat_id, 'There are no registered urls')
            return

        process_unseen(bot, chat_id, urls, history)

    except Exception as e:
        # print(traceback.format_exc())
        send_message(bot, chat_id, 'There was an error updating unseen')


def error(bot, update, error):
    # logger.warning('Update "%s" caused error "%s"', update, error)
    print('Update "%s" caused error "%s"', update, error)


def get_text_from_command(original_text, command):
    return original_text.replace('/'+command, '', 1).strip()


def send_message(bot, chat_id, text):
    bot.send_message(chat_id=chat_id, text=text)


def send_message_2(bot, chat_id, text):
    url = "https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(bot, chat_id, text)
    try:
        r = requests.get(url)
        print(r)
    except:
        print('Error in request')


def process_unseen(bot, chat_id, urls, history):
    seen, unseen = scrapper.scrap_for_unseen(urls, history)

    send_message(bot, chat_id, 'You have already seen {} ads'.format(len(seen)))

    if len(unseen) == 0:
        send_message(bot, chat_id, 'There are no new ads for you')
        return

    for ad in unseen:
        send_message(bot, chat_id, ad['url'])

    mark_as_seen(chat_id, unseen)


def mark_as_seen(chat_id, unseen):
    db.add_seen(chat_id, unseen)


def main():

    config = configparser.ConfigParser()
    config.read('sensitive.conf')
    bot_id = config['telegram.com']['bot-id']

    updater = Updater(bot_id)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler(COMMAND_ADD_URL, add_url))
    dp.add_handler(CommandHandler(COMMAND_GET_URLS, get_urls))
    dp.add_handler(CommandHandler(COMMAND_DELETE_URL, delete_url))
    dp.add_handler(CommandHandler('update_unseen', update_unseen))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

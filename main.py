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
import datetime

# Controller
#########################################

COMMAND_ADD_URL = 'addurl'
COMMAND_GET_URLS = 'geturls'
COMMAND_DELETE_URL = 'deleteurl'

START_TEXT = """
    Hello from **propfinder bot** developed by @rodri_st

    1 - Make a prop search in one of the available domains (www.zonaprop.com.ar, www.argenprop.com, inmuebles.mercadolibre.com.ar)
    2 - Order the results by 'most recent'
    3 - Copy url and pass it to the bot (/addurl <url>)
    4 - Use /updateunseen to get unseen prop ads

    We recommend you delete the prop ads you are not interested in to keep the conversation clean

    Available commands:
    /help - How it works
    /geturls - Get current urls
    /addurl <url> - Add new url
    /deleteurl <url> - Delete url (if does not exists, nothing happens)
    /updateunseen - Fetches all prop ads from your urls and returns those you haven't seen
"""


def start(bot, update):
    chat_id = update.message.chat_id

    try:
        send_message(bot, chat_id, START_TEXT)
    except Exception as e:
        send_message(bot, chat_id, 'There was an error while creating your user')


def create_user(bot, update):
    chat_id = update.message.chat_id

    try:
        send_message(bot, chat_id, 'Creating your user, wait for a confirmation message')
        db.create_user(chat_id)
        send_message(bot, chat_id, 'User successfully created!')
    except Exception as e:
        print('Error with chat_id: {}'.format(chat_id))
        print(traceback.format_exc())
        send_message(bot, chat_id, 'There was an error while creating your user')


def add_url(bot, update):
    chat_id = update.message.chat_id

    try:
        url = get_text_from_command(update.message.text, COMMAND_ADD_URL)

        if len(url) == 0:
            send_message(bot, chat_id, 'Cannot add empty url :(')
            return

        username = get_username(update.message.chat)
        db.add_url(chat_id, username, url)

        send_message(bot, chat_id, 'Successfully added new url!')
    except Exception as e:
        print('Error with chat_id: {}'.format(chat_id))
        print(traceback.format_exc())
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
        print('Error with chat_id: {}'.format(chat_id))
        print(traceback.format_exc())
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
        print('Error with chat_id: {}'.format(chat_id))
        print(traceback.format_exc())
        send_message(bot, chat_id, 'There was an error updating unseen')


def vippify(bot, update):
    chat_id = update.message.chat_id

    try:
        db.add_vip(chat_id)

        send_message(bot, chat_id, 'Successfully vippified')
    except Exception as e:
        send_message(bot, chat_id, 'There was an error vippifying')


def unvippify(bot, update):
    chat_id = update.message.chat_id

    try:
        db.remove_vip(chat_id)

        send_message(bot, chat_id, 'Successfully unvippified')
    except Exception as e:
        send_message(bot, chat_id, 'There was an error unvippifying')


def health_check(bot, update):
    chat_id = update.message.chat_id
    send_message(bot, chat_id, 'OK')


def error(bot, update, error):
    # logger.warning('Update "%s" caused error "%s"', update, error)
    print('Update "%s" caused error "%s"', update, error)


def get_username(chat):
        chat_type = chat.type
        if chat_type == 'private':
            username = chat.username
        elif chat_type == 'group':
            username = chat.title
        else:
            username = ''

        return username


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

    send_message(bot, chat_id, 'You have already seen {} ads of your current urls and {} in total'.format(len(seen), len(history)))

    if len(unseen) == 0:
        send_message(bot, chat_id, 'There are no new ads for you')
        return

    for ad in unseen:
        send_message(bot, chat_id, ad['url'])

    mark_as_seen(chat_id, unseen)


def mark_as_seen(chat_id, unseen):
    db.add_seen(chat_id, unseen)


def log_ip():
    ip = requests.get('https://api.ipify.org').text
    print('My public IP address is:', ip)
    #db.record_deploy(ip, datetime.datetime.utcnow())


def main():
    log_ip()

    config = configparser.ConfigParser()
    config.read('sensitive.conf')
    bot_id = config['telegram.com']['bot-id']

    updater = Updater(bot_id)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', start))
    dp.add_handler(CommandHandler(COMMAND_ADD_URL, add_url))
    dp.add_handler(CommandHandler(COMMAND_GET_URLS, get_urls))
    dp.add_handler(CommandHandler(COMMAND_DELETE_URL, delete_url))
    dp.add_handler(CommandHandler('updateunseen', update_unseen))
    dp.add_handler(CommandHandler('vippify', vippify))
    dp.add_handler(CommandHandler('unvippify', unvippify))
    dp.add_handler(CommandHandler('healthcheck', health_check))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

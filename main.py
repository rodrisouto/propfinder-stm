import database as db
import unseen_scrapper as scrapper

import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
import configparser
import logging


# Controller
#########################################

COMMAND_ADD_URL = 'add_url'
COMMAND_GET_URLS = 'get_urls'
COMMAND_DELETE_URL = 'delete_url'


def controller_start(bot, update):
    try:
        chat_id = update.message.chat_id
        send_message(bot, chat_id, 'Creating your user, wait for a confirmation message')
        db.create_user(chat_id)
        send_message(bot, chat_id, 'User successfully created!')
    except Exception as e:
        send_message(bot, chat_id, 'There was an error while creating your user')


def controller_add_url(bot, update):
    try:
        chat_id = update.message.chat_id
        url = get_text_from_command(update.message.text, COMMAND_ADD_URL)

        if len(url) == 0:
            send_message(bot, chat_id, 'Cannot add empty url :(')
            return

        db.add_url(chat_id, url)

        send_message(bot, chat_id, 'Successfully added new url!')
    except Exception as e:
        send_message(bot, chat_id, 'There was an error adding the url: ' + url)


def controller_get_urls(bot, update):
    try:
        chat_id = update.message.chat_id
        urls = db.get_urls(chat_id)
        
        if len(urls) == 0:
            send_message(bot, chat_id, 'There are no registered urls')
            return

        for url in urls:
            send_message(bot, chat_id, url)

    except Exception as e:
        print(e)
        send_message(bot, chat_id, 'There was an error getting the urls')


def controller_delete_url(bot, update):
    try:
        chat_id = update.message.chat_id
        url = get_text_from_command(update.message.text, COMMAND_DELETE_URL)
        db.delete_url(chat_id, url)

        send_message(bot, chat_id, 'Successfully deleted url')
    except Exception as e:
        send_message(bot, chat_id, 'There was an error deleting the url: ' + url)


def error(bot, update, error):
    # logger.warning('Update "%s" caused error "%s"', update, error)
    print('Update "%s" caused error "%s"', update, error)


def get_text_from_command(original_text, command):
    return original_text.replace('/'+command, '', 1).strip()


def send_message(bot, chat_id, text):
    bot.send_message(chat_id=chat_id, text=text)


def main():

    config = configparser.ConfigParser()
    config.read('sensitive.conf')
    bot_id = config['telegram.com']['bot-id']

    updater = Updater(bot_id)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", controller_start))
    dp.add_handler(CommandHandler(COMMAND_ADD_URL, controller_add_url))
    dp.add_handler(CommandHandler(COMMAND_GET_URLS, controller_get_urls))
    dp.add_handler(CommandHandler(COMMAND_DELETE_URL, controller_delete_url))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

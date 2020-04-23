
# Stolen from https://devcenter.heroku.com/articles/clock-processes-python

from apscheduler.schedulers.blocking import BlockingScheduler
import database as db
import unseen_scrapper as scrapper
import configparser
import traceback
import requests

sched = BlockingScheduler()
MINUTES_INTERVAL = 20
UPDATE_VIP_JOB_NAME = 'updateVip'


@sched.scheduled_job('interval', minutes=MINUTES_INTERVAL)
def timed_job():
    # print('This job is run every three minutes.')
    try:
        update_vips()
        db.register_job_result(UPDATE_VIP_JOB_NAME, True, None)
    except Exception as e:
        print('Error with cron')
        message = traceback.format_exc()
        print(message)
        db.register_job_result(UPDATE_VIP_JOB_NAME, False, message)


def update_vips():

    bot_id = get_bot_id()

    vip = db.get_vip_user_ids()

    for chat_id in vip:
        update_unseen(bot_id, chat_id)


def get_bot_id():
    config = configparser.ConfigParser()
    config.read('sensitive.conf')
    bot_id = config['telegram.com']['bot-id']
    return bot_id


def update_unseen(bot_id, chat_id):
    urls = db.get_urls(chat_id)
    history = list(map(lambda ad: ad['id'], db.get_history(chat_id)))

    if len(urls) == 0:
        # Not sending messages on purpose.
        # send_message(bot_id, chat_id, 'There are no registered urls')
        return

    process_unseen(bot_id, chat_id, urls, history)


def process_unseen(bot_id, chat_id, urls, history):
    seen, unseen = scrapper.scrap_for_unseen(urls, history)

    if len(unseen) == 0:
        return

    send_message(bot_id, chat_id, 'You have already seen {} ads of your current urls and {} in total'.format(len(seen), len(history)))

    for ad in unseen:
        send_message(bot_id, chat_id, ad['url'])

    mark_as_seen(chat_id, unseen)


def mark_as_seen(chat_id, unseen):
    db.add_seen(chat_id, unseen)


def send_message(bot_id, chat_id, text):
    url = "https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(bot_id, chat_id, text)
    try:
        r = requests.get(url)
    except:
        print('Error in request: {}'.format(url))


sched.start()


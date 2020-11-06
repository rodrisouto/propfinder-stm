import pymongo
import configparser
from datetime import datetime

DB_PROPFINDER = 'propfinder'

COL_SEEN_BY_USER = 'historyByUser'
COL_DEPLOY = 'deploy'

config = configparser.ConfigParser()
config.read('sensitive.conf')
mongodb_username = config['mongodb.com']['username']
mongodb_password = config['mongodb.com']['password']
mongodb_database = config['mongodb.com']['database']
mongodb_cluster_domain = config['mongodb.com']['cluster-domain']

client = pymongo.MongoClient('mongodb+srv://rodrisouto:' + mongodb_password + '@' + mongodb_cluster_domain + '/' + mongodb_database + '?retryWrites=true&w=majority')

col_history = client[DB_PROPFINDER][COL_SEEN_BY_USER]


def create_user(user_id, username):
    query = {'userId': user_id}
    update = {'$set': {'userId': user_id, 'userName': username, 'lastUpdate': datetime.utcnow()}}

    col_history.update_one(query, update, upsert=True)


def add_url(user_id, username, url):
    query = {'userId': user_id}
    update = {'$set': {'userName': username, 'lastUpdate': datetime.utcnow()}, '$addToSet': {'urls': url}}

    col_history.update_one(query, update, upsert=True)


def get_urls(user_id):
    query = {'userId': user_id}

    user = col_history.find_one(query)
    if user is None:
        return []

    urls = user.get('urls')
    if urls is None:
        return []

    return urls


def delete_url(user_id, username, url):
    query = {'userId': user_id}
    update = {'$set': {'userName': username, 'lastUpdate': datetime.utcnow()}, '$pull': {'urls': url}}

    col_history.update_one(query, update)


def add_seen(user_id, seen):
    query = {'userId': user_id}
    update = {'$set': {'lastUpdate': datetime.utcnow()}, '$addToSet': {'history': {'$each': seen}}}

    col_history.update_one(query, update)


def get_history(user_id):
    query = {'userId': user_id}

    user = col_history.find_one(query)
    if user is None:
        return []

    history = user.get('history')
    if history is None:
        return []

    return history


############################################


def record_deploy(ip, datetime):
    col = client[DB_PROPFINDER][COL_DEPLOY]

    query = {'ip': ip, 'datetime': datetime}
    col.insert_one(query)


############################################


COL_VIP = 'vip'


def get_vip_user_ids():
    col = client[DB_PROPFINDER][COL_VIP]

    query = {}
    vip = col.find_one(query)
    if vip is None:
        return []

    userIds = vip.get('userIds')
    if userIds is None:
        return []

    return userIds


def add_vip(user_id):
    col = client[DB_PROPFINDER][COL_VIP]

    query = {}
    update = {'$set': {'lastUpdate': datetime.utcnow()}, '$addToSet': {'userIds': user_id}}

    col.update_one(query, update, upsert=True)


def remove_vip(user_id):
    col = client[DB_PROPFINDER][COL_VIP]

    query = {}
    update = {'$set': {'lastUpdate': datetime.utcnow()}, '$pull': {'userIds': user_id}}

    col.update_one(query, update, upsert=True)


############################################


COL_JOB = 'jobResult'


def register_job_result(jobName, success, message):
    col = client[DB_PROPFINDER][COL_JOB]

    col.insert_one({'name': jobName, 'success': success, 'message': message, 'datetime': datetime.utcnow()})


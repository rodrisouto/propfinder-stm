import pymongo
import configparser

DB_PROPFINDER = 'propfinder'
COL_SEEN_BY_USER = 'seenByUser'

config = configparser.ConfigParser()
config.read('sensitive.conf')
mongodb_password = config['mongodb.com']['password']

client = pymongo.MongoClient('mongodb+srv://rodrisouto:' + mongodb_password + '@propfinder-stm-0uhxi.mongodb.net/test?retryWrites=true&w=majority')

col = client[DB_PROPFINDER][COL_SEEN_BY_USER]


def create_user(user_id):
    query = {'userId': user_id}
    update = {'$set': {'user_id': user_id}}

    col.update_one(query, update, upsert=True)


def add_seen(user_id, seen):
    query = {'userId': user_id}
    update = {'$addToSet': {'seen': {'$each': [1, 2, 3, 4]}}}

    col.update_one(query, update)


def add_url(user_id, url):
    query = {'userId': user_id}
    update = {'$addToSet': {'urls': url}}

    col.update_one(query, update)


def get_urls(user_id):
    query = {'userId': user_id}

    user = col.find_one(query)
    if user is None:
        return []
    return user['urls']


def delete_url(user_id, url):
    query = {'userId': user_id}
    update = {'$pull': {'urls': url}}

    col.update_one(query, update)

#####################################################################미국서비스#################################################################
from bs4 import BeautifulSoup
import requests
import json
import pymongo
import api_code
import re
from bson.json_util import dumps

url = api_code.mongodb_url
news_db_url = api_code.newsdb_url
client = pymongo.MongoClient(url)
client_news = pymongo.MongoClient(news_db_url)
db = client.gatuant
news_client = client_news.news
nasdaq_db = db["nasdaq_info"]
nasdaq_list_db = db["nasdaq"]
nyse_db = db["nyse_info"]
nyse_list_db = db["nyse"]
news_db = news_client["eng"]


def translate(summarys):
    trans_url = api_code.kakao_trans_url
    KEY = api_code.kakao_key
    header_trans = {'Authorization': KEY}
    tr = {'query': summarys, 'src_lang': 'en', 'target_lang': 'kr'}
    translate = requests.get(url=trans_url, headers=header_trans, params=tr)
    if translate.status_code == 200:
        summary = json.loads(translate.text)['translated_text'][0][0]
    else:
        summary = summarys
    return summary


def isHangul(text):
    hanCount = len(re.findall(u'[\u3130-\u318F\uAC00-\uD7A3]+', text))
    return hanCount > 0


def get_news(pages, offsets):
    page = int(pages)
    offset = int(offsets)
    return dumps(news_db.find().sort([("_id", pymongo.DESCENDING)]).skip(
        page * offset).limit(offset))


def get_lists():
    return dumps(nasdaq_list_db.aggregate([
        {'$unionWith': "nyse", }
    ]))


def get_stocks(code):
    result = nasdaq_db.aggregate(
        [{'$unionWith': "nyse_info"}, {'$match': {'code': code}}]).next()
    summary = result['summary']
    if isHangul(summary):
        print(summary)
        return(dumps(result))
    else:
        tr_summary = translate(summary)
        print(tr_summary)
        result['summary'] = tr_summary
        if nasdaq_list_db.find_one({'code': code}):
            nasdaq_db.update_one(
                {'code': code}, {'$set': {'summary': tr_summary}})
        else:
            nyse_db.update_one(
                {'code': code}, {'$set': {'summary': tr_summary}})
        return(dumps(result))
    # return dumps(
    #     nasdaq_db.aggregate([
    #         {'$unionWith': "nyse_info"},
    #         {'$match': {'code': code}}
    #     ]).next()
    # )


def get_classfys(peg, eps, roe, pages, offsets):
    p = float(peg)
    e = float(eps)
    r = float(roe)
    page = int(pages)
    offset = int(offsets)
    query = {'peg': {'$lt': p, '$gt': 0},
             'eps_increase': {'$gt': e}, 'roe': {'$gt': r}}
    sorting = {"peg": pymongo.ASCENDING, "eps_increase":
               pymongo.DESCENDING, "code": pymongo.DESCENDING}
    print(p, e, r, page, offset)
    return dumps(
        nasdaq_db.aggregate([
            {'$unionWith': "nyse_info"},
            {'$match': query},
            {'$sort': sorting},
            {'$skip': page*offset},
            {"$limit": offset}
        ])
    )


def get_recommends(kinds, pages, offsets):
    page = int(pages)
    offset = int(offsets)
    if kinds == "excellent":
        query = {'peg': {'$gt': 0, '$lt': 1.0}, 'point': {
            '$gt': 8.5}, 'marketCap': {'$gt': 30000000000}}
        sorting = {"marketCap": pymongo.DESCENDING,
                   "point": pymongo.DESCENDING, "code": pymongo.DESCENDING}
    elif kinds == "grow":
        query = {'point': {'$gt': 8.5}, 'eps_increase': {'$gt': 10.0}}
        sorting = {"eps_increase": pymongo.DESCENDING,
                   "point": pymongo.DESCENDING, "code": pymongo.DESCENDING}
    elif kinds == "point":
        query = {'point': {'$gt': 13.0}}
        sorting = {"point": pymongo.DESCENDING,
                   "peg": pymongo.DESCENDING, "code": pymongo.DESCENDING}
    elif kinds == "undervalued":
        query = {'point': {'$gt': 14}, 'volume_price': {'$lt': 2500000001}}
        sorting = [("point", pymongo.DESCENDING),
                   ("peg", pymongo.DESCENDING), ("cd", pymongo.DESCENDING)]
    return dumps(nasdaq_db.aggregate([
        {'$unionWith': "nyse_info"},
        {'$match': query},
        {'$sort': sorting},
        {'$skip': page*offset},
        {"$limit": offset}
    ]
    ))

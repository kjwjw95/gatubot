#####################################################################미국서비스#################################################################
from bs4 import BeautifulSoup
import requests
import json
import pymongo
import api_code
from bson.json_util import dumps
url = api_code.mongodb_url
client = pymongo.MongoClient(url)
db = client.gatuant
nasdaq_db = db["nasdaq_info"]
nasdaq_list_db = db["nasdaq"]
nyse_db = db["nasdaq_info"]
nyse_list_db = db["nasdaq"]


def get_news():
    url = "https://www.cnbc.com/world/"
    trans_url = "https://dapi.kakao.com/v2/translation/translate"
    KEY = "KakaoAK 49ba514a295f31e38cc9ceee74c0a862"
    header_trans = {"Authorization": KEY}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.3"}
    html = requests.get(url, headers=headers)
    soup = BeautifulSoup(html.text, "html.parser")
    metadata = soup.find_all("div", class_="LatestNews-headline", limit=10)
    news = []
    key = 0
    for i in metadata:
        title = i.a.get_text()
        title = title.replace("\n", "")
        tr = {"query": title, "src_lang": "en", "target_lang": "kr"}
        translate = requests.get(
            url=trans_url, headers=header_trans, params=tr)
        new = {"title": json.loads(translate.text)[
            "translated_text"][0][0], "href": i.a.get("href"), "eng_title": title, "key": key}
        key += 1
        news.append(new)
    return news


def get_lists():
    return dumps(nasdaq_list_db.aggregate([
        {'$unionWith': "nyse", }
    ]))


def get_stocks(code):
    return dumps(
        nasdaq_db.aggregate([
            {'$unionWith': "nyse_info"},
            {'$match': {'code': code}}
        ]).next()
    )
    # if market == "nasdaq":
    #     return dumps(nasdaq_db.find_one({'code': code}))
    # elif market == "nyse":
    #     return dumps(nyse_db.find_one({'code': code}))


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


def get_recommends(kinds, page, offset):
    if kinds == "excellent":
        query = {'peg': {'$gt': 0, '$lt': 1.0}, 'point': {
            '$gt': 7.0}, 'marketCap': {'$gt': 30000000000}}
        sorting = {"marketCap": pymongo.DESCENDING,
                   "point": pymongo.DESCENDING, "code": pymongo.DESCENDING}
    elif kinds == "grow":
        query = {'point': {'$gt': 7.0}, 'eps_increase': {'$gt': 10.0}}
        sorting = {"eps_increase": pymongo.DESCENDING,
                   "point": pymongo.DESCENDING, "code": pymongo.DESCENDING}
    elif kinds == "point":
        query = {'point': {'$gt': 12.0}}
        sorting = {"point": pymongo.DESCENDING,
                   "peg": pymongo.DESCENDING, "code": pymongo.DESCENDING}
    return dumps(nasdaq_db.aggregate([
        {'$unionWith': "nyse_info"},
        {'$match': query},
        {'$sort': sorting},
        {'$skip': page*offset},
        {"$limit": offset}
    ]
    ))

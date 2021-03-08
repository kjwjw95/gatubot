#####################################################################한국서비스#################################################################
from bs4 import BeautifulSoup
import requests
import json
import pymongo
from bson.json_util import dumps
# import pandas as pd
# import pandas_datareader as pdr
# from datetime import date, timedelta, datetime
url = 'mongodb+srv://kjw95:wjddnr1212@cluster0.i61ze.mongodb.net/gatuant?retryWrites=true&w=majority'
client = pymongo.MongoClient(url)
db = client.gatuant
stock_db = db["stock_info"]
list_db = db["stock"]


def get_news():
    url = "https://news.naver.com/main/main.nhn?mode=LSD&mid=shm&sid1=101"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.3"}
    html = requests.get(url, headers=headers,)
    soup = BeautifulSoup(html.text, "html.parser")
    metadata = soup.find_all("div", class_="cluster_text", limit=30)
    news = []
    key = 0
    for i in metadata:
        new = {"title": i.a.get_text().rstrip(
            '\n'), "href": i.a.get("href"), "key": key}
        key += 1
        news.append(new)
    return news


def get_lists():
    return dumps(list_db.find())


def get_stocks(code):
    return dumps(stock_db.find_one({'code': code}))


def get_classfys(roe, eps, debt, pages, offsets):
    r = float(roe)
    e = float(eps)
    d = float(debt)
    page = int(pages)
    offset = int(offsets)

    query = {'roe.2020.third_quarter': {'$gt': r}, 'roe.2020.second_quarter': {'$gt': r}, 'roe.2020.first_quarter': {'$gt': r},
             'eps_increase.2018': {'$gt': e}, 'eps_increase.2019': {'$gt': e}, 'eps_increase.2020': {'$gt': e}, 'debt': {'$lt': d}}
    sorting = [("roe.2020.third_quarter", pymongo.DESCENDING),
               ("eps_increase.2020", pymongo.DESCENDING), ("code", pymongo.DESCENDING)]
    return dumps(stock_db.find(query).sort(sorting).skip(page*offset).limit(offset))


def get_recommends(kinds, pages, offsets):
    page = int(pages)
    offset = int(offsets)
    if kinds == "excellent":
        query = {'peg': {'$gt': 0, '$lt': 1.0}, 'point': {
            '$gt': 10.0}, 'market_cap': {'$gt': 785500000000}}
        sorting = [("market_cap", pymongo.DESCENDING),
                   ("point", pymongo.DESCENDING), ("code", pymongo.DESCENDING)]
    elif kinds == "grow":
        query = {'point': {'$gt': 12.0}, 'eps_increase.2020': {'$gt': 10.0}}
        sorting = [("eps_increase.2020", pymongo.DESCENDING),
                   ("point", pymongo.DESCENDING), ("cd", pymongo.DESCENDING)]
    elif kinds == "point":
        query = {'point': {'$gt': 13.0}}
        sorting = [("point", pymongo.DESCENDING),
                   ("peg", pymongo.DESCENDING), ("cd", pymongo.DESCENDING)]
    return dumps(stock_db.find(query).sort(sorting).skip(page*offset).limit(offset))

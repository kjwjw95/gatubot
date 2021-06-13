#####################################################################한국서비스#################################################################
from bs4 import BeautifulSoup
import requests
import json
import pymongo
import api_code
import urllib.request
from datetime import date, timedelta, datetime
from bson.json_util import dumps
url = api_code.mongodb_url
client = pymongo.MongoClient(url)
db = client.gatuant
stock_db = db["stock_info"]
list_db = db["stock"]
yeardb = db['years']
chart_db = db['stock_chart']


def find_news(word):
    encText = urllib.parse.quote(word)
    url = api_code.naver_url + encText  # json 결과
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", api_code.naver_id)
    request.add_header("X-Naver-Client-Secret", api_code.naver_secret)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()
    if(rescode == 200):
        response_body = response.read()
        return(json.loads(response_body.decode('utf-8'))['items'])
    else:
        return("뉴스 결과를 찾을 수 없습니다.")


def get_news():
    url = api_code.news_url
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
    chart = chart_db.aggregate([
        {'$match': {'code': code}},
        {
            '$project': {
                'share': {
                    '$filter': {
                        'input': "$share",
                        'as': "share",
                        'cond': {'$gte': ["$$share.date", str(date.today() - timedelta(30))]}
                    }
                }
            }
        }
    ]).next()
    stock = stock_db.find_one({'code': code})
    news = find_news(stock['name'])
    year = yeardb.find_one()
    result = {
        'stock': stock,
        'news': news,
        'year': year,
        'chart': chart
    }
    return dumps(result)


def get_classfys(eps, peg, roe, pages, offsets):
    r = float(roe)
    e = float(eps)
    p = float(peg)
    page = int(pages)
    offset = int(offsets)

    query = {'roe.2020.third_quarter': {'$gt': r}, 'roe.2020.second_quarter': {'$gt': r}, 'roe.2020.first_quarter': {'$gt': r},
             'eps_increase.2018': {'$gt': e}, 'eps_increase.2019': {'$gt': e}, 'eps_increase.2020': {'$gt': e}, 'peg': {'$lt': p, '$gt': 0}}
    sorting = [("roe.2020.third_quarter", pymongo.DESCENDING),
               ("eps_increase.2020", pymongo.DESCENDING), ("code", pymongo.DESCENDING)]
    return dumps(stock_db.find(query).sort(sorting).skip(page*offset).limit(offset))


def get_recommends(kinds, pages, offsets):
    page = int(pages)
    offset = int(offsets)
    if kinds == "excellent":
        query = {'peg': {'$gt': 0, '$lt': 1.0}, 'point': {
            '$gt': 11.0}, 'market_cap': {'$gt': 785500000000}, 'volume_price': {'$gt': 3000000000}}
        sorting = [("market_cap", pymongo.DESCENDING),
                   ("point", pymongo.DESCENDING), ("code", pymongo.DESCENDING)]
    elif kinds == "grow":
        query = {'point': {'$gt': 11.5}, 'eps_increase.2020': {
            '$gt': 12}, 'volume_price': {'$gt': 2500000000}}
        sorting = [("eps_increase.2020", pymongo.DESCENDING),
                   ("point", pymongo.DESCENDING), ("cd", pymongo.DESCENDING)]
    elif kinds == "point":
        query = {'point': {'$gt': 13}, 'volume_price': {'$gt': 2500000000}}
        sorting = [("point", pymongo.DESCENDING),
                   ("peg", pymongo.DESCENDING), ("cd", pymongo.DESCENDING)]
    elif kinds == "undervalued":
        query = {'point': {'$gt': 13}, 'volume_price': {'$lt': 2500000001}}
        sorting = [("point", pymongo.DESCENDING),
                   ("peg", pymongo.DESCENDING), ("cd", pymongo.DESCENDING)]
    return dumps(stock_db.find(query).sort(sorting).skip(page*offset).limit(offset))

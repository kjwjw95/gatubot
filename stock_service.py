import pymongo
from bson.json_util import dumps
import json
import pandas as pd
import pandas_datareader as pdr

url = 'mongodb+srv://kjw95:wjddnr1212@cluster0.i61ze.mongodb.net/gatuant?retryWrites=true&w=majority'
client = pymongo.MongoClient(url)
db = client.gatuant
stock_db = db["stock_info"]
list_db = db["stock"]


def stock_cal(code):
    # code = get_code(code_df, name)
    try:
        df = pdr.get_data_yahoo(code, adjust_price=True)
        dates = date.today()
        dates = dates.strftime('%Y-%m-%d')
        stocks = int(df.loc[dates, 'Close'])
        return stocks
    except:
        return 0
# 검색한 주식의 정보를 불러오는 메소드


def get_stock_info(code):
    return dumps(stock_db.find_one({'code': code}), ensure_ascii=False)

# 주식 리스트를 불러오는 메소드


def get_stock_list():
    return dumps(list_db.find(), ensure_ascii=False)

# 주식 정렬 리스트를 불러오는 메소드


def get_stock_sort(roe=-100, eps=-100, debt=500):
    query = {'roe.2020.third_quarter': {'$gt': roe}, 'roe.2020.second_quarter': {'$gt': roe}, 'roe.2020.first_quarter': {'$gt': roe},
             'eps_increase.2020': {'$gt': eps}, 'eps_increase.2020': {'$gt': eps}, 'eps_increase.2020': {'$gt': eps},
             'eps.2020.third_quarter': {'$gt': 0}, 'debt': {'$lt': debt}}
    return dumps(stock_db.find(query), ensure_ascii=False)

# 주식 추천 리스트를 불러오는 메소드


def get_stock_recommend():
    query = {'roe.2020.third_quarter': {'$gt': 0}, 'peg': {'$gt': 0, '$lt': 1.5}, 'eps.2020.third_quarter': {'$gt': 0}, 'debt': {
        '$lt': 100.0}, 'profit.2020.third_quarter': {'$gt': 0}, 'profit.2020.first_quarter': {'$gt': 0}, 'profit.2020.second_quarter': {'$gt': 0}}
    lists = stock_db.find(query)
    result = []
    for l in lists:
        try:
            cd = l['code']
            stock = stock_cal(cd)
            if l['rim'] > stock:
                result.append(l)
        except:
            continue
    return dumps(result, ensure_ascii=False)

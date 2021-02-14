import pymongo
from bson.json_util import dumps
import json
import pandas as pd
import pandas_datareader as pdr
from datetime import date, timedelta
url = 'mongodb+srv://kjw95:wjddnr1212@cluster0.i61ze.mongodb.net/gatuant?retryWrites=true&w=majority'
client = pymongo.MongoClient(url)
db = client.gatuant
stock_db = db["stock_info"]
list_db = db["stock"]


def Per_cal(eps, stock):
    return stock / eps


def Pbr_cal(bps, stock):
    return stock/bps


def stock_cal(code):
    # code = get_code(code_df, name)
    df = pdr.get_data_yahoo(code, adjust_price=True)
    for ddate in range(0, 5, 1):
        dates = date.today() - timedelta(ddate)
        dates = dates.strftime('%Y-%m-%d')
        try:
            stocks = int(df.loc[dates, 'Close'])
            # print(stocks, " ", dates)
            if (stocks > 0):
                break
        except:
            continue
    return stocks
# 검색한 주식의 정보를 불러오는 메소드


def get_stock_info(code):
    result = stock_db.find_one({'code': code})
    result["share"] = stock_cal(result["code"])
    return dumps(result)

# 주식 리스트를 불러오는 메소드


def get_stock_list():
    return dumps(list_db.find())

# 주식 정렬 리스트를 불러오는 메소드


def get_stock_sort(roe, eps, debt):
    r = float(roe)
    e = float(eps)
    d = float(debt)
    query = {'roe.2020.third_quarter': {'$gt': r}, 'roe.2020.second_quarter': {'$gt': r}, 'roe.2020.first_quarter': {'$gt': r},
             'eps_increase.2018': {'$gt': e}, 'eps_increase.2019': {'$gt': e}, 'eps_increase.2020': {'$gt': e}, 'debt': {'$lt': d}}
    lists = stock_db.find(query)
    result = []
    for l in lists:
        cd = l['code']
        share = stock_cal(cd)
        stock = {"name": l['name'], "share": str(share), "rim": str(l['rim']), "per":  str(Per_cal(
            l['eps']['2020']['third_quarter'], share)), "pbr": str(Pbr_cal(l['bps']['2020']['third_quarter'], share)), "roe": str(l['roe']['2020']['third_quarter']), "debt": str(l['debt']), "code": cd}
        result.append(stock)
    return result

# 주식 추천 리스트를 불러오는 메소드


def get_stock_recommend():
    query = {'roe.2020.third_quarter': {'$gt': 5}, 'peg': {'$gt': 0, '$lt': 1.5}, 'eps.2020.third_quarter': {'$gt': 0}, 'debt': {
        '$lt': 100.0}, 'profit.2020.third_quarter': {'$gt': 0}, 'profit.2020.first_quarter': {'$gt': 0}, 'profit.2020.second_quarter': {'$gt': 0}}
    lists = dumps(stock_db.find(query))
    # print(lists)
    # result = []
    # for l in lists:
    #     cd = l['code']
    #     stock = stock_cal(cd)
    #     if l['rim'] > stock:
    #         result.append(dumps(l))
    return lists

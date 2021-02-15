import pymongo
from bson.json_util import dumps
import json
import pandas as pd
import pandas_datareader as pdr
from datetime import date, timedelta, datetime
url = 'mongodb+srv://kjw95:wjddnr1212@cluster0.i61ze.mongodb.net/gatuant?retryWrites=true&w=majority'
client = pymongo.MongoClient(url)
db = client.gatuant
stock_db = db["stock_info"]
list_db = db["stock"]


def Per_cal(eps, stock):
    return stock / eps


def stock_quater_cal(year, code):
    result = []
    for i in range(3):
        temp = []
        years = str(year+i)
        for j in range(4):
            month = 3+3*j
            dates = years+"-"+str(month)+"-01"
            temp.append(stock_cal(code, datetime.strptime(dates, '%Y-%m-%d')))
        result.append(temp)
    return result


def Per_quater(eps, year, stocks):
    lists = []
    for i in range(3):
        years = str(year+i)
        for j in range(4):
            if j == 0:
                quater = "first_quarter"
            elif j == 1:
                quater = "second_quarter"
            elif j == 2:
                quater = "third_quarter"
            elif j == 3:
                quater = "fourth_quarter"
            epss = eps[years][quater]
            stock = stocks[i][j]

            if epss == 0:
                lists.append(0)
            else:
                lists.append(stock / epss)
    result = {
        year: {
            "first_quarter": lists[0],
            "fourth_quarter": lists[1],
            "second_quarter": lists[2],
            "third_quarter": lists[3]
        },
        year+1: {
            "first_quarter": lists[4],
            "fourth_quarter": lists[5],
            "second_quarter": lists[6],
            "third_quarter": lists[7]
        },
        year+2: {
            "first_quarter": lists[8],
            "fourth_quarter": lists[9],
            "second_quarter": lists[10],
            "third_quarter": lists[11]
        }
    }
    return result


def Pbr_quater(bps, year, stocks):
    lists = []
    for i in range(3):
        years = str(year+i)
        for j in range(4):
            if j == 0:
                quater = "first_quarter"
            elif j == 1:
                quater = "second_quarter"
            elif j == 2:
                quater = "third_quarter"
            elif j == 3:
                quater = "fourth_quarter"
            bpss = bps[years][quater]
            stock = stocks[i][j]

            if bpss == 0:
                lists.append(0)
            else:
                lists.append(stock / bpss)
    result = {
        year: {
            "first_quarter": lists[0],
            "fourth_quarter": lists[1],
            "second_quarter": lists[2],
            "third_quarter": lists[3]
        },
        year+1: {
            "first_quarter": lists[4],
            "fourth_quarter": lists[5],
            "second_quarter": lists[6],
            "third_quarter": lists[7]
        },
        year+2: {
            "first_quarter": lists[8],
            "fourth_quarter": lists[9],
            "second_quarter": lists[10],
            "third_quarter": lists[11]
        }
    }
    return result


def Pbr_cal(bps, stock):
    return stock/bps


def Point_cal(info):
    return 0


def stock_cal(code, d=date.today()):
    df = pdr.get_data_yahoo(code, adjust_price=True)
    stocks = 0
    for ddate in range(0, 7, 1):
        dates = d - timedelta(ddate)
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
    year = 2018
    result = stock_db.find_one({'code': code})
    share = stock_cal(code)
    stock_quater = stock_quater_cal(year, code)
    result["share"] = share
    result["per"] = Per_quater(result["eps"], year, stock_quater)
    result["pbr"] = Pbr_quater(result["bps"], year, stock_quater)
    result["point"] = Point_cal(result)
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

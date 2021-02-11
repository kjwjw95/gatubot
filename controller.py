import traceback
import os

from flask import request, url_for, jsonify
from flask_api import FlaskAPI, status, exceptions
from flask_restplus import Resource, Api, fields
# from flask_jwt_extended import ( JWTManager, jwt_required, create_access_token, create_refresh_token, get_jwt_identity, jwt_refresh_token_required )

# from functools import wraps

import stock_service
import news_service

app = FlaskAPI(__name__)
app.config['JSON_AS_ASCII'] = False

# 스웨거 설정
api = Api(app, version='1.0', title='가투봇 RestApi',
          description='뉴스 조회, 주식 조회',
          )

newsns = api.namespace('news', description='뉴스 조회')
stocksns = api.namespace('stocks', description='주식 조회')

# def error_decorator(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         try :
#             return f(*args, **kwargs)

#         except cn_exception.BizError as be :
#             return jsonify({'code':be.code, 'msg':be.msg}), be.httpcode

#         except Exception as ex :
#             traceback.print_exc()
#             return jsonify({'code':500, 'msg':'Internal Error'}), status.HTTP_500_INTERNAL_SERVER_ERROR

#     return decorated_function


@app.route('/', methods=['GET'])
def ping():
    return jsonify({'code': 200, 'msg': 'success'}), status.HTTP_200_OK


@newsns.route('/<lng>')
class NewsManager(Resource):
    def get(lng):
        '''뉴스를 불러온다'''
        print(lng)
        return news_service.getnews(lng), 200


@stocksns.route('/info/<code>')
class StocksInfoManager(Resource):
    def get():
        '''검색한 주식의 정보를 불러온다'''
        return stock_service.get_stock_info(code), 200


@stocksns.route('/list')
class StockslistManager(Resource):
    def get():
        '''종목코드 리스트를 불러온다'''
        return stock_service.get_stock_list(), 200


@stocksns.route('/sort')
class StockssortManager(Resource):
    def get():
        '''주식 정렬 리스트를 불러온다'''
        roes = request.args.get('roe')
        epss = request.args.get('eps')
        deb = request.args.get('deb')
        return stock_service.get_stock_sort(roe=roes, eps=epss, debt=deb), 200


@stocksns.route('/recommend')
class StocksrecommendManager(Resource):
    def get_stocklist():
        '''주식 추천 리스트를 불러온다'''
        return stock_service.get_stock_recommend(), 200

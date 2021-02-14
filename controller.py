import traceback
import os
import json
from flask import request, url_for, jsonify
from flask_api import FlaskAPI, status, exceptions
# from flask_jwt_extended import ( JWTManager, jwt_required, create_access_token, create_refresh_token, get_jwt_identity, jwt_refresh_token_required )

# from functools import wraps

import stock_service
import news_service

app = FlaskAPI(__name__)
app.config['JSON_AS_ASCII'] = False


def error_decorator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)

        except cn_exception.BizError as be:
            return jsonify({'code': be.code, 'msg': be.msg}), be.httpcode

        except Exception as ex:
            traceback.print_exc()
            return jsonify({'code': 500, 'msg': 'Internal Error'}), status.HTTP_500_INTERNAL_SERVER_ERROR

    return decorated_function


@app.route('/', methods=['GET'])
def ping():
    return jsonify({'code': 200, 'msg': 'success'}), status.HTTP_200_OK

# 뉴스를 불러오는 메소드


@app.route('/news/<lng>', methods=['GET'])
def get_news(lng):

    result = news_service.getnews(lng)

    return jsonify({'code': 200, 'msg': 'SUCCESS', 'news': result}), status.HTTP_200_OK

# 검색한 주식의 정보를 불러오는 메소드


@app.route('/stock/info', methods=['GET'])
def get_stockinfo():
    code = request.args.get('code')
    result = stock_service.get_stock_info(code)
    resp = jsonify({'code': 200, 'msg': 'SUCCESS',
                    'stock': json.loads(result)})
    resp.status_code = 200
    return resp

# 주식 리스트를 불러오는 메소드


@app.route('/stock/list', methods=['GET'])
def get_stocklist():
    result = stock_service.get_stock_list()
    resp = jsonify({'code': 200, 'msg': 'SUCCESS',
                    'stock': json.loads(result)})
    resp.status_code = 200
    return resp

# 주식 정렬 리스트를 불러오는 메소드


@app.route('/stock/sort', methods=['GET'])
def get_stocklist2():
    roes = request.args.get('roe', 0)
    epss = request.args.get('eps', 0)
    deb = request.args.get('debt', 500)
    return jsonify({'code': 200, 'msg': 'SUCCESS', 'stocks': stock_service.get_stock_sort(roe=roes, eps=epss, debt=deb)}), status.HTTP_200_OK


# 주식 추천 리스트를 불러오는 메소드
@app.route('/stock/recommend', methods=['GET'])
def get_stocklist3():
    result = stock_service.get_stock_recommend()
    resp = jsonify({'code': 200, 'msg': 'SUCCESS',
                    'stock': json.loads(result)})
    resp.status_code = 200
    return resp

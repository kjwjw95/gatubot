import traceback
import os
import json
from flask import request, url_for, jsonify
from flask_api import FlaskAPI, status, exceptions

import kor_service
import eng_service

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

# 한국서비스를 불러오는 메소드


@app.route('/kor/<bif>', methods=['GET'])
def get_kor(bif):
    try:
        if bif == "news":
            result = kor_service.get_news()
        elif bif == "lists":
            result = json.loads(
                kor_service.get_lists())
        elif bif == "stocks":
            result = json.loads(
                kor_service.get_stocks(request.args.get('code')))
        elif bif == "classfys":
            result = json.loads(kor_service.get_classfys(request.args.get('roe', 0), request.args.get(
                'eps', 0), request.args.get('debt', 500), request.args.get('page', 0), request.args.get('offset', 10)))
        elif bif == "recommends":
            result = json.loads(kor_service.get_recommends(request.args.get(
                'kinds', 'excellent'), request.args.get('page', 0), request.args.get('offset', 10)))
        else:
            return jsonify({'code': 400, 'msg': 'error'}), status.HTTP_400_BAD_REQUEST

        return jsonify({'code': 200, 'msg': 'SUCCESS', 'result': result}), status.HTTP_200_OK
    except:
        return jsonify({'code': 400, 'msg': 'error'}), status.HTTP_400_BAD_REQUEST

# 미국서비스를 불러오는 메소드


@ app.route('/eng/<bif>', methods=['GET'])
def get_eng(bif):
    try:
        if bif == "news":
            result = eng_service.get_news()
        elif bif == "lists":
            result = json.loads(
                eng_service.get_lists())
        elif bif == "stocks":
            result = json.loads(
                eng_service.get_stocks(request.args.get('code')))
        elif bif == "classfys":
            result = json.loads(eng_service.get_classfys(peg=request.args.get(
                'peg', 5), eps=request.args.get('eps', 0), roe=request.args.get('roe', 0), pages=request.args.get('page', 0), offsets=request.args.get('offset', 10)))
        elif bif == "recommends":
            result = json.loads(eng_service.get_recommends(
                request.args.get('kinds', 'excellent'), request.args.get('page', 0), request.args.get('offset', 10)))
        else:
            return jsonify({'code': 400, 'msg': 'error'}), status.HTTP_400_BAD_REQUEST

        return jsonify({'code': 200, 'msg': 'SUCCESS', 'result': result}), status.HTTP_200_OK
    except:
        return jsonify({'code': 400, 'msg': 'error'}), status.HTTP_400_BAD_REQUEST

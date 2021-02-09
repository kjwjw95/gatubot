import traceback
import os 

from flask import request, url_for, jsonify
from flask_api import FlaskAPI, status, exceptions

from functools import wraps

# import cn_exception
# import cn_service

app = FlaskAPI(__name__)

def error_decorator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try :
            return f(*args, **kwargs)

        except cn_exception.BizError as be :
            return jsonify({'code':be.code, 'msg':be.msg}), be.httpcode

        except Exception as ex :
            traceback.print_exc()
            return jsonify({'code':500, 'msg':'Internal Error'}), status.HTTP_500_INTERNAL_SERVER_ERROR

    return decorated_function

@app.route('/', methods=['GET'])
def ping():
    return jsonify({'code':200, 'msg':'success'}), status.HTTP_200_OK


@app.route('/stock/<st>', methods=['GET'])
def get_blocked_sites(st):

    # TODO cache 필요

    account = extract_account(request)

    result = cn_service.get_blocked_sites(account, st)

    return jsonify({'code':200, 'msg':'SUCCESS', 'clean_news':result['clean_news'], 'last':result['last'] }), status.HTTP_200_OK

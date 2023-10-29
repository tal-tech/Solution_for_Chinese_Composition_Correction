#! /usr/bin/python3
# -*- coding: UTF-8 -*-
import time
import traceback
from uuid import uuid4
from config import Config
from flask import Flask, request
from utility import log_error
from utility.g_logger import g_logger
from common.e_eureka import eureka_register
from utility.utils import make_response, Status, check_args

from module.rhetoric_recognition.rhetoric import Rhetoric

# from score_process import Process


if Config.DEPLOY_ENV != 'local':
    eureka_register()

app = Flask(__name__)
# score_process = Process()
scorer = Rhetoric()


@app.route('/', methods=['POST'])
def index():
    st = time.time()
    req_id = request.args.get('requestId') or str(uuid4())
    try:
        if not request.json:
            raise KeyError
        else:
            original_sent_list = request.json.get('original_sent_list')
        
        if not check_args(original_sent_list):
            raise TypeError  

    except TypeError:
        log_error(req_id, Status.PAR_ERROR)
        return make_response(Status.PAR_ERROR)
    except Exception as e:
        log_error(req_id, Status.BAD_REQ, traceback.format_exception(type(e), e, e.__traceback__))
        return make_response(Status.BAD_REQ)

    try:
        rh_result = scorer.get_all_rhetorics(original_sent_list)
    except Exception as e:
        log_error(req_id, Status.MODEL_ERR, traceback.format_exception(type(e), e, e.__traceback__))
        return make_response(Status.MODEL_ERR)
      
    ft = time.time()
    g_logger.info('Request:{}, ----Handle Time: {}'.format(req_id, ft - st))
    return make_response(Status.SUCCESS, rh_result)


@app.route('/healthy', methods=["GET"])
def healthy():
    # g_logger.info("I'm alive ............")
    return make_response(Status.SUCCESS)


# if __name__ == '__main__':
#    app.run(host='0.0.0.0', port=8210, debug=False)

#! /usr/bin/env python3
# -*- coding: UTF-8 -*-
import time
import json
import traceback
from uuid import uuid4
from config import Config
from flask import Flask, request
from utility import log_error
from utility.g_logger import g_logger
from common.e_eureka import eureka_register
from utility.utils import make_response, Status
from chinese_essay_grading.essay_grading.content import ContentScorer


if Config.DEPLOY_ENV != 'local':
    eureka_register()

app = Flask(__name__)
model_scorer = ContentScorer()


@app.route('/', methods=['POST'])
def index():
    st = time.time()
    req_id = request.args.get('requestId') or str(uuid4())
    try:
        if not request.json:
            raise TypeError

        answer_text = request.json.get('answer_text')
        if (answer_text is None) or (not isinstance(answer_text, list)):
            raise TypeError

        grade = request.json.get('grade')
        if (grade is None) or (not isinstance(grade, int)):
            raise TypeError
    
        basic_info = request.json.get('basic_info')
        if basic_info is None:
            raise TypeError

        correction_type = request.json.get('correction_type')
        if basic_info is None:
            correction_type = 1
    except TypeError:
        log_error(req_id, Status.PAR_ERROR)
        return make_response(Status.PAR_ERROR)
    except Exception as e:
        log_error(req_id, Status.BAD_REQ, traceback.format_exception(type(e), e, e.__traceback__))
        return make_response(Status.BAD_REQ)

    try:
        con_start = time.time()
        content_result = model_scorer.get_content_result(answer_text, basic_info, grade, correction_type)
        con_stop = time.time()
        g_logger.debug('Request:{}, Content Time: {}'.format(req_id, con_stop - con_start))
    except Exception as e:
        log_error(req_id, Status.MODEL_ERR, traceback.format_exception(type(e), e, e.__traceback__))
        content_result = Config.FAIL_RESULT

    if content_result.get('code') != 1:
        return make_response(Status.MODEL_ERR)

    response_data = content_result['data']
    ft = time.time()
    g_logger.info('Request:{}, Handle Time: {}'.format(req_id, ft - st))
    return make_response(Status.SUCCESS, response_data)

#if __name__ == '__main__':
#    app.run(host='0.0.0.0', port=8989,debug=False)
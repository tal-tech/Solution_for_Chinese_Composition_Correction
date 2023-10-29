#! /usr/bin/env python3
# -*- coding: UTF-8 -*-
import json
from .g_logger import g_logger
from flask import Response


class Status:
    SUCCESS = 'success'    
    BAD_REQ = 'request is not json'
    PAR_ERROR = 'parameters error'
    MODEL_ERR = 'model error'


error_code = {
    'success': 20000,
    'request is not json': 300036001,
    'parameters error': 300036002,
    'model error': 300036003
}


def make_response(msg, data=None):
    if data is None:
        data = {}

    return Response(json.dumps({'msg': msg, 'code': error_code.get(msg), 'data': data}, ensure_ascii=False,
                               ), status=200, content_type='application/json')


def log_error(idx, msg, detail=''):
    return g_logger.error('Request: {} ------ {} ------ {}'.format(idx, msg, detail))


def check_args(sentence_list):
    if not sentence_list or not isinstance(sentence_list, list):
        return False

    return True

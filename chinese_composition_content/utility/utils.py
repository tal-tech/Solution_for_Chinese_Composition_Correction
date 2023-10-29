#! /usr/bin/env python3
# -*- coding: UTF-8 -*-
import json
from .g_logger import g_logger
from flask import Response


class Status:
    SUCCESS = 'success'
    PAR_ERROR = 'the input is incorrect'
    BAD_REQ = 'request is not json'
    MODEL_ERR = 'algorithm parse failed'


error_code = {
    'success': 20000,
    'the input is incorrect': 300036001,
    'request is not json': 300036002,
    'algorithm parse failed': 300036003
}


def make_response(msg, data=None):
    if data is None:
        data = {}

    return Response(json.dumps({'msg': msg, 'code': error_code.get(msg), 'data': data}, ensure_ascii=False,
                               ), status=200, content_type='application/json')


def log_error(idx, msg, detail=''):
    return g_logger.error('Request: {} ------ {} ------ {}'.format(idx, msg, detail))

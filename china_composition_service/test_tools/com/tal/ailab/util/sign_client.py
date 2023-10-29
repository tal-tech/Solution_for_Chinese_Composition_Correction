#!/usr/bin/python
# -*- coding:utf-8 -*-

import base64
import hmac
from hashlib import sha1
import time
import uuid
from com.tal.ailab.util.url_encode import encode
from urllib import parse
import json

__request_body = "request_body"
__application_json = 'application/json'
__application_x_www_form_urlencoded = 'application/x-www-form-urlencoded'


def url_format(parameters):
    param_list = []
    for (k, v) in parameters:
        param_str = '{}={}'.format(k, v)
        param_list.append(param_str)
    string_to_sign = '&'.join(param_list)
    return string_to_sign


def __generate_signature(parameters, access_key_secret):
    sorted_parameters = sorted(parameters.items(), key=lambda parameters : parameters[0])
    string_to_sign = url_format(sorted_parameters)
    secret = access_key_secret + "&"

    # print(secret)
    # print(string_to_sign)
    h = hmac.new(secret.encode('utf-8'), string_to_sign.encode('utf-8'), sha1)
    signature = base64.b64encode(h.digest()).strip()
    signature = str(signature, encoding="utf8")
    signature = encode(signature)
    # signature = bytes(signature, encoding="utf8")
    # print(signature)
    return signature


def get_signature(url_params, body_params, request_method, content_type, access_key_secret):
    signature_nonce = str(uuid.uuid1())

    sign_param = {
        'signature_nonce': signature_nonce
    }

    if body_params is not None and len(body_params) != 0 \
            and (request_method == 'POST' or request_method == 'PATCH' or request_method == 'PUT'):
        if content_type == __application_x_www_form_urlencoded:
            sign_param[__request_body] = parse.urlencode(body_params)
        else:
            sign_param[__request_body] = json.dumps(body_params)

    for key in url_params.keys():
        sign_param[key] = url_params[key]

    signature = __generate_signature(sign_param, access_key_secret)
    # print(signature_nonce)
    # print(signature)
    return signature, signature_nonce




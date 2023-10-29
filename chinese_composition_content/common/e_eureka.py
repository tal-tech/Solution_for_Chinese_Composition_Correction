#! /usr/bin/env python3
# -*- coding: UTF-8 -*-
import os
import sys
import time
import socket
import signal
from functools import reduce
from threading import Thread
from config import Config
from utility.g_logger import g_logger
import py_eureka_client.eureka_client as eureka_client

RETRY=True
SERVER_PORT = 8003
HEART_BEAT_INTERVAL = 3

app_name = Config.APP_NAME
SERVER_HOST = Config.SERVER_HOST


def __eureka_register(MY_SERVER_PORT):
    try:
        if eureka_client.get_discovery_client() != None:
            return
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        hostname = socket.gethostname()
        #ss = hostname.split('-')[:-2]
        #global SERVER_HOST
        #SERVER_HOST = reduce(lambda x, y: x + '-' + y, ss)
        instance_id = "{}:{}:{}".format(hostname, app_name.lower(), MY_SERVER_PORT)

        eureka_client.init(eureka_server=os.environ.get("EUREKA_URL") or
                            "http://AILab:PaaS@eureka-dev.facethink.com/eureka/",
                           app_name=app_name,
                           # 当前组件的主机名，可选参数，如果不填写会自动计算一个，如果服务和 eureka 服务器部署在同一台机器，请必须填写，否则会计算出 127.0.0.1
                           # instance_host=MyConfig.MY_SERVER_HOST,
                           instance_id=instance_id,
                           instance_port=MY_SERVER_PORT,
                           instance_host=SERVER_HOST,
                           renewal_interval_in_secs=HEART_BEAT_INTERVAL,
                           duration_in_secs=10,
                           # 调用其他服务时的高可用策略，可选，默认为随机
                           ha_strategy=eureka_client.HA_STRATEGY_RANDOM)
    except Exception as e:
        app.logger.error('Init eureka server wrong, the error message is {}, the port is {}',
                         {str(e), MY_SERVER_PORT})


def eureka_stop(*args, **kargs):
    global RETRY
    RETRY = False

def eureka_register():
    global RETRY
    signal.signal(signal.SIGINT, eureka_stop)
    signal.signal(signal.SIGTERM, eureka_stop)
    signal.signal(signal.SIGABRT, eureka_stop)

    def h():
        while RETRY:
            __eureka_register(SERVER_PORT)
            time.sleep(HEART_BEAT_INTERVAL)

        eureka_client.stop()
        os.kill(os.getpid(), signal.SIGKILL)

    t = Thread(target=lambda: h())
    t.start()
#! /usr/bin/env python3
# -*- coding: UTF-8 -*-
import os
import logging


class Config:

    BASE_FOLDER = os.path.abspath(os.path.dirname(__file__))

    LOG_LEVEL = logging.DEBUG
    if os.environ.get('LOG_LEVEL') != "DEBUG":
        LOG_LEVEL = logging.INFO

    DEPLOY_ENV = os.environ.get('DEPLOY_ENV') or 'local'

    PORT = os.environ.get('PORT') or 8210
    EUREKA_APP_NAME = os.environ.get('EUREKA_APP_NAME') or 'CH-COM-RHETORIC'
    EUREKA_HOST_NAME = os.environ.get('EUREKA_HOST_NAME') or 'ch-com-rhetoric'
    EUREKA_URL = os.environ.get('EUREKA_URL') or 'http://AILab:PaaS@godhand-eureka-master:8761/eureka/,http:' \
                                                 '//AILab:PaaS@godhand-eureka-slave1:8761/eureka/,http:' \
                                                 '//AILab:PaaS@godhand-eureka-slave2:8761/eureka/'


if __name__ == '__main__':

    print(Config.BASE_FOLDER)

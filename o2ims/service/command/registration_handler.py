# Copyright (C) 2021-2022 Wind River Systems, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

# import time
import json
# import asyncio
# import requests

from urllib.parse import urlparse
from retry import retry

from o2common.service.unit_of_work import AbstractUnitOfWork
from o2common.config import config, conf
from o2common.service.command.handler import get_https_conn_default
from o2common.service.command.handler import get_http_conn
from o2common.service.command.handler import get_https_conn_selfsigned
from o2common.service.command.handler import post_data
import ssl
from o2ims.domain import commands
from o2ims.domain.subscription_obj import NotificationEventEnum

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


def registry_to_smo(
    cmd: commands.Register2SMO,
    uow: AbstractUnitOfWork,
):
    logger.info('In registry_to_smo')
    data = cmd.data
    logger.info('The Register2SMO notificationEventType is {}'.format(
        data.notificationEventType))
    with uow:
        ocloud = uow.oclouds.get(data.id)
        if ocloud is None:
            return
        logger.debug('O-Cloud Global UUID: {}'.format(ocloud.globalCloudId))
        ocloud_dict = ocloud.serialize()
        if data.notificationEventType == NotificationEventEnum.CREATE:
            register_smo(uow, ocloud_dict)


class RegIMSToSMOExp(Exception):
    def __init__(self, value):
        self.value = value


def register_smo(uow, ocloud_data):
    call_res, status = call_smo(ocloud_data)
    logger.debug('Call SMO response is {}'.format(call_res))
    if call_res is True:
        logger.info('Register to smo success response is {}'.format(status))
    else:
        raise RegIMSToSMOExp('Register o2ims to SMO failed')
    # TODO: record the result for the smo register


# def retry(fun, max_tries=2):
#     for i in range(max_tries):
#         try:
#             time.sleep(5*i)
#             # await asyncio.sleep(5*i)
#             res = fun()
#             logger.debug('retry function result: {}'.format(res))
#             return res
#         except Exception:
#             continue


@retry((ConnectionRefusedError), tries=2, delay=2)
def call_smo(reg_data: dict):
    smo_token = conf.DEFAULT.smo_token_data
    smo_token_info = {
        'iss': 'o2ims',
        'aud': 'smo',
        'smo_token_payload': smo_token,
        'smo_token_type': 'jwt',
        'smo_token_expiration': '',
        'smo_token_algo': 'RS256'
    }

    callback_data = json.dumps({
        'globalCloudId': reg_data['globalCloudId'],
        'oCloudId': reg_data['oCloudId'],
        'IMS_EP': config.get_api_url(),
        'smo_token_data': smo_token_info
    })
    logger.info('URL: {}, data: {}'.format(
        conf.DEFAULT.smo_register_url, callback_data))
    o = urlparse(conf.DEFAULT.smo_register_url)
    if o.scheme == 'https':
        conn = get_https_conn_default(o.netloc)
    else:
        conn = get_http_conn(o.netloc)

    try:
        return post_data(conn, o.path, callback_data)
    except ssl.SSLCertVerificationError as e:
        logger.info('Register to smo with well-known ca failed: {}'.format(e))
        if 'self signed' in str(e):
            conn = get_https_conn_selfsigned(o.netloc)
            try:
                return post_data(conn, o.path, callback_data)
            except Exception as e:
                logger.info(
                    'Register to smo with self-signed ca failed: {}'.format(e))
                # TODO: write the status to extension db table.
                return False, None
        return False, None
    except Exception as e:
        logger.critical('Register to smo except: {}'.format(e))
        return False, None

# Copyright (C) 2021 Wind River Systems, Inc.
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
import http.client
from urllib.parse import urlparse
from retry import retry

from o2common.service.unit_of_work import AbstractUnitOfWork
from o2common.config import config, conf

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
        logger.debug('O-Cloud Global UUID: {}'.format(ocloud.globalcloudId))
        ocloud_dict = ocloud.serialize()
        if data.notificationEventType == NotificationEventEnum.CREATE:
            register_smo(uow, ocloud_dict)


def register_smo(uow, ocloud_data):
    call_res = call_smo(ocloud_data)
    logger.debug('Call SMO response is {}'.format(call_res))
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
        'consumerSubscriptionId': reg_data['globalcloudId'],
        'notificationEventType': 'CREATE',
        'objectRef': config.get_api_url(),
        'postObjectState': reg_data,
        'smo_token_data': smo_token_info
    })
    logger.info('URL: {}, data: {}'.format(
        conf.DEFAULT.smo_register_url, callback_data))
    o = urlparse(conf.DEFAULT.smo_register_url)
    conn = http.client.HTTPConnection(o.netloc)
    headers = {'Content-type': 'application/json'}
    conn.request('POST', o.path, callback_data, headers)
    resp = conn.getresponse()
    data = resp.read().decode('utf-8')
    # json_data = json.loads(data)
    if resp.status == 202 or resp.status == 200:
        logger.info('Registrer to SMO successed, response code {} {}, data {}'.
                    format(resp.status, resp.reason, data))
        return True
    logger.error('Response code is: {}'.format(resp.status))
    return False

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
from o2common.config import config
from o2ims.domain import commands
from o2ims.domain.subscription_obj import RegistrationStatusEnum

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


def registry_to_smo(
    cmd: commands.Register2SMO,
    uow: AbstractUnitOfWork,
):
    logger.info('In registry_to_smo')
    data = cmd.data
    logger.info('The Register2SMO all is {}'.format(data.all))
    if data.all:
        regs = uow.registrations.list()
        for reg in regs:
            reg_data = reg.serialize()
            logger.debug('Registration: {}'.format(reg_data['registrationId']))

            register_smo(uow, reg_data)
    else:
        with uow:
            reg = uow.registrations.get(data.id)
            if reg is None:
                return
            logger.debug('Registration: {}'.format(reg.registrationId))
            reg_data = reg.serialize()
            register_smo(uow, reg_data)


def register_smo(uow, reg_data):
    call_res = call_smo(reg_data)
    logger.debug('Call SMO response is {}'.format(call_res))
    if call_res:
        reg = uow.registrations.get(reg_data['registrationId'])
        if reg is None:
            return
        reg.status = RegistrationStatusEnum.NOTIFIED
        logger.debug('Updating Registration: {}'.format(
            reg.registrationId))
        uow.registrations.update(reg)
        uow.commit()


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
    callback_data = json.dumps({
        'consumerSubscriptionId': reg_data['registrationId'],
        'imsUrl': config.get_api_url()
    })
    logger.info('URL: {}, data: {}'.format(
        reg_data['callback'], callback_data))

    o = urlparse(reg_data['callback'])
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

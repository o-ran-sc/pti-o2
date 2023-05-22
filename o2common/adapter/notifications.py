# Copyright (C) 2021-2023 Wind River Systems, Inc.
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
# pylint: disable=too-few-public-methods
import abc

from o2common.config import config, conf
from o2common.service.command.handler import SMOClient

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)

SMO_O2_ENDPOINT = config.get_smo_o2endpoint()


class AbstractNotifications(abc.ABC):
    @abc.abstractmethod
    def send(self, url, message):
        raise NotImplementedError


class NoneNotifications(AbstractNotifications):
    def __init__(self):
        pass

    def send(self, url, message):
        pass


class SmoO2Notifications(AbstractNotifications):
    def __init__(self, smoO2Endpoint=SMO_O2_ENDPOINT):
        self.smoO2Endpoint = smoO2Endpoint

    def send(self, url, message):
        pass


class SmoNotifications(AbstractNotifications):
    def __init__(self):
        logger.debug('In SmoNotifications')
        if conf.PUBSUB.SMO_AUTH_URL is not None \
                and conf.PUBSUB.SMO_AUTH_URL != '':
            logger.debug(f'SMO_AUTH_URL is {conf.PUBSUB.SMO_AUTH_URL}')
            self.smo_client = SMOClient(
                conf.PUBSUB.SMO_CLIENT_ID, conf.PUBSUB.SMO_AUTH_URL,
                conf.PUBSUB.SMO_USERNAME, conf.PUBSUB.SMO_PASSWORD,
                use_oauth=True)
        else:
            self.smo_client = SMOClient()

    def send(self, url, message):
        try:
            return self.smo_client.post(url, message)
        except Exception as e:
            logger.critical('Notify except: {}'.format(e))
            return False

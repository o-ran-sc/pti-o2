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

# client talking to Stx standalone

from o2ims.service.client.base_client import BaseClient
from typing import List
# Optional,  Set
from o2ims.domain import stx_object as ocloudModel
from o2ims import config

# from dcmanagerclient.api import client
from cgtsclient.client import get_client
import logging
logger = logging.getLogger(__name__)

class StxSaOcloudClient(BaseClient):
    def __init__(self, driver=None):
        super().__init__()
        self.driver = driver if driver else StxSaClientImp()

    # def list(self) -> List[ocloudModel.StxGenericModel]:
    #     return self._list()

    # def get(self, id) -> ocloudModel.StxGenericModel:
    #     return self._get(id)

    def _get(self, id) -> ocloudModel.StxGenericModel:
        return self.driver.getInstanceInfo()

    def _list(self):
        return [self.driver.getInstanceInfo()]


class StxSaResourcePoolClient(BaseClient):
    def __init__(self):
        super().__init__()
        self.driver = StxSaClientImp()

    def _get(self, id) -> ocloudModel.StxGenericModel:
        return self.driver.getInstanceInfo()

    def _list(self):
        return [self.driver.getInstanceInfo()]


class StxSaDmsClient(BaseClient):
    def __init__(self):
        super().__init__()
        self.driver = StxSaClientImp()

    def _get(self, id) -> ocloudModel.StxGenericModel:
        return self.driver.getK8sDetail(id)

    def _list(self):
        return self.driver.getK8sList()

class StxPserverClient(BaseClient):
    def __init__(self):
        super().__init__()
        self.driver = StxSaClientImp()
    
    def _get(self, id) -> ocloudModel.StxGenericModel:
        return self.driver.getPserver(id)
    
    def _list(self) -> List[ocloudModel.StxGenericModel]:
        return self.driver.getPserverList()

# internal driver which implement client call to Stx Standalone instance

class StxSaClientImp(object):
    def __init__(self, stx_client=None):
        super().__init__()
        self.stxclient = stx_client if stx_client else self.getStxClient()

    def getStxClient():
        os_client_args = config.get_stx_access_info()
        config_client = get_client(**os_client_args)
        return config_client

    def getInstanceInfo(self) -> ocloudModel.StxGenericModel:
        systems = self.stxclient.isystem.list()
        logger.debug("systems:"+str(systems[0].to_dict()))
        return ocloudModel.StxGenericModel(systems[0]) if systems else None

    def getPserverList(self) -> List[ocloudModel.StxGenericModel]:
        hosts = self.stxclient.ihost.list()
        logger.debug("host 1:"+ str(hosts[0].to_dict()))
        return [ocloudModel.StxGenericModel(self._hostconverter(host)) for host in hosts if host]

    def getPserver(self, id) -> ocloudModel.StxGenericModel:
        host = self.stxclient.ihost.get(id)
        logger.debug("host:"+ str(host.to_dict()))
        return ocloudModel.StxGenericModel(self._hostconverter(host))

    def getK8sList(self) -> List[ocloudModel.StxGenericModel]:
        raise NotImplementedError

    def getK8sDetail(self, id) -> ocloudModel.StxGenericModel:
        raise NotImplementedError

    @staticmethod
    def _hostconverter(host):
        setattr(host, "name", host.hostname)
        return host
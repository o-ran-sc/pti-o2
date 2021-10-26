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

from service.client.base_client import BaseClient
from typing import List
# Optional,  Set
from o2ims.domain import stx_object as ocloudModel
from o2ims import config


class StxSaOcloudClient(BaseClient):
    def __init__(self):
        super().__init__()
        self.driver = StxSaClientImp()

    # def list(self) -> List[ocloudModel.StxGenericModel]:
    #     return self._list()

    # def get(self, id) -> ocloudModel.StxGenericModel:
    #     return self._get(id)

    def _get(self, id) -> ocloudModel.StxGenericModel:
        raise self.driver.getInstanceInfo()

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

# internal driver which implement client call to Stx Standalone instance

# from keystoneauth1.identity import v3
# from keystoneauth1 import session
# # from keystoneclient.v3 import ksclient
# from starlingxclient.v3 import stxclient


class StxSaClientImp(object):
    def __init__(self, access_info=None) -> None:
        super().__init__()
        self.access_info = access_info
        if self.access_info is None:
            self.access_info = config.get_stx_access_info()
        # self.auth = auth = v3.Password(
        #     auth_url="http://example.com:5000/v3", username="admin",
        #     password="password", project_name="admin",
        #     user_domain_id="default", project_domain_id="default")
        # self.session = sess = session.Session(auth=auth)
        # # self.keystone = ksclient.Client(session=sess)
        # self.stx = stxclient.Client(session=sess)

    def getInstanceInfo(self) -> ocloudModel.StxGenericModel:
        raise NotImplementedError

    def getK8sList(self) -> List[ocloudModel.StxGenericModel]:
        raise NotImplementedError

    def getK8sDetail(self, id) -> ocloudModel.StxGenericModel:
        raise NotImplementedError

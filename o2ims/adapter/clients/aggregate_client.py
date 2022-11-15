# Copyright (C) 2022 Wind River Systems, Inc.
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
import uuid
from typing import List

from o2common.service.client.base_client import BaseClient
from o2ims.domain import stx_object as ocloudModel
from o2ims.domain.resource_type import ResourceTypeEnum

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


class ComputeAggClient(BaseClient):
    def __init__(self, driver=None):
        super().__init__()
        self.driver = AggClientImp()

    def _get(self, id) -> ocloudModel.StxGenericModel:
        return self.driver.getComputeList(res_pool=self._pool_id)[0]

    def _list(self, **filters):
        return self.driver.getComputeList(res_pool=self._pool_id)

    def _set_stx_client(self):
        pass


class NetworkAggClient(BaseClient):
    def __init__(self, driver=None):
        super().__init__()
        self.driver = AggClientImp()

    def _get(self, id) -> ocloudModel.StxGenericModel:
        return self.driver.getNetworkList(res_pool=self._pool_id)[0]

    def _list(self, **filters):
        return self.driver.getNetworkList(res_pool=self._pool_id)

    def _set_stx_client(self):
        pass


class StorageAggClient(BaseClient):
    def __init__(self, driver=None):
        super().__init__()
        self.driver = AggClientImp()

    def _get(self, id) -> ocloudModel.StxGenericModel:
        return self.driver.getStorageList(res_pool=self._pool_id)[0]

    def _list(self, **filters):
        return self.driver.getStorageList(res_pool=self._pool_id)

    def _set_stx_client(self):
        pass


class UndefinedAggClient(BaseClient):
    def __init__(self, driver=None):
        super().__init__()
        self.driver = AggClientImp()

    def _get(self, id) -> ocloudModel.StxGenericModel:
        return self.driver.getUndefinedList(res_pool=self._pool_id)[0]

    def _list(self, **filters):
        return self.driver.getUndefinedList(res_pool=self._pool_id)

    def _set_stx_client(self):
        pass


class AggClientImp(object):
    def __init__(self):
        super().__init__()

    def getComputeList(self, **filters) -> List[ocloudModel.StxGenericModel]:
        compute = ComputeAggregate(filters['res_pool'])
        return [ocloudModel.StxGenericModel(
            ResourceTypeEnum.COMPUTE_AGGREGATE, compute)]

    def getNetworkList(self, **filters) -> List[ocloudModel.StxGenericModel]:
        network = NetworkAggregate(filters['res_pool'])
        return [ocloudModel.StxGenericModel(
            ResourceTypeEnum.NETWORK_AGGREGATE, network)]

    def getStorageList(self, **filters) -> List[ocloudModel.StxGenericModel]:
        storage = StorageAggregate(filters['res_pool'])
        return [ocloudModel.StxGenericModel(
            ResourceTypeEnum.STORAGE_AGGREGATE, storage)]

    def getUndefinedList(self, **filters) -> List[ocloudModel.StxGenericModel]:
        undefined = UndefinedAggregate(filters['res_pool'])
        return [ocloudModel.StxGenericModel(
            ResourceTypeEnum.UNDEFINED_AGGREGATE, undefined)]


class Aggregate:
    def __init__(self, res_pool_id: str, name: str) -> None:
        self.name = name
        setattr(self, 'name', self.name)
        setattr(self, 'uuid',
                uuid.uuid3(uuid.NAMESPACE_URL, res_pool_id + self.name))
        setattr(self, 'updated_at', None)
        setattr(self, 'created_at', None)

    def to_dict(self):
        return {}


class ComputeAggregate(Aggregate):
    def __init__(self, res_pool_id: str) -> None:
        super().__init__(res_pool_id, 'compute_aggregate')


class NetworkAggregate(Aggregate):
    def __init__(self, res_pool_id: str) -> None:
        super().__init__(res_pool_id, 'network_aggregate')


class StorageAggregate(Aggregate):
    def __init__(self, res_pool_id: str) -> None:
        super().__init__(res_pool_id, 'storage_aggregate')


class UndefinedAggregate(Aggregate):
    def __init__(self, res_pool_id: str) -> None:
        super().__init__(res_pool_id, 'undefined_aggregate')

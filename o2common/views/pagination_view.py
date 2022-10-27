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

import math
from typing import List, Tuple

from o2common.domain.base import Serializer

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


class Pagination:
    def __init__(self, **kwargs) -> None:
        # filter key should be the same with database name
        self.pagination_kwargs = {}
        self.limit = int(kwargs['per_page']) if 'per_page' in kwargs else 30
        self.page = int(kwargs['page']) if 'page' in kwargs else 1
        if self.page < 1:
            self.page = 1
        self.start = (self.page - 1) * self.limit
        self.pagination_kwargs['limit'] = self.limit
        self.pagination_kwargs['start'] = self.start

    def get_pagination(self):
        return self.pagination_kwargs

    def get_result(self, ret: Tuple[int, List[Serializer]]):
        count = ret[0]
        logger.info('List count: {}'.format(count))
        ret_list = ret[1]
        page_total = int(math.ceil(count/self.limit)
                         ) if count > self.limit else 1
        result = {
            "count": count,
            "page_total": page_total,
            "page_current": self.page,
            "per_page": self.limit,
            "results": [r.serialize() for r in ret_list]
        }
        return result

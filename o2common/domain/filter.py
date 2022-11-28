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

from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy import or_

from o2ims.domain.alarm_obj import AlarmEventRecord
from o2ims.domain.ocloud import Ocloud

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


def gen_orm_filter(obj: ColumnElement, filter_str: str):
    logger.debug(filter_str)
    if not filter_str:
        return []
    filter_without_space = filter_str.strip()
    items = filter_without_space.split(';')

    filter_list = list()
    for i in items:
        item = i.strip(' ()')
        filter_expr = item.split(',')
        if len(filter_expr) < 3:
            continue
        filter_op = filter_expr[0].strip()
        filter_key = filter_expr[1].strip()
        if filter_key == 'objectType':
            continue
        filter_vals = filter_expr[2:]
        filter_list.extend(toFilterArgs(
            filter_op, obj, filter_key, filter_vals))
    logger.debug('Filter list length: %d' % len(filter_list))
    return filter_list


def toFilterArgs(operation: str, obj: ColumnElement, key: str, values: list):
    # if not hasattr(obj, key):
    #     logger.warning('Filter attrName %s not in Object %s' %
    #                    (key, str(obj)))
    #     raise KeyError(
    #         'Filter attrName {} not in the Object'.format(key))

    # if operation in ['eq', 'neq', 'gt', 'lt', 'gte', 'lte']:
    #     if len(values) != 1:
    #         raise KeyError(
    #             'Filter operation one {} is only support one value'.
    #             format(operation))
    # elif operation in ['in', 'nin', 'cont', 'ncont']:
    #     if len(values) == 0:
    #         raise KeyError('Filter operation {} value is needed'.
    #                        format(operation))
    # else:
    #     raise KeyError('Filter operation {} not support'.format(operation))
    key = transfer_filter_attr_name_in_special(obj, key)

    ll = list()
    if operation == 'eq':
        val = values[0]
        if val.lower() == 'null':
            val = None
        ll.append(getattr(obj, key) == val)
    elif operation == 'neq':
        val = values[0]
        if val.lower() == 'null':
            val = None
        ll.append(getattr(obj, key) != val)
    elif operation == 'gt':
        val = values[0]
        ll.append(getattr(obj, key) > val)
    elif operation == 'lt':
        val = values[0]
        ll.append(getattr(obj, key) < val)
    elif operation == 'gte':
        val = values[0]
        ll.append(getattr(obj, key) >= val)
    elif operation == 'lte':
        val = values[0]
        ll.append(getattr(obj, key) <= val)
    elif operation == 'in':
        ll.append(getattr(obj, key).in_(values))
    elif operation == 'nin':
        ll.append(~getattr(obj, key).in_(values))
    elif operation == 'cont':
        val_list = list()
        for val in values:
            val_list.append(getattr(obj, key).contains(val))
        ll.append(or_(*val_list))
    elif operation == 'ncont':
        val_list = list()
        for val in values:
            val_list.append(getattr(obj, key).contains(val))
        ll.append(~or_(*val_list))
    return ll


def transfer_filter_attr_name_in_special(obj: ColumnElement, filter_key: str):
    if obj == AlarmEventRecord:
        if filter_key == 'resourceTypeID':
            filter_key = 'resourceTypeId'
        elif filter_key == 'resourceID':
            filter_key = 'resourceId'
        elif filter_key == 'alarmDefinitionID':
            filter_key = 'alarmDefinitionId'
        elif filter_key == 'probableCauseID':
            filter_key = 'probableCauseId'
    elif obj == Ocloud:
        if filter_key == 'globalcloudId':
            filter_key = 'globalCloudId'
    return filter_key

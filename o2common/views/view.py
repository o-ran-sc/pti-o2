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

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


def gen_filter(obj: ColumnElement, filter_str: str):
    if filter_str == '':
        return []
    filter_without_space = filter_str.replace(" ", "")
    items = filter_without_space.split(';')

    filter_list = list()
    for i in items:
        if '(' in i:
            i = i.replace("(", "")
        if ')' in i:
            i = i.replace(")", "")
        filter_expr = i.split(',')
        if len(filter_expr) < 3:
            continue
        filter_op = filter_expr[0]
        filter_key = filter_expr[1]
        filter_vals = filter_expr[2:]
        filter_list.extend(toFilterArgs(
            filter_op, obj, filter_key, filter_vals))
    logger.info('Filter list length: %d' % len(filter_list))
    return filter_list


def toFilterArgs(operation: str, obj: ColumnElement, key: str, values: list):
    if not hasattr(obj, key):
        logger.warning('Filter attrName %s not in Object %s.' %
                       (key, str(obj)))
        return []

    ll = list()
    if operation == 'eq':
        for val in values:
            if val.lower() == 'null':
                val = None
            ll.append(getattr(obj, key) == val)
    elif operation == 'neq':
        for val in values:
            if val.lower() == 'null':
                val = None
            ll.append(getattr(obj, key) != val)
    elif operation == 'gt':
        for val in values:
            ll.append(getattr(obj, key) > val)
    elif operation == 'lt':
        for val in values:
            ll.append(getattr(obj, key) < val)
    elif operation == 'gte':
        for val in values:
            ll.append(getattr(obj, key) >= val)
    elif operation == 'lte':
        for val in values:
            ll.append(getattr(obj, key) <= val)
    elif operation == 'in':
        pass
    elif operation == 'nin':
        pass
    elif operation == 'count':
        pass
    elif operation == 'ncount':
        pass
    else:
        raise KeyError('Filter operation value not support.')

    return ll

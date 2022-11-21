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

# import re
from sqlalchemy.sql.elements import ColumnElement

from o2common.views.route_exception import BadRequestException
from o2common.domain.filter import gen_orm_filter, \
    transfer_filter_attr_name_in_special

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


def gen_filter(obj: ColumnElement, filter_str: str):
    check_filter(obj, filter_str)
    try:
        filter_list = gen_orm_filter(obj, filter_str)
    except KeyError as e:
        raise BadRequestException(e.args[0])
    return filter_list


# The regular expressions testing example put on here
# (neq,testkey,value-1)
# (neq,testkey,value-1,value-2)
# (gt,hello,1)
# (gte,world,2)
# (lt,testlt,notint)
# (ncont,key1,v1,v_2)
# (gt,hello,1);(ncont,world,val1,val-2)
# (eq,wrong,60cba7be-e2cd-3b8c-a7ff-16e0f10573f9)
# (eq,description,value key)
def check_filter(obj: ColumnElement, filter_str: str):
    if not filter_str:
        return
    # pattern = r'^(\((eq|neq|gt|lt|gte|lte){1},\w+,[\w -\.]+\)\;?|' +\
    #     r'\((in|nin|cont|ncont){1},\w*(,[\w -\.]*)*\)\;?)+'
    # result = re.match(pattern, filter_str)
    # logger.debug('filter: {} match result is {}'.format(filter_str, result))
    # if not result:
    #     raise BadRequestException(
    #         'filter value format is invalid')
    check_filter_attribute(obj, filter_str)


def check_filter_attribute(obj: ColumnElement, filter_str: str):
    # filter_without_space = filter_str.replace(" ", "")
    filter_without_space = filter_str.strip(' ()')
    logger.debug(
        f"filter_str: {filter_str}, stripped: {filter_without_space}")
    items = filter_without_space.split(';')

    for i in items:
        # if '(' in i:
        #     i = i.replace("(", "")
        # if ')' in i:
        #     i = i.replace(")", "")
        filter_expr = i.split(',')
        if len(filter_expr) < 3:
            raise BadRequestException(
                'ignore invalid filter {}'.format(i))
            continue
        filter_op = filter_expr[0].strip()
        filter_key = filter_expr[1].strip()
        filter_vals = filter_expr[2:]
        if filter_op in ["eq", "neq", "gt", "lt", "gte", "lte"]:
            if len(filter_vals) != 1:
                raise BadRequestException(
                    "Found {} values: {} while only single value"
                    " is allowed for operation {}".format(
                        len(filter_vals), filter_vals, filter_op)
                )
        elif filter_op not in ["in", "nin", "cont", "ncont"]:
            raise BadRequestException(
                'Filter operation {} is invalid'.format(filter_op)
            )
        else:
            pass
        filter_key = transfer_filter_attr_name_in_special(obj, filter_key)
        if not hasattr(obj, filter_key):
            raise BadRequestException(
                'Filter attrName {} is invalid'.format(filter_key))

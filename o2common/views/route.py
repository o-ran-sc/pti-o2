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

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# from collections import OrderedDict
from functools import wraps
# from six import iteritems

from flask import request

from flask_restx import Namespace
from flask_restx._http import HTTPStatus
from flask_restx.marshalling import marshal_with, marshal
from flask_restx.utils import merge
from flask_restx.mask import Mask  # , apply as apply_mask
from flask_restx.model import Model
from flask_restx.fields import List, Nested, String
from flask_restx.utils import unpack

from o2common.views.route_exception import BadRequestException

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


class O2Namespace(Namespace):

    def __init__(self, name, description=None, path=None, decorators=None,
                 validate=None, authorizations=None, ordered=False, **kwargs):
        super().__init__(name, description, path, decorators,
                         validate, authorizations, ordered, **kwargs)

    def marshal_with(
        self, fields, as_list=False, code=HTTPStatus.OK, description=None,
        **kwargs
    ):
        """
        A decorator specifying the fields to use for serialization.

        :param bool as_list: Indicate that the return type is a list \
            (for the documentation)
        :param int code: Optionally give the expected HTTP response \
            code if its different from 200

        """

        def wrapper(func):
            doc = {
                "responses": {
                    str(code): (description, [fields], kwargs)
                    if as_list
                    else (description, fields, kwargs)
                },
                "__mask__": kwargs.get(
                    "mask", True
                ),  # Mask values can't be determined outside app context
            }
            func.__apidoc__ = merge(getattr(func, "__apidoc__", {}), doc)
            return o2_marshal_with(fields, ordered=self.ordered,
                                   **kwargs)(func)

        return wrapper


class o2_marshal_with(marshal_with):
    def __init__(
        self, fields, envelope=None, skip_none=False, mask=None, ordered=False
    ):
        """
        :param fields: a dict of whose keys will make up the final
                       serialized response output
        :param envelope: optional key that will be used to envelop the
                       serialized response
        """
        self.fields = fields
        self.envelope = envelope
        self.skip_none = skip_none
        self.ordered = ordered
        self.mask = Mask(mask, skip=True)

    def __call__(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            resp = f(*args, **kwargs)

            req_args = request.args
            mask = self._gen_mask_from_selector(**req_args)
            if mask == '':
                mask = self.mask

            # if has_request_context():
            # mask_header = current_app.config["RESTX_MASK_HEADER"]
            # mask = request.headers.get(mask_header) or mask
            if isinstance(resp, tuple):
                data, code, headers = unpack(resp)
                return (
                    marshal(
                        data,
                        self.fields,
                        self.envelope,
                        self.skip_none,
                        mask,
                        self.ordered,
                    ),
                    code,
                    headers,
                )
            else:
                return marshal(
                    resp, self.fields, self.envelope, self.skip_none, mask,
                    self.ordered
                )

        return wrapper

    def _gen_mask_from_selector(self, **kwargs) -> str:
        mask_val = ''
        if 'all_fields' in kwargs:
            all_fields_without_space = kwargs['all_fields'].replace(" ", "")
            logger.debug('all_fields selector value is {}'.format(
                all_fields_without_space))
            # all_fields = all_fields_without_space.lower()
            # if 'true' == all_fields:
            selector = self.__gen_selector_from_model_with_value(
                self.fields)
            mask_val = self.__gen_mask_from_selector(selector)

        elif 'fields' in kwargs and kwargs['fields'] != '':
            fields_without_space = kwargs['fields'].replace(" ", "")

            # filters = fields_without_space.split(',')

            # mask_val_list = []
            # for f in filters:
            #     if '/' in f:
            #         a = self.__gen_mask_tree(f)
            #         mask_val_list.append(a)
            #         continue
            #     mask_val_list.append(f)
            # mask_val = '{%s}' % ','.join(mask_val_list)
            selector = {}

            self.__update_selector_value(selector, fields_without_space, True)
            self.__set_default_mask(selector)

            mask_val = self.__gen_mask_from_selector(selector)

        elif 'exclude_fields' in kwargs and kwargs['exclude_fields'] != '':
            exclude_fields_without_space = kwargs['exclude_fields'].replace(
                " ", "")

            selector = self.__gen_selector_from_model_with_value(
                self.fields)

            self.__update_selector_value(
                selector, exclude_fields_without_space, False)
            self.__set_default_mask(selector)

            mask_val = self.__gen_mask_from_selector(selector)
        elif 'exclude_default' in kwargs and kwargs['exclude_default'] != '':
            exclude_default_without_space = kwargs['exclude_default'].replace(
                " ", "")
            exclude_default = exclude_default_without_space.lower()
            if 'true' == exclude_default:
                mask_val = '{}'

        else:
            mask_val = ''

        return mask_val

    def __gen_mask_tree(self, field: str) -> str:

        f = field.split('/', 1)
        if len(f) > 1:
            s = self.__gen_mask_tree(f[1])
            return '%s%s' % (f[0], s)
        else:
            return '{%s}' % f[0]

    def __gen_selector_from_model_with_value(
            self, model: Model, default_val: bool = True) -> dict:
        selector = dict()
        for i in model:
            if type(model[i]) is List:
                if type(model[i].container) is String:
                    selector[i] = default_val
                    continue
                selector[i] = self.__gen_selector_from_model_with_value(
                    model[i].container.model, default_val)
                continue
            elif type(model[i]) is Nested:
                selector[i] = self.__gen_selector_from_model_with_value(
                    model[i].model, default_val)
            selector[i] = default_val
        return selector

    def __update_selector_value(self, selector: dict, filter: str,
                                val: bool):
        fields = filter.split(',')
        for f in fields:
            if '/' in f:
                self.__update_selector_tree_value(selector, f, val)
                continue
            if f not in self.fields:
                raise BadRequestException(
                    'Selector attribute {} not found'.format(f))
            selector[f] = val

    def __update_selector_tree_value(self, m: dict, filter: str, val: bool):
        filter_list = filter.split('/', 1)
        if filter_list[0] not in m:
            m[filter_list[0]] = dict()
        if len(filter_list) > 1:
            self.__update_selector_tree_value(
                m[filter_list[0]], filter_list[1], val)
            return
        m[filter_list[0]] = val

    def __gen_mask_from_selector(self, fields: dict) -> str:
        mask_li = list()
        for k, v in fields.items():
            if type(v) is dict:
                s = self.__gen_mask_from_selector(v)
                mask_li.append('%s%s' % (k, s))
                continue
            if v:
                mask_li.append(k)

        return '{%s}' % ','.join(mask_li)

    def __set_default_mask(self, selector: dict, val: bool = True):
        default_selector = str(getattr(self.fields, "__mask__"))[1:-1]
        self.__update_selector_value(selector, default_selector, val)

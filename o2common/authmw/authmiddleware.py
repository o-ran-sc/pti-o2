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

from werkzeug.wrappers import Request, Response
from o2common.helper import o2logging
from o2common.authmw.authprov import auth_definer
from flask_restx._http import HTTPStatus
import json

logger = o2logging.get_logger(__name__)


class AuthRequiredExp(Exception):
    def __init__(self, value):
        self.value = value

    def dictize(self):
        return {
            'WWW-Authenticate': '{}'.format(self.value)}


class AuthProblemDetails():
    def __init__(self, code: int, detail: str, path: str,
                 title=None, instance=None
                 ) -> None:
        self.status = code
        self.detail = detail
        self.type = path
        self.title = title if title is not None else self.getTitle(code)
        self.instance = instance if instance is not None else []

    def getTitle(self, code):
        return HTTPStatus(code).phrase

    def serialize(self):
        details = {}
        for key in dir(self):
            if key == 'ns' or key.startswith('__') or \
                    callable(getattr(self, key)):
                continue
            else:
                details[key] = getattr(self, key)
        return json.dumps(details, indent=True)


class AuthFailureExp(Exception):
    def __init__(self, value):
        self.value = value

    def dictize(self):
        return {
            'WWW-Authenticate': '{}'.format(self.value)}


def _response_wrapper(environ, start_response, header, detail):
    res = Response(headers=header,
                   mimetype='application/json', status=401, response=detail)
    return res(environ, start_response)


def _internal_err_response_wrapper(environ, start_response, detail):
    res = Response(mimetype='application/json', status=500, response=detail)
    return res(environ, start_response)


class authmiddleware():

    '''
    Auth WSGI middleware
    '''

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        logger.debug(__name__ + 'authentication middleware')
        req = Request(environ, populate_request=True, shallow=True)
        auth_token = None
        try:
            auth_header = req.headers.get('Authorization', None)
            if auth_header:
                auth_token = auth_header.split(" ")[1]

                ad = auth_definer('oauth')
                # invoke underlying auth mdw to make k8s/keystone api
                ret = ad.authenticate(auth_token)
                if ret is True:
                    logger.debug(
                        "auth success with oauth token: " + auth_token)
                    try:
                        return self.app(environ, start_response)
                    except Exception as ex:
                        logger.error(
                            'Internal exception happend \
                            ed {}'.format(str(ex)), exc_info=True)
                        prb = AuthProblemDetails(
                            500, 'Internal error.', req.path)
                        return \
                            _internal_err_response_wrapper(
                                environ,
                                start_response, prb.serialize())
                else:
                    raise AuthFailureExp(
                        'Bearer realm="Authentication Failed"')
            else:
                raise AuthRequiredExp('Bearer realm="Authentication Required"')
        except AuthRequiredExp as ex:
            prb = AuthProblemDetails(401, ex.value, req.path)
            return _response_wrapper(environ, start_response,
                                     ex.dictize(), prb.serialize())
        except AuthFailureExp as ex:
            prb = AuthProblemDetails(401, ex.value, req.path)
            return _response_wrapper(environ, start_response,
                                     ex.dictize(), prb.serialize())
        except Exception as ex:
            if auth_token:
                logger.error('Internal exception happended {}'.format(
                    str(ex)), exc_info=True)
                prb = AuthProblemDetails(500, 'Internal error.', req.path)
                return \
                    _internal_err_response_wrapper(
                        environ, start_response, prb.serialize())
            else:
                logger.debug('Auth token missing or not obtained.')
                ex = AuthRequiredExp('Bearer realm="Authentication Required"')
                prb = AuthProblemDetails(401, ex.value, req.path)
                return _response_wrapper(environ, start_response,
                                         ex.dictize(), prb.serialize())

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

logger = o2logging.get_logger(__name__)


class AuthRequiredExp(Exception):
    def __init__(self, value):
        self.value = value

    def dictize(self):
        return {
            'WWW-Authenticate': '{}'.format(self.value)}


class AuthFailureExp(Exception):
    def __init__(self, value):
        self.value = value

    def dictize(self):
        return {
            'WWW-Authenticate': '{}'.format(self.value)}


def _response_wrapper(environ, start_response, header):
    res = Response(headers=header,
                   mimetype='text/plain', status=401)
    return res(environ, start_response)


def _internal_err_response_wrapper(environ, start_response):
    res = Response(mimetype='text/plain', status=500)
    return res(environ, start_response)


class authmiddleware():

    '''
    Auth WSGI middleware
    '''

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        logger.info(__name__ + 'authentication middleware')
        req = Request(environ, populate_request=True, shallow=True)
        try:
            try:
                auth_header = req.headers['Authorization']
            except Exception as ex:
                raise AuthRequiredExp('Bearer realm="Authentication Required"')
            if auth_header:
                auth_token = auth_header.split(" ")[1]

                ad = auth_definer('oauth')
                # invoke underlying auth mdw to make k8s/keystone api
                ret = ad.authenticate(auth_token)
                if ret is True:
                    logger.info(
                        "auth success with oauth token: " + auth_token)
                    try:
                        return self.app(environ, start_response)
                    except Exception as ex:
                        logger.error(
                            'Internal exception happend \
                            ed {}'.format(str(ex)), exc_info=True)
                        return \
                            _internal_err_response_wrapper(environ,
                                                           start_response)
                else:
                    raise AuthFailureExp(
                        'Bearer realm="Authentication Failed"')
            else:
                raise AuthRequiredExp('Bearer realm="Authentication Required"')
        except AuthRequiredExp as ex:
            return _response_wrapper(environ, start_response, ex.dictize())
        except AuthFailureExp as ex:
            return _response_wrapper(environ, start_response, ex.dictize())
        except Exception as ex:
            logger.error('Internal exception happended {}'.format(
                str(ex)), exc_info=True)
            return _internal_err_response_wrapper(environ, start_response)

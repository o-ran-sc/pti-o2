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

import ssl
import urllib.request
import urllib.parse
import json
from http import HTTPStatus
from requests import post as requests_post
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from jwt import decode as jwt_decode
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from o2common.authmw.exceptions import AuthRequiredExp
from o2common.authmw.exceptions import AuthFailureExp
from o2common.config.config import get_auth_provider, get_review_url
from o2common.config.config import get_reviewer_token
from o2common.config import conf
from o2common.helper import o2logging

ssl._create_default_https_context = ssl._create_unverified_context
logger = o2logging.get_logger(__name__)


# read the conf from config file
auth_prv_conf = get_auth_provider()

try:
    token_review_url = get_review_url()
except Exception:
    raise Exception('Get k8s token review url failed')


class OAuthAuthenticationException(Exception):
    def __init__(self, value):
        self.value = value


class K8SAuthenticaException(Exception):
    def __init__(self, value):
        self.value = value


class K8SAuthorizationException(Exception):
    def __init__(self, value):
        self.value = value


class auth_definer():

    def __init__(self, name):
        super().__init__()
        self.name = name
        if auth_prv_conf == 'k8s':
            self.obj = k8s_auth_provider('k8s')
        else:
            self.obj = oauth2_auth_provider('oauth2')

    def tokenissue(self):
        return self.obj.tokenissue()

    def sanity_check(self):
        return self.obj.sanity_check()

    def authenticate(self, token):
        return self.obj.authenticate(token)

    def __repr__(self) -> str:
        return "<auth_definer: name = %s>" % self.name


class k8s_auth_provider(auth_definer):

    def __init__(self, name):
        self.name = name

    def tokenissue(self, **args2):
        pass

    def sanity_check(self):
        try:
            self.authenticate('faketoken')
        except Exception as ex:
            logger.critical(
                'Failed to bootstrap oauth middleware with exp: ' + str(ex))
            raise Exception(str(ex))

    def authenticate(self, token):
        ''' Call Kubenetes API to authenticate '''
        reviewer_token = get_reviewer_token()
        tokenreview = {
            "kind": "TokenReview",
            "apiVersion": "authentication.k8s.io/v1",
            "metadata": {
                "creationTimestamp": None
            },
            "spec": {
                "token": ""+token
            },
            "status": {
                "user": {}
            }
        }
        datas = json.dumps(tokenreview)
        binary_data = datas.encode('utf-8')
        # 'post' method
        header = {'Authorization': 'Bearer '+reviewer_token,
                  'Content-Type': 'application/json'}
        try:
            req = urllib.request.Request(
                token_review_url, data=binary_data, headers=header)
            response = urllib.request.urlopen(req)
            data = json.load(response)
            if data['status']['authenticated'] is True:
                logger.debug("Authenticated.")
                return True
        except Exception as ex:
            strex = str(ex)
            logger.warning(
                "Invoke K8s API Service Exception happened:" + strex)
            if '403' in strex:
                raise K8SAuthorizationException(
                    'No privilege to perform oauth token check.')
            elif '401' in strex:
                raise K8SAuthenticaException(
                    'Self Authentication failure.')
        return False

    def tokenrevoke(self, **args2):
        return True


class oauth2_auth_provider(auth_definer):
    def __init__(self, name):
        self.name = name

    def _format_public_key(self):
        public_key_string = """-----BEGIN PUBLIC KEY----- \
        %s \
        -----END PUBLIC KEY-----""" % conf.OAUTH2.oauth2_public_key
        return public_key_string

    def _verify_jwt_token_introspect(self, token):
        introspect_endpoint = conf.OAUTH2.oauth2_introspection_endpoint
        client_id = conf.OAUTH2.oauth2_client_id
        client_secret = conf.OAUTH2.oauth2_client_secret
        try:
            response = requests_post(
                introspect_endpoint,
                data={'token': token, 'client_id': client_id},
                auth=HTTPBasicAuth(client_id, client_secret)
            )
        except HTTPError as e:
            logger.error('OAuth2 jwt token introspect verify failed.')
            raise Exception(str(e))
        if response.status_code == HTTPStatus.OK:
            introspection_data = response.json()
            if introspection_data.get('active'):
                logger.info('OAuth2 jwt token introspect result active.')
                return True
        logger.info('OAuth2 jwt token introspect verify failed.')
        return False

    def _verify_jwt_token(self, token):
        algorithm = conf.OAUTH2.oauth2_algorithm
        public_key_string = self._format_public_key()
        try:
            options = {"verify_signature": True, "verify_aud": False,
                       "exp": True}
            decoded_token = jwt_decode(token, public_key_string,
                                       algorithms=[algorithm], options=options)
            logger.info(
                'Verified Token from client: %s' %
                decoded_token.get("clientHost"))
            return True
        except (ExpiredSignatureError,
                InvalidTokenError) as e:
            logger.error(f'OAuth2 jwt token validation failed: {e}')
            raise AuthFailureExp(
                'OAuth2 JWT Token Authentication failure.')
        except Exception as e:
            raise AuthRequiredExp(str(e))

    def authenticate(self, token):
        ''' Call the JWT to authenticate
        
        If the verify type is introspection, call introspection endpoint to
        verify the token.
        If the verify type is jwt, call JWT SDK to verify the token.
        '''
        oauth2_verify_type = conf.OAUTH2.oauth2_verify_type
        if oauth2_verify_type == 'introspection':
            return self._verify_jwt_token_introspect(token)
        elif oauth2_verify_type == 'jwt':
            return self._verify_jwt_token(token)
        return False

    def sanity_check(self):
        pass

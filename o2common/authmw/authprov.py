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
from o2common.helper import o2logging
import urllib.request
import urllib.parse
import json

from o2common.config.config import get_auth_provider, get_review_url
from o2common.config.config import get_reviewer_token

ssl._create_default_https_context = ssl._create_unverified_context
logger = o2logging.get_logger(__name__)

# read the conf from config file
auth_prv_conf = get_auth_provider()


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
            self.obj = keystone_auth_provider('keystone')

    def tokenissue(self):
        return self.obj.tokenissue()

    def sanity_check(self):
        return self.obj.sanity_check()

    # call k8s api
    def authenticate(self, token):
        return self.obj.authenticate(token)

    def __repr__(self) -> str:
        return "<auth_definer: name = %s>" % self.name


class k8s_auth_provider(auth_definer):

    def __init__(self, name):
        self.name = name
        try:
            self.token_review_url = get_review_url()
        except Exception:
            raise Exception('Get k8s token review url failed')


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
                self.token_review_url, data=binary_data, headers=header)
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


class keystone_auth_provider(auth_definer):
    def __init__(self, name):
        self.name = name

    def tokenissue(self, *args1, **args2):
        pass

    def authenticate(self, *args1, **args2):
        return False

    def sanity_check(self):
        pass

    def tokenrevoke(self, *args1, **args2):
        return False

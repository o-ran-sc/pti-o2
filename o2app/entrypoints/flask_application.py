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

from flask import Flask
from flask_restx import Api


from o2app import bootstrap
from o2ims.views import configure_namespace as ims_route_configure_namespace
from o2common.views.route_exception import configure_exception

from o2common.authmw import authmiddleware
from o2common.authmw import authprov
from o2common.config.config import get_review_url
from o2common.helper import o2logging

# apibase = config.get_o2ims_api_base()
auth = True
app = Flask(__name__)
logger = o2logging.get_logger(__name__)


def _get_k8s_url():
    try:
        token_review_url = get_review_url()
        return token_review_url
    except Exception:
        raise Exception('Get k8s token review url failed')


FLASK_API_VERSION = '1.0.0'

if auth:
    # perform service account identity&privilege check.
    _get_k8s_url()
    ad = authprov.auth_definer('ad')
    ad.sanity_check()
    app.wsgi_app = authmiddleware.authmiddleware(app.wsgi_app)

app.config.SWAGGER_UI_DOC_EXPANSION = 'list'
# app.config['RESTX_MASK_HEADER'] = 'fields'
app.config['RESTX_MASK_SWAGGER'] = False
app.config['ERROR_INCLUDE_MESSAGE'] = False
api = Api(
    app, version=FLASK_API_VERSION,
    catch_all_404s=True,
    title='INF O2 Services API',
    description='Swagger OpenAPI document for the INF O2 Services',
          )
bus = bootstrap.bootstrap()

configure_exception(api)
ims_route_configure_namespace(api)

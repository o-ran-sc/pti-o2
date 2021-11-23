# Copyright (C) 2021 Wind River Systems, Inc.
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
from o2ims.views import ocloud_route as ims_route
from o2dms.views import dms_route


# apibase = config.get_o2ims_api_base()
app = Flask(__name__)
app.config.SWAGGER_UI_DOC_EXPANSION = 'list'
api = Api(app, version='1.0.0',
          title='O-Cloud O2 Services',
          description='Swagger OpenAPI document for \
          O-Cloud O2 Services',
          )
bus = bootstrap.bootstrap()

ims_route.configure_namespace(api, bus)
dms_route.configure_namespace(api, bus)

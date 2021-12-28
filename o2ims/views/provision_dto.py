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

from flask_restx import fields

from o2ims.views.api_ns import api_provision_v1


class SmoEndpointDTO:

    endpoint_get = api_provision_v1.model(
        "SmoEndpointGetDto",
        {
            'configurationId': fields.String(required=True,
                                             description='Configuration ID'),
            'endpoint': fields.String,
            'status': fields.String,
            'comments': fields.String,
        }
    )

    endpoint = api_provision_v1.model(
        "SmoEndpointCreateDto",
        {
            'endpoint': fields.String(
                required=True,
                description='Configuration SMO callback address',
                example='http://mock_smo:80/registration')
        }
    )

    endpoint_post_resp = api_provision_v1.model(
        "SmoEndpointCreatedRespDto",
        {
            'configurationId': fields.String(required=True,
                                             description='Configuration ID'),
        }
    )

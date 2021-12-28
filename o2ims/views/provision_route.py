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

from flask_restx import Resource

from o2common.service.messagebus import MessageBus
from o2ims.views import provision_view
from o2ims.views.api_ns import api_provision_v1
from o2ims.views.provision_dto import SmoEndpointDTO


def configure_api_route():
    # Set global bus for resource
    global bus
    bus = MessageBus.get_instance()


# ----------  SMO endpoint ---------- #
@api_provision_v1.route("/smo-endpoint")
class SmoEndpointListRouter(Resource):

    model = SmoEndpointDTO.endpoint_get
    expect = SmoEndpointDTO.endpoint
    post_resp = SmoEndpointDTO.endpoint_post_resp

    @api_provision_v1.doc('List SMO endpoints')
    @api_provision_v1.marshal_list_with(model)
    def get(self):
        return provision_view.configurations(bus.uow)

    @api_provision_v1.doc('Create a SMO endpoint')
    @api_provision_v1.expect(expect)
    @api_provision_v1.marshal_with(post_resp, code=201)
    def post(self):
        data = api_provision_v1.payload
        result = provision_view.configuration_create(data, bus)
        return result, 201


@api_provision_v1.route("/smo-endpoint/<configurationID>")
@api_provision_v1.param('configurationID',
                        'ID of the SMO endpoint configuration')
@api_provision_v1.response(404, 'SMO Endpoint configuration not found')
class SmoEndpointGetDelRouter(Resource):

    model = SmoEndpointDTO.endpoint_get

    @api_provision_v1.doc('Get configuration by ID')
    @api_provision_v1.marshal_with(model)
    def get(self, configurationID):
        result = provision_view.configuration_one(
            configurationID, bus.uow)
        if result is not None:
            return result
        api_provision_v1.abort(404,
                               "SMO Endpoint configuration {} doesn't exist".
                               format(configurationID))

    @api_provision_v1.doc('Delete configuration by ID')
    @api_provision_v1.response(204, 'Configuration deleted')
    def delete(self, configurationID):
        result = provision_view.configuration_delete(configurationID, bus.uow)
        return result, 204

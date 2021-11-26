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

# from flask import jsonify
from flask_restx import Resource

from o2common.config import config
from o2dms.views.dms_dto import DmsLcmNfOCloudVResourceDTO
from o2dms.views import dms_lcm_view, api_dms_lcm_v1
from o2common.service.messagebus import MessageBus

apibase = config.get_o2dms_api_base()


# LCM services #
@api_dms_lcm_v1\
    .route("/<deploymentManagerID>/O2dms_DeploymentLifecycle/"
           "NfDeployment/<nfDeploymentId>/NfOCloudVirtualResource")
@api_dms_lcm_v1\
    .param('deploymentManagerID', 'ID of the Deployment Manager')
@api_dms_lcm_v1.param('nfDeploymentId',
                      'ID of the NfDeployment')
@api_dms_lcm_v1.response(404, 'DMS LCM not found')
class DmsLcmNfOCloudVResListRouter(Resource):

    model = DmsLcmNfOCloudVResourceDTO.NfOCloudVResource_get

    @api_dms_lcm_v1.doc('Get a list of NfOCloudVirtualResource')
    @api_dms_lcm_v1.marshal_list_with(model)
    def get(self, nfDeploymentId, deploymentManagerID):
        bus = MessageBus.get_instance()
        return dms_lcm_view.lcm_nfocloudvresource_list(
            nfDeploymentId, bus.uow)


@api_dms_lcm_v1\
    .route("/<deploymentManagerID>/O2dms_DeploymentLifecycle/"
           "NfDeployment/<nfDeploymentId>/"
           "NfOCloudVirtualResource/<nfOCloudVirtualResourceId>")
@api_dms_lcm_v1\
    .param('deploymentManagerID', 'ID of the deployment manager')
@api_dms_lcm_v1.param('nfDeploymentId',
                      'ID of the NfDeployment')
@api_dms_lcm_v1.param('nfOCloudVirtualResourceId',
                      'ID of the NfOCloudVirtualResource')
@api_dms_lcm_v1.response(404, 'DMS LCM not found')
class DmsLcmNfOCloudVResGetRouter(Resource):

    model = DmsLcmNfOCloudVResourceDTO.NfOCloudVResource_get

    @api_dms_lcm_v1.doc('Get a NfOCloudVirtualResource')
    @api_dms_lcm_v1.marshal_with(model)
    def get(self, nfOCloudVirtualResourceId,
            nfDeploymentId, deploymentManagerID):
        bus = MessageBus.get_instance()
        result = dms_lcm_view\
            .lcm_nfocloudvresource_one(nfOCloudVirtualResourceId, bus.uow)
        if result is not None:
            return result
        api_dms_lcm_v1.abort(
            404, "NfOCloudVirtualResource {} doesn't exist".format(
                nfOCloudVirtualResourceId))

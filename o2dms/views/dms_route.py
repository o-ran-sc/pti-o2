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
from o2dms.views.dms_dto import DmsDTO, DmsLcmNfDeploymentDescriptorDTO
from o2dms.views import dms_lcm_view, api_dms_lcm_v1

apibase = config.get_o2dms_api_base()


# ----------  DeploymentManagers ---------- #
@api_dms_lcm_v1.route("/<deploymentManagerID>")
@api_dms_lcm_v1.param('deploymentManagerID', 'ID of the deployment manager')
@api_dms_lcm_v1.response(404, 'Deployment manager not found')
class DmsGetRouter(Resource):

    model = DmsDTO.dms_get

    @api_dms_lcm_v1.doc('Get deployment manager')
    @api_dms_lcm_v1.marshal_with(model)
    def get(self, deploymentManagerID):
        result = dms_lcm_view.deployment_manager_one(
            deploymentManagerID, bus.uow)
        if result is not None:
            return result
        api_dms_lcm_v1.abort(404, "Deployment manager {} doesn't exist".format(
            deploymentManagerID))


# LCM services #
@api_dms_lcm_v1\
    .route("/<deploymentManagerID>/O2dms_DeploymentLifecycle/"
           "NfDeploymentDescriptor")
@api_dms_lcm_v1\
    .param('deploymentManagerID', 'ID of the deployment manager')
@api_dms_lcm_v1.response(404, 'DMS LCM not found')
class DmsLcmNfDeploymentDescListRouter(Resource):

    model = DmsLcmNfDeploymentDescriptorDTO.dmslcm_NfDeploymentDescriptor_get

    createdto = DmsLcmNfDeploymentDescriptorDTO.NfDeploymentDescriptor_create
    post_resp = DmsLcmNfDeploymentDescriptorDTO.\
        NfDeploymentDescriptor_create_post_resp

    @api_dms_lcm_v1.doc('Get a list of NfDeploymentDescriptor')
    @api_dms_lcm_v1.marshal_list_with(model)
    def get(self, deploymentManagerID):
        return dms_lcm_view.lcm_nfdeploymentdesc_list(
            deploymentManagerID, bus.uow)

    @api_dms_lcm_v1.doc('Create a NfDeploymentDescriptor')
    @api_dms_lcm_v1.expect(createdto)
    @api_dms_lcm_v1.marshal_with(post_resp, code=201)
    def post(self, deploymentManagerID):
        data = api_dms_lcm_v1.payload
        id = dms_lcm_view.lcm_nfdeploymentdesc_create(
            deploymentManagerID, data, bus.uow)
        return {"id": id}, 201


@api_dms_lcm_v1\
    .route("/<deploymentManagerID>/O2dms_DeploymentLifecycle/"
           "NfDeploymentDescriptor/<nfDeploymentDescriptorId>")
@api_dms_lcm_v1\
    .param('deploymentManagerID', 'ID of the deployment manager')
@api_dms_lcm_v1.param('nfDeploymentDescriptorId',
                      'ID of the NfDeploymentDescriptor')
@api_dms_lcm_v1.response(404, 'DMS LCM not found')
class DmsLcmNfDeploymentDescGetRouter(Resource):

    model = DmsLcmNfDeploymentDescriptorDTO.dmslcm_NfDeploymentDescriptor_get
    updatedto = DmsLcmNfDeploymentDescriptorDTO.\
        NfDeploymentDescriptor_update

    @api_dms_lcm_v1.doc('Get a NfDeploymentDescriptor')
    @api_dms_lcm_v1.marshal_with(model)
    def get(self, nfDeploymentDescriptorId, deploymentManagerID):
        result = dms_lcm_view\
            .lcm_nfdeploymentdesc_one(nfDeploymentDescriptorId, bus.uow)
        if result is not None:
            return result
        api_dms_lcm_v1.abort(
            404, "NfDeploymentDescriptor {} doesn't exist".format(
                nfDeploymentDescriptorId))

    @api_dms_lcm_v1.doc('Update a NfDeploymentDescriptor')
    @api_dms_lcm_v1.expect(updatedto)
    def put(self, nfDeploymentDescriptorId, deploymentManagerID):
        data = api_dms_lcm_v1.payload
        dms_lcm_view.lcm_nfdeploymentdesc_update(
            nfDeploymentDescriptorId, data, bus.uow)
        return {}, 201

    @api_dms_lcm_v1.doc('Delete NfDeploymentDescriptor by ID')
    @api_dms_lcm_v1.response(204, 'NfDeploymentDescriptor deleted')
    def delete(self, nfDeploymentDescriptorId, deploymentManagerID):
        with bus.uow:
            bus.uow.nfdeployment_descs.delete(nfDeploymentDescriptorId)
            bus.uow.commit()
        return '', 204


def configure_namespace(app, bus_new):
    app.add_namespace(api_dms_lcm_v1, path=apibase)

    # Set global uow
    global bus
    bus = bus_new

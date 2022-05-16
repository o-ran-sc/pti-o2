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
from os.path import exists
from flask import send_file
from flask_restx import Resource, reqparse

from o2dms.api.dms_dto import DmsDTO
from o2dms.api import dms_lcm_view
from o2dms.api.dms_api_ns import api_dms_lcm_v1

from o2common.service.messagebus import MessageBus
from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


def configure_api_route():
    pass


# ----------  DeploymentManagers ---------- #
@api_dms_lcm_v1.route("/<deploymentManagerID>")
@api_dms_lcm_v1.param('deploymentManagerID', 'ID of the deployment manager')
@api_dms_lcm_v1.param('profile', 'DMS profile',
                      location='args')
@api_dms_lcm_v1.response(404, 'Deployment manager not found')
class DmsGetRouter(Resource):

    model = DmsDTO.dms_get

    @api_dms_lcm_v1.doc('Get deployment manager')
    @api_dms_lcm_v1.marshal_with(model)
    def get(self, deploymentManagerID):
        logger.debug("get o2dms info:{}".format(
            deploymentManagerID
        ))
        bus = MessageBus.get_instance()

        parser = reqparse.RequestParser()
        parser.add_argument('profile', location='args')
        args = parser.parse_args()

        result = dms_lcm_view.deployment_manager_one(
            deploymentManagerID, args.profile, bus.uow)
        if result is not None:
            return result
        api_dms_lcm_v1.abort(404, "Deployment manager {} doesn't exist".format(
            deploymentManagerID))


@api_dms_lcm_v1.route("/<deploymentManagerID>/download/<filename>")
@api_dms_lcm_v1.param('deploymentManagerID',
                      'ID of the deployment manager')
@api_dms_lcm_v1.param('filename',
                      'profile filename')
@api_dms_lcm_v1.response(404, 'profile not found')
class DeploymentManagerGetFileRouter(Resource):
    def get(self, deploymentManagerID, filename):
        path = "/tmp/kubeconfig_" + filename

        if exists(path):
            return send_file(path, as_attachment=True)
        api_dms_lcm_v1.abort(
            404,
            "Deployment manager {}'s Kube config file doesn't exist".
            format(deploymentManagerID))

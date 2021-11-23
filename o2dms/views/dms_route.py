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

from o2ims import config
from o2ims.views import ocloud_view
from o2dms.views.dms_dto import DmsDTO

apibase = config.get_o2dms_api_base()


# ----------  DeploymentManagers ---------- #
api_dms = DmsDTO.api


@api_dms.route("/<deploymentManagerID>")
@api_dms.param('deploymentManagerID', 'ID of the deployment manager')
@api_dms.response(404, 'Deployment manager not found')
class DmsGetRouter(Resource):

    model = DmsDTO.dms_get

    @api_dms.doc('Get deployment manager')
    @api_dms.marshal_with(model)
    def get(self, deploymentManagerID):
        result = ocloud_view.deployment_manager_one(
            deploymentManagerID, uow)
        if result is not None:
            return result
        api_dms.abort(404, "Deployment manager {} doesn't exist".format(
            deploymentManagerID))


def configure_namespace(app, bus):
    app.add_namespace(api_dms, path=apibase)
    # Set global uow
    global uow
    uow = bus.uow

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

# from datetime import datetime
from flask import Flask, jsonify
# request
# from o2ims.domain import commands
# from o2ims.service.handlers import InvalidResourceType
from o2ims import bootstrap, config
from o2ims.views import ocloud_view


def configure_routes(app, bus):

    # ----------  OClouds ---------- #
    @app.route(apibase, methods=["GET"])
    def oclouds():
        result = ocloud_view.oclouds(bus.uow)
        return jsonify(result), 200

    # ----------  ResourceTypes ---------- #

    @app.route(apibase + "/resourceTypes", methods=["GET"])
    def resource_types():
        result = ocloud_view.resource_types(bus.uow)
        return jsonify(result), 200

    @app.route(apibase + "/resourceTypes", methods=["POST", "PUT", "PATCH",
                                                    "DELETE"])
    def resource_types_not_allow():
        return "Method Not Allowed", 405

    @app.route(apibase + "/resourceTypes/<resourceTypeID>", methods=["GET"])
    def resource_types_one(resourceTypeID):
        result = ocloud_view.resource_type_one(resourceTypeID, bus.uow)
        if result is None:
            return "", 200
        return jsonify(result), 200

    @app.route(apibase + "/resourceTypes/<resourceTypeID>",
               methods=["POST", "PUT", "PATCH", "DELETE"])
    def resource_types_one_not_allow(resourceTypeID):
        return "Method Not Allowed", 405

    # ----------  ResourcePools ---------- #

    @app.route(apibase + "/resourcePools", methods=["GET"])
    def resource_pools():
        result = ocloud_view.resource_pools(bus.uow)
        return jsonify(result), 200

    @app.route(apibase + "/resourcePools", methods=["POST", "PUT", "PATCH",
                                                    "DELETE"])
    def resource_pools_not_allow():
        return "Method Not Allowed", 405

    @app.route(apibase + "/resourcePools/<resourcePoolID>", methods=["GET"])
    def resource_pools_one(resourcePoolID):
        result = ocloud_view.resource_pool_one(resourcePoolID, bus.uow)
        if result is None:
            return "", 200
        return jsonify(result), 200

    @app.route(apibase + "/resourcePools/<resourcePoolID>",
               methods=["POST", "PUT", "PATCH", "DELETE"])
    def resource_pools_one_not_allow(resourcePoolID):
        return "Method Not Allowed", 405

    # ----------  Resources ---------- #

    @app.route(apibase + "/resourcePools/<resourcePoolID>/resources",
               methods=["GET"])
    def resources(resourcePoolID):
        result = ocloud_view.resources(resourcePoolID, bus.uow)
        return jsonify(result), 200

    @app.route(apibase + "/resourcePools/<resourcePoolID>/resources",
               methods=["POST", "PUT", "PATCH", "DELETE"])
    def resource_not_allow(resourcePoolID):
        return "Method Not Allowed", 405

    @app.route(apibase +
               "/resourcePools/<resourcePoolID>/resources/<resourceID>",
               methods=["GET"])
    def resources_one(resourcePoolID, resourceID):
        result = ocloud_view.resource_one(resourceID, bus.uow)
        if result is None:
            return "", 200
        return jsonify(result), 200

    @app.route(apibase +
               "/resourcePools/<resourcePoolID>/resources/<resourceID>",
               methods=["POST", "PUT", "PATCH", "DELETE"])
    def resource_one_not_allow(resourcePoolID, resourceID):
        return "Method Not Allowed", 405

    # ----------  DeploymentManagers ---------- #

    @app.route(apibase + "/deploymentManagers", methods=["GET"])
    def deployment_managers():
        result = ocloud_view.deployment_managers(bus.uow)
        return jsonify(result), 200

    @app.route(apibase + "/deploymentManagers",
               methods=["POST", "PUT", "PATCH", "DELETE"])
    def deployment_managers_not_allow():
        return "Method Not Allowed", 405

    @app.route(apibase + "/deploymentManagers/<deploymentManagerID>",
               methods=["GET"])
    def deployment_manager_one(deploymentManagerID):
        result = ocloud_view.deployment_manager_one(
            deploymentManagerID, bus.uow)
        if result is None:
            return "", 200
        return jsonify(result), 200

    @app.route(apibase + "/deploymentManagers/<deploymentManagerID>",
               methods=["POST", "PUT", "PATCH", "DELETE"])
    def deployment_manager_one_not_allow(deploymentManagerID):
        return "Method Not Allowed", 405


app = Flask(__name__)
bus = bootstrap.bootstrap()
apibase = config.get_o2ims_api_base()
configure_routes(app, bus)

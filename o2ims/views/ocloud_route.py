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

from flask import jsonify
from flask_restx import Resource

from o2ims import config
from o2ims.views import ocloud_view
from o2ims.views.ocloud_dto import OcloudDTO, ResourceTypeDTO,\
    ResourcePoolDTO, ResourceDTO, DeploymentManagerDTO, SubscriptionDTO

apibase = config.get_o2ims_api_base()
# api = Namespace("O2IMS", description='IMS')


# ----------  OClouds ---------- #
api_ocloud = OcloudDTO.api


@api_ocloud.route("/")
class OcloudsListRouter(Resource):
    """Ocloud get endpoint
    O2 interface ocloud endpoint
    """

    ocloud_get = OcloudDTO.ocloud_list

    @api_ocloud.marshal_list_with(ocloud_get)
    def get(self):
        return ocloud_view.oclouds(uow)


# ----------  ResourceTypes ---------- #
api_rt = ResourceTypeDTO.api


@api_rt.route("/resourceTypes")
class ResourceTypesListRouter(Resource):

    model = ResourceTypeDTO.resource_type_get

    @api_rt.marshal_list_with(model)
    def get(self):
        return ocloud_view.resource_types(uow)

    # @api.doc(response={405: 'Method Not Allowed'})
    # def post(self):
    #     api.abort(405)

    # @api.doc(response={405: 'Method Not Allowed'})
    # def put(self):
    #     api.abort(405)

    # @api.doc(response={405: 'Method Not Allowed'})
    # def patch(self):
    #     api.abort(405)

    # @api.doc(response={405: 'Method Not Allowed'})
    # def delete(self):
    #     api.abort(405)


@api_rt.route("/resourceTypes/<resourceTypeID>")
@api_rt.param('resourceTypeID', 'ID of the resource type')
@api_rt.response(404, 'Resource type not found')
class ResourceTypeGetRouter(Resource):

    model = ResourceTypeDTO.resource_type_get

    @api_rt.doc('Get resource type')
    @api_rt.marshal_with(model)
    def get(self, resourceTypeID):
        result = ocloud_view.resource_type_one(resourceTypeID, uow)
        if result is not None:
            return result
        api_rt.abort(
            404, "Resource type {} doesn't exist".format(resourceTypeID))


# ----------  ResourcePools ---------- #
api_rp = ResourcePoolDTO.api


@api_rp.route("/resourcePools")
class ResourcePoolsListRouter(Resource):

    model = ResourcePoolDTO.resource_pool_get

    @api_rp.marshal_list_with(model)
    def get(self):
        return ocloud_view.resource_pools(uow)


@api_rp.route("/resourcePools/<resourcePoolID>")
@api_rp.param('resourcePoolID', 'ID of the resource pool')
@api_rp.response(404, 'Resource pool not found')
class ResourcePoolGetRouter(Resource):

    model = ResourcePoolDTO.resource_pool_get

    @api_rp.doc('Get resource pool')
    def get(self, resourcePoolID):
        result = ocloud_view.resource_pool_one(resourcePoolID, uow)
        if result is not None:
            return result
        api_rp.abort(
            404, "Resource pool {} doesn't exist".format(resourcePoolID))


# ----------  Resources ---------- #
api_res = ResourceDTO.api


@api_res.route("/resourcePools/<resourcePoolID>/resources")
@api_res.param('resourcePoolID', 'ID of the resource pool')
class ResourcesListRouter(Resource):

    model = ResourceDTO.resource_list

    @api_res.marshal_list_with(model)
    def get(self, resourcePoolID):
        return ocloud_view.resources(resourcePoolID, uow)


@api_res.route("/resourcePools/<resourcePoolID>/resources/<resourceID>")
@api_res.param('resourcePoolID', 'ID of the resource pool')
@api_res.param('resourceID', 'ID of the resource')
@api_res.response(404, 'Resource not found')
class ResourceGetRouter(Resource):

    model = ResourceDTO.resource_get

    @api_res.doc('Get resource')
    def get(self, resourcePoolID, resourceID):
        result = ocloud_view.resource_one(resourceID, uow)
        if result is not None:
            return result
        api_res.abort(404, "Resource {} doesn't exist".format(resourceID))


# ----------  DeploymentManagers ---------- #
api_dm = DeploymentManagerDTO.api


@api_dm.route("/deploymentManagers")
class DeploymentManagersListRouter(Resource):

    model = DeploymentManagerDTO.deployment_manager_get

    @api_dm.marshal_list_with(model)
    def get(self):
        return ocloud_view.deployment_managers(uow)


@api_dm.route("/deploymentManagers/<deploymentManagerID>")
@api_dm.param('deploymentManagerID', 'ID of the deployment manager')
@api_dm.response(404, 'Deployment manager not found')
class DeploymentManagerGetRouter(Resource):

    model = DeploymentManagerDTO.deployment_manager_get

    @api_dm.doc('Get deployment manager')
    def get(self, deploymentManagerID):
        result = ocloud_view.deployment_manager_one(
            deploymentManagerID, uow)
        if result is not None:
            return result
        api_dm.abort(404, "Deployment manager {} doesn't exist".format(
            deploymentManagerID))


# ----------  Subscriptions ---------- #
api_sub = SubscriptionDTO.api


@api_sub.route("/subscriptions")
class SubscriptionsListRouter(Resource):

    model = SubscriptionDTO.subscription_get

    @api_sub.marshal_list_with(model)
    def get(self):
        return ocloud_view.subscriptions(uow)


@api_sub.route("/subscriptions/<subscriptionID>")
@api_sub.param('subscriptionID', 'ID of the subscription')
@api_sub.response(404, 'Subscription not found')
class SubscriptionGetRouter(Resource):

    model = DeploymentManagerDTO.deployment_manager_get

    @api_sub.doc('Get subscription by ID')
    def get(self, subscriptionID):
        result = ocloud_view.subscription_one(
            subscriptionID, uow)
        if result is not None:
            return result
        api_sub.abort(404, "Subscription {} doesn't exist".format(
            subscriptionID))


def configure_namespace(app, bus):

    app.add_namespace(api_ocloud, path=apibase)
    app.add_namespace(api_rt, path=apibase)
    app.add_namespace(api_rp, path=apibase)
    app.add_namespace(api_res, path=apibase)
    app.add_namespace(api_dm, path=apibase)
    app.add_namespace(api_sub, path=apibase)

    # Set global uow
    global uow
    uow = bus.uow


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

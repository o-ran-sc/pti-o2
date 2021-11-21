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

from flask_restx import Namespace, fields


class OcloudDTO:

    api = Namespace("Ocloud", description='Ocloud related operations.')

    ocloud_list = api.model(
        "List Ocloud object",
        {
            'oCloudId': fields.String(required=True),
            'globalCloudId': fields.String,
            'name': fields.String,
            'description': fields.String,
            'infrastructureManagementServiceEndpoint': fields.String,
        }
    )


class ResourceTypeDTO:

    api = Namespace(
        "ResourceType", description='Resource type related operations.')

    resource_type_get = api.model(
        "Get ResourceType object",
        {
            'resourceTypeId': fields.String(required=True,
                                            description='Resource type ID'),
            'name': fields.String,
            'vendor': fields.String,
            'version': fields.String,
            'description': fields.String,
        }
    )


class ResourcePoolDTO:

    api = Namespace(
        "ResourcePool", description='Resource pool related operations.')

    resource_pool_get = api.model(
        "Get ResourcePool object",
        {
            'resourcePoolId': fields.String(required=True,
                                            description='Resource pool ID'),
            'name': fields.String,
            'globalLocationId': fields.String,
            'location': fields.String,
            'description': fields.String,
        }
    )


class ResourceDTO:

    api = Namespace("Resource", description='Resource related operations.')

    resource_list = api.model(
        "List Resource object",
        {
            'resourceId': fields.String(required=True,
                                        description='Resource ID'),
            'resourceTypeId': fields.String,
            'resourcePoolId': fields.String,
            'parentId': fields.String,
            'description': fields.String,
        }
    )

    resource_get = api.model(
        "Get Resource object",
        {
            'resourceId': fields.String(required=True,
                                        description='Resource ID'),
            'resourceTypeId': fields.String,
            'resourcePoolId': fields.String,
            'parentId': fields.String,
            'description': fields.String,
        }
    )


class DeploymentManagerDTO:

    api = Namespace("DeploymentManager",
                    description='Deployment manager related operations.')

    deployment_manager_get = api.model(
        "Get DeploymentManager object",
        {
            'deploymentManagerId': fields.String(
                required=True,
                description='Deployment manager ID'),
            'name': fields.String,
            'description': fields.String,
            'deploymentManagementServiceEndpoint': fields.String,
            'supportedLocations': fields.String,
            'capabilities': fields.String,
            'capacity': fields.String,
        }
    )


class SubscriptionDTO:

    api = Namespace(
        "Subscription", description='Subscription related operations.')

    subscription_get = api.model(
        "Get Subscription object",
        {
            'subscriptionId': fields.String(required=True,
                                            description='Subscription ID'),
            'callback': fields.String,
            'consumerSubscriptionId': fields.String,
            'filter': fields.String,
        }
    )

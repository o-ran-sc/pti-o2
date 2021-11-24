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

from o2ims.views import api


class OcloudDTO:

    ocloud = api.model(
        "OcloudDto",
        {
            'oCloudId': fields.String(required=True),
            'globalCloudId': fields.String,
            'name': fields.String,
            'description': fields.String,
            'infrastructureManagementServiceEndpoint': fields.String,
        }
    )


class ResourceTypeDTO:

    resource_type_get = api.model(
        "ResourceTypeGetDto",
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

    resource_pool_get = api.model(
        "ResourcePoolGetDto",
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

    resource_list = api.model(
        "ResourceListDto",
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
        "ResourceGetDto",
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

    deployment_manager_get = api.model(
        "DeploymentManagerGetDto",
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

    subscription_get = api.model(
        "SubscriptionGetDto",
        {
            'subscriptionId': fields.String(required=True,
                                            description='Subscription ID'),
            'callback': fields.String,
            'consumerSubscriptionId': fields.String,
            'filter': fields.String,
        }
    )

    subscription = api.model(
        "SubscriptionCreateDto",
        {
            'callback': fields.String(
                required=True, description='Subscription callback address'),
            'consumerSubscriptionId': fields.String,
            'filter': fields.String,
        }
    )

    subscription_post_resp = api.model(
        "SubscriptionCreatedRespDto",
        {
            'subscriptionId': fields.String(required=True,
                                            description='Subscription ID'),
        }
    )

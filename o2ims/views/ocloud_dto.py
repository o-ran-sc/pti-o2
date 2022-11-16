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

from o2ims.views.api_ns import api_ims_inventory as api_ims_inventory_v1
from o2common.views.flask_restx_fields import Json2Dict

class OcloudDTO:

    ocloud = api_ims_inventory_v1.model(
        "OcloudDto",
        {
            'oCloudId': fields.String(required=True),
            'globalcloudId': fields.String(attribute='globalCloudId'),
            'name': fields.String,
            'description': fields.String,
            'serviceUri': fields.String(attribute='serviceUri'),
            # 'infrastructureManagementServiceEndpoint': fields.String(
            # attribute='serviceUri'),
            # 'infrastructureMangementServiceEndPoint': fields.String(
            # attribute='serviceUri'),
            # 'resourceTypes': fields.String,
            # 'resourcePools': fields.String,
            # 'deploymentManagers': fields.String,
            # 'smoRegistrationService': fields.String
            'extensions': fields.String
        },
        mask='{oCloudId,globalcloudId,name,description,serviceUri}'
    )


class ResourceTypeDTO:
    alarm_dictionary = api_ims_inventory_v1.model(
        "AlarmDictionaryDto",
        {
            'id': fields.String,
            'alarmDictionaryVersion': fields.String,
            'alarmDictionarySchemVersion': fields.String,
            'entityType': fields.String,
            'vendor': fields.String,
            'managementInterfaceId': fields.String,
            'pkNotificationField': fields.String,
            'alarmDefinition': fields.String,
        }
    )

    resource_type_get = api_ims_inventory_v1.model(
        "ResourceTypeGetDto",
        {
            'resourceTypeId': fields.String(required=True,
                                            description='Resource type ID'),
            'name': fields.String,
            'description': fields.String,
            'vendor': fields.String,
            'model': fields.String,
            'version': fields.String,
            'alarmDictionary': fields.Nested(alarm_dictionary, False, True),
            # 'resourceKind': fields.String,
            # 'resourceClass': fields.String,
            'extensions': fields.String
        },
        mask='{resourceTypeId,name,description,model,vendor,version}'
    )


class ResourcePoolDTO:

    resource_pool_get = api_ims_inventory_v1.model(
        "ResourcePoolGetDto",
        {
            'resourcePoolId': fields.String(required=True,
                                            description='Resource pool ID'),
            'globalLocationId': fields.String,
            'name': fields.String,
            'description': fields.String,
            'oCloudId': fields.String,
            'location': fields.String,
            # 'resources': fields.String,
            'extensions': fields.String
        },
        mask='{resourcePoolId,oCloudId,globalLocationId,name,description}'
    )


class ResourceDTO:
    resource_list = api_ims_inventory_v1.model(
        "ResourceListDto",
        {
            'resourceId': fields.String(required=True,
                                        description='Resource ID'),
            'resourceTypeId': fields.String,
            'resourcePoolId': fields.String,
            'globalAssetId': fields.String,
            # 'name': fields.String,
            'parentId': fields.String,
            'description': fields.String,
            # 'elements': fields.String,
            # 'extensions': fields.String
            'extensions': Json2Dict(attribute='extensions')
            # 'extensions': fields.Raw(attribute='extensions')
        },
        mask='{resourceId,resourcePoolId,resourceTypeId,description,parentId}'
    )

    def recursive_resource_mapping(iteration_number=2):
        resource_json_mapping = {
            'resourceId': fields.String(required=True,
                                        description='Resource ID'),
            'resourceTypeId': fields.String,
            'resourcePoolId': fields.String,
            'globalAssetId': fields.String,
            # 'name': fields.String,
            'parentId': fields.String,
            'description': fields.String,
            # 'elements': fields.String,
            # 'extensions': fields.String
            'extensions': Json2Dict(attribute='extensions')
            # 'extensions': fields.Raw(attribute='extensions')
        }
        if iteration_number:
            resource_json_mapping['elements'] = fields.List(
                fields.Nested(ResourceDTO.recursive_resource_mapping(
                    iteration_number-1)), attribute='children')
        return api_ims_inventory_v1.model(
            'ResourceGetDto' + str(iteration_number), resource_json_mapping,
            mask='{resourceId,resourcePoolId,resourceTypeId,description,' +
            'parentId}')


class DeploymentManagerDTO:

    deployment_manager_list = api_ims_inventory_v1.model(
        "DeploymentManagerListDto",
        {
            'deploymentManagerId': fields.String(
                required=True,
                description='Deployment manager ID'),
            'name': fields.String,
            'description': fields.String,
            'oCloudId': fields.String,
            'serviceUri': fields.String(attribute='serviceUri'),
            # 'deploymentManagementServiceEndpoint': fields.String(
            # attribute='serviceUri'),
            # 'supportedLocations': fields.String,
            # 'capabilities': fields.String,
            # 'capacity': fields.String,
            'profileSupportList': fields.List(
                fields.String,
                description='Profile support list, use default for the return \
                     endpoint'),
            'extensions': fields.String
        },
        mask='{deploymentManagerId,name,description,oCloudId,serviceUri,' + \
        'profileSupportList}'
    )

    profile = api_ims_inventory_v1.model("DeploymentManagerGetDtoProfile", {
        'cluster_api_endpoint': fields.String(
            attribute='cluster_api_endpoint'),
        'cluster_ca_cert': fields.String(attribute='cluster_ca_cert'),
        'admin_user': fields.String(attribute='admin_user'),
        'admin_client_cert': fields.String(attribute='admin_client_cert'),
        'admin_client_key': fields.String(attribute='admin_client_key'),
        # 'kube_config_file': fields.String(attribute='kube_config_file')
        'helmcli_host_with_port': fields.String(
            attribute='helmcli_host_with_port'),
        'helmcli_username': fields.String(attribute='helmcli_username'),
        'helmcli_password': fields.String(attribute='helmcli_password'),
        'helmcli_kubeconfig': fields.String(attribute='helmcli_kubeconfig'),
    })

    extensions = api_ims_inventory_v1.model("DeploymentManagerExtensions", {
        'profileName': fields.String,
        'profileData': fields.Nested(profile, False, True),
    })

    deployment_manager_get = api_ims_inventory_v1.model(
        "DeploymentManagerGetDto",
        {
            'deploymentManagerId': fields.String(
                required=True,
                description='Deployment manager ID'),
            'name': fields.String,
            'description': fields.String,
            'oCloudId': fields.String,
            'serviceUri': fields.String(attribute='serviceUri'),
            # 'deploymentManagementServiceEndpoint': fields.String(
            # attribute='serviceUri'),
            # 'supportedLocations': fields.String,
            # 'capabilities': fields.String,
            # 'capacity': fields.String,
            'extensions': fields.Nested(extensions, True, True)
        },
        mask='{deploymentManagerId,name,description,oCloudId,serviceUri,' +\
        'extensions/profileName,extensions/profileData}'
    )


class SubscriptionDTO:

    subscription_get = api_ims_inventory_v1.model(
        "SubscriptionGetDto",
        {
            'subscriptionId': fields.String(required=True,
                                            description='Subscription ID'),
            'callback': fields.String,
            'consumerSubscriptionId': fields.String,
            'filter': fields.String,
        },
        mask='{subscriptionId,callback}'
    )

    subscription_create = api_ims_inventory_v1.model(
        "SubscriptionCreateDto",
        {
            'callback': fields.String(
                required=True, description='Subscription callback address'),
            'consumerSubscriptionId': fields.String,
            'filter': fields.String,
        }
    )

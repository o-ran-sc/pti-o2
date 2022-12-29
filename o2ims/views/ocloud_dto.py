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
            'oCloudId': fields.String(
                required=True,
                example='f078a1d3-56df-46c2-88a2-dd659aa3f6bd',
                description='Identifier for the containing O-Cloud.'),
            'globalCloudId': fields.String(
                example='10a07219-4201-4b3e-a52d-81ab6a755d8a',
                description='Identifier of the O-Cloud instance. ' +
                'Globally unique across O-Cloud instances.'),
            'globalcloudId': fields.String(
                attribute='globalCloudId',
                example='10a07219-4201-4b3e-a52d-81ab6a755d8a',
                description='Identifier of the O-Cloud instance. ' +
                'Globally unique across O-Cloud instances.(Specification)'),
            'name': fields.String(
                example='95b818b8-b315-4d9f-af37-b82c492101f1',
                description='Human readable name of the O-Cloud.'),
            'description': fields.String(
                example='An ocloud',
                description='Human readable description of the O-Cloud.'),
            'serviceUri': fields.String(
                attribute='serviceUri',
                example='https://128.224.115.51:30205',
                description='The fully qualified URI root to all ' +
                'services provided by the O2ims interface'),
            # 'infrastructureManagementServiceEndpoint': fields.String(
            # attribute='serviceUri'),
            # 'infrastructureMangementServiceEndPoint': fields.String(
            # attribute='serviceUri'),
            # 'resourceTypes': fields.String,
            # 'resourcePools': fields.String,
            # 'deploymentManagers': fields.String,
            # 'smoRegistrationService': fields.String
            'extensions': fields.String(
                example='',
                description='These are unspecified (not standardized) ' +\
                'properties (keys) which are tailored by the vendor ' +\
                'to extend the information provided about the O-Cloud.'),
        },
        mask='{oCloudId,globalCloudId,globalcloudId,name,description,' +\
        'serviceUri}'
    )


class ResourceTypeDTO:
    alarm_definition = api_ims_inventory_v1.model(
        "AlarmDefinitionDto",
        {
            'alarmDefinitionId': fields.String,
            'alarmName': fields.String,
            'alarmLastChange': fields.String,
            'alarmChangeType': fields.String,
            'alarmDescription': fields.String,
            'proposedRepairActions': fields.String,
            'clearingType': fields.String,
            'managementInterfaceId': fields.String,
            'pkNotificationField': fields.String,
            'alarmAdditionalFields': fields.String,
        }

    )
    alarm_dictionary = api_ims_inventory_v1.model(
        "AlarmDictionaryDto",
        {
            'id': fields.String,
            'alarmDictionaryVersion': fields.String,
            'alarmDictionarySchemaVersion': fields.String,
            'entityType': fields.String,
            'vendor': fields.String,
            'managementInterfaceId': fields.String,
            'pkNotificationField': fields.String,
            # 'alarmDefinition': fields.String,
            'alarmDefinition': fields.List(fields.Nested(alarm_definition),
                                           attribute='alarmDefinition'),
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
            'resourcePoolId': fields.String(
                required=True,
                example='f078a1d3-56df-46c2-88a2-dd659aa3f6bd',
                description='Identifier for the Resource Pool in the ' +
                'O-Cloud instance.'),
            'globalLocationId': fields.String(
                example='',
                description='This identifier is copied from the O-Cloud ' +
                'Id assigned by the SMO during the O-Cloud deployment.'),
            'name': fields.String(
                example='RegionOne',
                description='Human readable name of the resource pool.'),
            'description': fields.String(
                example='A Resource Pool',
                description='Human readable description of the ' +
                'resource pool.'),
            'oCloudId': fields.String(
                example='f078a1d3-56df-46c2-88a2-dd659aa3f6bd',
                description='Identifier for the containing O-Cloud.'),
            'location': fields.String(
                example='',
                description='Information about the geographical ' +
                'location of the resource pool as detected by the O-Cloud.'),
            # 'resources': fields.String,
            'extensions': fields.String(
                example='',
                description='List of metadata key-value pairs ' +\
                'used to associate meaningful metadata to ' +\
                'the related resource pool.')
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

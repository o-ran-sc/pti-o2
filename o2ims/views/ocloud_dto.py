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


class InventoryApiV1DTO:

    api_version = api_ims_inventory_v1.model(
        'InventoryV1ApiVersionStructure',
        {
            'version': fields.String(
                required=True,
                example='1.0.0',
                description='Identifies a supported version.'
            )
        },
        mask='{version,}'
    )

    api_version_info_get = api_ims_inventory_v1.model(
        "InventoryV1APIVersion",
        {
            'uriPrefix': fields.String(
                required=True,
                example='https://128.224.115.36:30205/' +
                'o2ims-infrastructureInventory/v1',
                description='Specifies the URI prefix for the API'),
            'apiVersions': fields.List(
                fields.Nested(api_version),
                example=[{'version': '1.0.0'}],
                description='Version(s) supported for the API ' +
                'signaled by the uriPrefix attribute.'),
        },
        mask='{uriPrefix,apiVersions}'
    )


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
            'alarmDefinitionId': fields.String(
                example='eaefa070-7cb6-3403-be46-177bd9ccc2d3',
                description='Provides a unique identifier of the alarm ' +
                'being raised.'),
            'alarmName': fields.String(
                example='100.104',
                description='Provides short name for the alarm.'),
            'alarmLastChange': fields.String(
                example='0.1',
                description='Indicates the Alarm Dictionary Version in ' +
                'which this alarm last changed.'),
            'alarmChangeType': fields.String(
                example='ADDED',
                description='Indicates the type of change that occurred ' +
                'during the alarm last change; added, deleted, modified.'),
            'alarmDescription': fields.String(
                example='host=<hostname>.filesystem=<mount-dir>\n    ' +
                'File System threshold exceeded; threshold x%, actual y% .\n' +
                '        CRITICAL @ 90%\n        ' +
                'MAJOR    @ 80%\nOR\n' +
                'host=<hostname>.volumegroup=<volumegroup-name>\n    ' +
                'Monitor and if condition persists, consider addin ...',
                description='Provides a longer descriptive meaning of ' +
                'the alarm condition and a description of the ' +
                'consequences of the alarm condition.'),
            'proposedRepairActions': fields.String(
                example='Reduce usage or resize filesystem.',
                description='Provides guidance for proposed repair actions.'),
            'clearingType': fields.String(
                example='MANUAL',
                description='Identifies whether alarm is cleared ' +
                'automatically or manually.'),
            'managementInterfaceId': fields.String(
                example='O2IMS',
                description='List of management interface over which ' +
                'alarms are transmitted for this Entity Type.'),
            'pkNotificationField': fields.String(
                example='',
                description='Identifies which field or list of fields in ' +
                'the alarm notification contains the primary key (PK) into ' +
                'the Alarm Dictionary for this interface; i.e. which ' +
                'field contains the Alarm Definition ID.'),
            'alarmAdditionalFields': fields.String(
                example='',
                description='List of metadata key-value pairs used to ' +
                'associate meaningful metadata to the related resource type.'),
        }

    )
    alarm_dictionary = api_ims_inventory_v1.model(
        "AlarmDictionaryDto",
        {
            'id': fields.String(
                example='7e1e59c3-c99e-3d1c-9934-21548a3a699a',
                description='Identifier for the Alarm Dictionary.'),
            'alarmDictionaryVersion': fields.String(
                example='0.1',
                description='Version of the Alarm Dictionary.'),
            'alarmDictionarySchemaVersion': fields.String(
                example='0.1',
                description='Version of the Alarm Dictionary Schema to ' +
                'which this alarm dictionary conforms.'),
            'entityType': fields.String(
                example='pserver',
                description='O-RAN entity type emitting the alarm: This ' +
                'shall be unique per vendor ResourceType.model and ' +
                'ResourceType.version'),
            'vendor': fields.String(
                example='',
                description='Vendor of the Entity Type to whom this ' +
                'Alarm Dictionary applies. This should be the same value ' +
                'as in the ResourceType.vendor attribute.'),
            'managementInterfaceId': fields.String(
                example='O2IMS',
                description='List of management interface over which ' +
                'alarms are transmitted for this Entity Type.'),
            'pkNotificationField': fields.String(
                example='',
                description='Identifies which field or list of fields in ' +
                'the alarm notification contains the primary key (PK) into ' +
                'the Alarm Dictionary for this interface; i.e. which field ' +
                'contains the Alarm Definition ID.'),
            # 'alarmDefinition': fields.String,
            'alarmDefinition': fields.List(
                fields.Nested(alarm_definition),
                attribute='alarmDefinition',
                example='',
                description='Contains the list of alarms that can be ' +
                'detected against this ResourceType.'),
        }
    )

    resource_type_get = api_ims_inventory_v1.model(
        "ResourceTypeGetDto",
        {
            'resourceTypeId': fields.String(
                required=True,
                example='60cba7be-e2cd-3b8c-a7ff-16e0f10573f9',
                description='Identifier for the Resource Type.'),
            'name': fields.String(
                example='pserver',
                description='Human readable name of the resource type.'),
            'description': fields.String(
                example='The Physical Server resource type',
                description='Human readable description of the resource ' +
                'type.'),
            'vendor': fields.String(
                example='',
                description='Provider of the Resource.'),
            'model': fields.String(
                example='',
                description='Information about the model of the resource ' +
                'as defined by its provider.'),
            'version': fields.String(
                example='',
                description='Version or generation of the resource as ' +
                'defined by its provider.'),
            'alarmDictionary': fields.Nested(
                alarm_dictionary, False, True),
            # description='Dictionary of alarms for this resource type.'),
            # 'resourceKind': fields.String,
            # 'resourceClass': fields.String,
            'extensions': fields.String(
                example='',
                description='List of metadata key-value pairs used to ' +
                'associate meaningful metadata to the related resource type.'),
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
            'resourceId': fields.String(
                required=True,
                example='5b3a2da8-17da-466c-b5f7-972590c7baf2',
                description='Identifier for the Resource.'),
            'resourceTypeId': fields.String(
                example='60cba7be-e2cd-3b8c-a7ff-16e0f10573f9',
                description='Identifier for the Resource Type of ' +
                'this resource.'),
            'resourcePoolId': fields.String(
                example='f078a1d3-56df-46c2-88a2-dd659aa3f6bd',
                description='Identifier of the Resource Pool containing ' +
                'this resource.'),
            'globalAssetId': fields.String(
                example='',
                description='Identifier or serial number of the resource.'),
            # 'name': fields.String,
            'parentId': fields.String(
                example='None',
                description='Identifier for the parent resource.'),
            'description': fields.String(
                example="id:1;hostname:controller-0;mgmt_mac:00:00:00:00:" +
                "00:00;mgmt_ip:192.168.204.2;personality:controller;" +
                "subfunctions:controller,worker;administrative:unlocked;" +
                "operational:enabled;availability:available;" +
                "clock_synchronization:ntp;capabilities:" +
                "{'is_max_cpu_configurable': 'configurable', " +
                "'stor_function': 'monitor', 'Personality': " +
                "'Controller-Active'};boot_device:/dev/disk/by-path" +
                "/pci-0000:02:00.0-scsi-0:1:0:0;rootfs_device:/dev/disk/" +
                "by-path/pci-0000:02:00.0-scsi-0:1:0:0;software_load:" +
                "22.12;install_state:None;max_cpu_mhz_allowed:None",
                description='Human readable description of the resource.'),
            # 'elements': fields.String,
            # 'extensions': fields.String
            'extensions': Json2Dict(attribute='extensions')
            # 'extensions': fields.Raw(attribute='extensions')
        },
        mask='{resourceId,resourcePoolId,resourceTypeId,description,parentId}'
    )

    def recursive_resource_mapping(iteration_number=2):
        resource_json_mapping = {
            'resourceId': fields.String(
                required=True,
                example='eee8b101-6b7f-4f0a-b54b-89adc0f3f906',
                description='Identifier for the Resource.'),
            'resourceTypeId': fields.String(
                example='a45983bb-199a-30ec-b7a1-eab2455f333c',
                description='Identifier for the Resource Type of ' +
                'this resource.'),
            'resourcePoolId': fields.String(
                example='f078a1d3-56df-46c2-88a2-dd659aa3f6bd',
                description='Identifier of the Resource Pool containing ' +
                'this resource.'),
            'globalAssetId': fields.String(
                example='',
                description='Identifier or serial number of the resource.'),
            # 'name': fields.String,
            'parentId': fields.String(
                example='5b3a2da8-17da-466c-b5f7-972590c7baf2',
                description='Identifier for the parent resource.'),
            'description': fields.String(
                example="cpu:0;core:0;thread:0;cpu_family:6;cpu_model:" +
                "Intel(R) Xeon(R) CPU E5-2670 v2 @ 2.50GHz;" +
                "allocated_function:Platform;numa_node:0",
                description='Human readable description of the resource.'),
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

    capabilities = api_ims_inventory_v1.model(
        "DeploymentManagerCapabilities", {
            'OS': fields.String(
                example='low_latency',
                description='Show the OS capablities of ' +
                'the Deployment Manager'),
        })

    deployment_manager_list = api_ims_inventory_v1.model(
        "DeploymentManagerListDto",
        {
            'deploymentManagerId': fields.String(
                required=True,
                example='c765516a-a84e-30c9-b954-9c3031bf71c8',
                description='Identifier for the Deployment Manager.'),
            'name': fields.String(
                example='95b818b8-b315-4d9f-af37-b82c492101f1.kubernetes',
                description='Human readable name of the deployment manager.'),
            'description': fields.String(
                example='A DMS',
                description='Human readable description of the deployment ' +
                'manager.'),
            'oCloudId': fields.String(
                example='f078a1d3-56df-46c2-88a2-dd659aa3f6bd',
                description='Identifier for the containing O-Cloud.'),
            'serviceUri': fields.String(
                attribute='serviceUri',
                example='https://128.224.115.51:6443',
                description='The fully qualified URI to a Deployment ' +
                'Management server for O2dms.'),
            # 'deploymentManagementServiceEndpoint': fields.String(
            # attribute='serviceUri'),
            # 'supportedLocations': fields.String,
            'capabilities': fields.Nested(capabilities, True, True),
            # 'capacity': fields.String,
            'profileSupportList': fields.List(
                fields.String,
                example=['native_k8sapi'],
                description='Profile support list, use default for the ' +
                'return endpoint'),
            'extensions': fields.String(
                example='',
                description='List of metadata key-value pairs used to ' +
                'associate meaningful metadata to the related Deployment ' +
                'Manager'),
        },
        mask='{deploymentManagerId,name,description,oCloudId,serviceUri,' + \
        'profileSupportList}'
    )

    profile = api_ims_inventory_v1.model("DeploymentManagerGetDtoProfile", {
        'cluster_api_endpoint': fields.String(
            attribute='cluster_api_endpoint',
            example='https://128.224.115.51:6443',
            description='Kubernetes Cluster API Endpoint'),
        'cluster_ca_cert': fields.String(
            attribute='cluster_ca_cert',
            example='LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUZEakNDQX.....',
            description='Kubernetes Cluster CA cert'),
        'admin_user': fields.String(
            attribute='admin_user',
            example='kubernetes-admin',
            description='Kubernetes Admin username'),
        'admin_client_cert': fields.String(
            attribute='admin_client_cert',
            example='LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUVJRENDQW.....',
            description='Kubernetes Admin client cert'),
        'admin_client_key': fields.String(
            attribute='admin_client_key',
            example='LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpNSUlFcE.....',
            description='Kubernetes Admin client key'),
        # 'kube_config_file': fields.String(attribute='kube_config_file')
        'helmcli_host_with_port': fields.String(
            attribute='helmcli_host_with_port',
            example='128.224.115.34:30022',
            description='Helm CLI Host address with SSH port'),
        'helmcli_username': fields.String(
            attribute='helmcli_username',
            example='helm',
            description='Helm CLI SSH login username'),
        'helmcli_password': fields.String(
            attribute='helmcli_password',
            example='password',
            description='Helm CLI SSH login password'),
        'helmcli_kubeconfig': fields.String(
            attribute='helmcli_kubeconfig',
            example='/share/kubeconfig_c765516a.config',
            description='Helm CLI KUBECONFIG path'),
    })

    extensions = api_ims_inventory_v1.model("DeploymentManagerExtensions", {
        'profileName': fields.String(
            example='',
            description=''),
        'profileData': fields.Nested(profile, False, True),
    })

    deployment_manager_get = api_ims_inventory_v1.model(
        "DeploymentManagerGetDto",
        {
            'deploymentManagerId': fields.String(
                required=True,
                example='c765516a-a84e-30c9-b954-9c3031bf71c8',
                description='Identifier for the Deployment Manager.'),
            'name': fields.String(
                example='95b818b8-b315-4d9f-af37-b82c492101f1.kubernetes',
                description='Human readable name of the deployment manager.'),
            'description': fields.String(
                example='A DMS',
                description='Human readable description of the deployment ' +
                'manager.'),
            'oCloudId': fields.String(
                example='f078a1d3-56df-46c2-88a2-dd659aa3f6bd',
                description='Identifier for the containing O-Cloud.'),
            'serviceUri': fields.String(
                attribute='serviceUri',
                example='https://128.224.115.51:6443',
                description='The fully qualified URI to a Deployment ' +
                'Management server for O2dms.'),
            # 'deploymentManagementServiceEndpoint': fields.String(
            # attribute='serviceUri'),
            # 'supportedLocations': fields.String,
            'capabilities': fields.Nested(capabilities, True, True),
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
            'subscriptionId': fields.String(
                required=True,
                example='0bea3e71-d2f7-4bf3-9c06-41d8d35806f9',
                description='Identifier for the Subscription.'),
            'callback': fields.String(
                example='https://128.224.115.15:1081/smo/v1/' +
                'o2ims_inventory_observer',
                description='The fully qualified URI to a consumer ' +
                'procedure which can process a Post of the ' +
                'InventoryEventNotification.'),
            'consumerSubscriptionId': fields.String(
                example='3F20D850-AF4F-A84F-FB5A-0AD585410361',
                description='Identifier for the consumer of events sent due ' +
                'to the Subscription.'),
            'filter': fields.String(
                example='',
                description='Criteria for events which do not need to be ' +
                'reported or will be filtered by the subscription ' +
                'notification service. Therefore, if a filter is not ' +
                'provided then all events are reported.'),
        },
        mask='{subscriptionId,callback}'
    )

    subscription_create = api_ims_inventory_v1.model(
        "SubscriptionCreateDto",
        {
            'callback': fields.String(
                required=True,
                example='https://128.224.115.15:1081/smo/v1/' +
                'o2ims_inventory_observer',
                description='Identifier for the Subscription.'),
            'consumerSubscriptionId': fields.String(
                example='3F20D850-AF4F-A84F-FB5A-0AD585410361',
                description='Identifier for the consumer of events sent due ' +
                'to the Subscription.'),
            'filter': fields.String(
                example='',
                description='Criteria for events which do not need to be ' +
                'reported or will be filtered by the subscription ' +
                'notification service. Therefore, if a filter is not ' +
                'provided then all events are reported.'),
        }
    )

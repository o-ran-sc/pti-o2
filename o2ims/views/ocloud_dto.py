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

from o2ims.views.api_ns import api_ims_inventory_v1


class OcloudDTO:

    ocloud = api_ims_inventory_v1.model(
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

    resource_type_get = api_ims_inventory_v1.model(
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

    resource_pool_get = api_ims_inventory_v1.model(
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

    resource_list = api_ims_inventory_v1.model(
        "ResourceListDto",
        {
            'resourceId': fields.String(required=True,
                                        description='Resource ID'),
            'resourceTypeId': fields.String,
            'resourcePoolId': fields.String,
            'name': fields.String,
            'parentId': fields.String,
            'description': fields.String,
        }
    )

    def recursive_resource_mapping(iteration_number=2):
        resource_json_mapping = {
            'resourceId': fields.String(required=True,
                                        description='Resource ID'),
            'resourceTypeId': fields.String,
            'resourcePoolId': fields.String,
            'name': fields.String,
            'parentId': fields.String,
            'description': fields.String,
            'elements': fields.String,
        }
        if iteration_number:
            resource_json_mapping['children'] = fields.List(
                fields.Nested(ResourceDTO.recursive_resource_mapping(
                    iteration_number-1)))
        return api_ims_inventory_v1.model(
            'ResourceGetDto' + str(iteration_number), resource_json_mapping)

    # def _recursive_resource_mapping(self, iteration_number=2):
    #     resource_json_mapping = {
    #         'resourceId': fields.String(required=True,
    #                                     description='Resource ID'),
    #         'resourceTypeId': fields.String,
    #         'resourcePoolId': fields.String,
    #         'name': fields.String,
    #         'parentId': fields.String,
    #         'description': fields.String,
    #     }
    #     if iteration_number:
    #         resource_json_mapping['children'] = fields.List(
    #             fields.Nested(self._recursive_resource_mapping(
    #                 iteration_number-1)))
    #         # print(type(resource_json_mapping['children']))
    #         if resource_json_mapping['children'] is None:
    #             del resource_json_mapping['children']
    #     return resource_json_mapping

    # def get_resource_get(self):
    #     return api_ims_inventory_v1.model(
    #         'ResourceGetDto',
    #         {
    #             'resourceId': fields.String(required=True,
    #                                         description='Resource ID'),
    #             'resourceTypeId': fields.String,
    #             'resourcePoolId': fields.String,
    #             'name': fields.String,
    #             'parentId': fields.String,
    #             'description': fields.String,
    #             'children': fields.List(fields.Nested(
    #                 self._recursive_resource_mapping()))
    #         }
    #     )


class DeploymentManagerDTO:

    deployment_manager_list = api_ims_inventory_v1.model(
        "DeploymentManagerListDto",
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
            'profileSupportList': fields.List(
                fields.String,
                description='Profile support list, use default for the return \
                     endpoint'),
        }
    )

    profile = api_ims_inventory_v1.model("DeploymentManagerGetDtoProfile", {
        'cluster_api_endpoint': fields.String(
            attributes='cluster_api_endpoint'),
        'cluster_ca_cert': fields.String(attributes='cluster_ca_cert'),
        'admin_user': fields.String(attributes='admin_user'),
        'admin_client_cert': fields.String(attributes='admin_client_cert'),
        'admin_client_key': fields.String(attributes='admin_client_key'),
        # 'kube_config_file': fields.String(attributes='kube_config_file')
        'helmcli_host_with_port': fields.String(
            attributes='helmcli_host_with_port'),
        'helmcli_username': fields.String(attributes='helmcli_username'),
        'helmcli_password': fields.String(attributes='helmcli_password'),
        'helmcli_kubeconfig': fields.String(attributes='helmcli_kubeconfig'),
    })

    deployment_manager_get = api_ims_inventory_v1.model(
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
            'profileName': fields.String,
            'profileData': fields.Nested(profile, False, True),
        }
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
        }
    )

    subscription = api_ims_inventory_v1.model(
        "SubscriptionCreateDto",
        {
            'callback': fields.String(
                required=True, description='Subscription callback address'),
            'consumerSubscriptionId': fields.String,
            'filter': fields.String,
        }
    )

    subscription_post_resp = api_ims_inventory_v1.model(
        "SubscriptionCreatedRespDto",
        {
            'subscriptionId': fields.String(required=True,
                                            description='Subscription ID'),
        }
    )

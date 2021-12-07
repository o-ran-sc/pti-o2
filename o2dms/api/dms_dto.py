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
from o2dms.api.dms_api_ns import api_dms_lcm_v1
from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


class DmsDTO:
    dms_get = api_dms_lcm_v1.model(
        "DmsGetDto",
        {
            'deploymentManagerId': fields.String(
                required=True,
                description='Deployment manager ID'),
            'name': fields.String,
            'description': fields.String,
            'supportedLocations': fields.String,
            'capabilities': fields.String,
            'capacity': fields.String,
        }
    )


class DmsLcmNfDeploymentDescriptorDTO:
    NfDeploymentDescriptor_get = api_dms_lcm_v1.model(
        "NfDeploymentDescriptorGetDto",
        {
            'id': fields.String(
                required=True,
                description='NfDeploymentDescriptor ID'),
            'name': fields.String,
            'description': fields.String,
            'inputParams': fields.String,
            'outputParams': fields.String,
            'artifactUrl': fields.String
        }
    )

    NfDeploymentDescriptor_create = api_dms_lcm_v1.model(
        "NfDeploymentDescriptorCreateDto",
        {
            'name': fields.String,
            'description': fields.String,
            'artifactUrl': fields.String,
            'inputParams': fields.String,
            'outputParams': fields.String
        }
    )

    NfDeploymentDescriptor_create_post_resp = api_dms_lcm_v1.model(
        "NfDeploymentDescriptorCreateRespDto",
        {
            'id': fields.String(
                required=True, description='NfDeploymentDescriptor ID'),
        }
    )

    NfDeploymentDescriptor_update = api_dms_lcm_v1.model(
        "NfDeploymentDescriptorUpdateDto",
        {
            'name': fields.String,
            'description': fields.String,
            'artifactUrl': fields.String,
            'inputParams': fields.String,
            'outputParams': fields.String
        }
    )


class DmsLcmNfDeploymentDTO:
    NfDeployment_get = api_dms_lcm_v1.model(
        "NfDeploymentGetDto",
        {
            'id': fields.String(
                required=True,
                description='NfDeployment ID'),
            'name': fields.String,
            'description': fields.String,
            'descriptorId': fields.String,
            'parentDeploymentId': fields.String,
            'status': fields.Integer
        }
    )

    NfDeployment_create = api_dms_lcm_v1.model(
        "NfDeploymentCreateDto",
        {
            'name': fields.String,
            'description': fields.String,
            'descriptorId': fields.String,
            'parentDeploymentId': fields.String
        }
    )

    NfDeployment_create_post_resp = api_dms_lcm_v1.model(
        "NfDeploymentCreateRespDto",
        {
            'id': fields.String(
                required=True, description='NfDeployment ID'),
        }
    )

    NfDeployment_update = api_dms_lcm_v1.model(
        "NfDeploymentUpdateDto",
        {
            'name': fields.String,
            'description': fields.String,
            'parentDeploymentId': fields.String
        }
    )


class DmsLcmNfOCloudVResourceDTO:
    NfOCloudVResource_get = api_dms_lcm_v1.model(
        "NfOCloudVResourceGetDto",
        {
            'id': fields.String(
                required=True,
                description='NfOCloudVResource ID'),
            'name': fields.String,
            'description': fields.String,
            'descriptorId': fields.String,
            'vresourceType': fields.String,
            'status': fields.Integer,
            'metadata': fields.String
        }
    )

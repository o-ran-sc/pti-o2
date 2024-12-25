# Copyright (C) 2021-2022 Wind River Systems, Inc.
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

from flask import request
from flask_restx import Resource, fields

from o2common.views.route import O2Namespace


api_ims_inventory = O2Namespace(
    "O2IMS-InfrastructureInventory",
    description='O2 IMS Inventory related operations.')

api_provision_v1 = O2Namespace(
    "PROVISION",
    description='Provision related operations.')

api_ims_monitoring = O2Namespace(
    "O2IMS-InfrastructureMonitoring",
    description='O2 IMS Monitoring related operations.')

api_ims_performance = O2Namespace(
    'O2IMS-InfrastructurePerformance',
    description='O2 IMS Infrastructure Performance API',
    validate=True
)


@api_ims_inventory.route('/api_versions')
class InventoryVersion(Resource):
    api_version = api_ims_inventory.model(
        'InventoryApiVersionStructure',
        {
            'version': fields.String(
                required=True,
                example='1.0.0',
                description='Identifies a supported version.'
            )
        },
        mask='{version,}'
    )
    model = api_ims_inventory.model(
        "InventoryAPIVersion",
        {
            'uriPrefix': fields.String(
                required=True,
                example='https://128.224.115.36:30205/' +
                'o2ims-infrastructureInventory',
                description='Specifies the URI prefix for the API'),
            'apiVersions': fields.List(
                fields.Nested(api_version),
                example=[{'version': '1.0.0'}],
                description='Version(s) supported for the API ' +
                'signaled by the uriPrefix attribute.'),
        },
        mask='{uriPrefix,apiVersions}'
    )

    @api_ims_inventory.doc('Get Inventory Version')
    @api_ims_inventory.marshal_with(model)
    def get(self):
        return {
            'uriPrefix': request.base_url.rsplit('/', 1)[0],
            'apiVersions': [{
                'version': '1.0.0',
                # 'isDeprecated': 'False',
                # 'retirementDate': ''
            }]
        }


@api_ims_monitoring.route('/api_versions')
class MonitoringVersion(Resource):
    api_version = api_ims_inventory.model(
        'MonitoringApiVersionStructure',
        {
            'version': fields.String(
                required=True,
                example='1.0.0',
                description='Identifies a supported version.'
            )
        },
        mask='{version,}'
    )
    model = api_ims_inventory.model(
        "MonitoringAPIVersion",
        {
            'uriPrefix': fields.String(
                required=True,
                example='https://128.224.115.36:30205/' +
                'o2ims-infrastructureMonitoring',
                description='Specifies the URI prefix for the API'),
            'apiVersions': fields.List(
                fields.Nested(api_version),
                example=[{'version': '1.0.0'}],
                description='Version(s) supported for the API ' +
                'signaled by the uriPrefix attribute.'),
        },
        mask='{uriPrefix,apiVersions}'
    )

    @api_ims_monitoring.doc('Get Monitoring Version')
    @api_ims_monitoring.marshal_with(model)
    def get(self):
        return {
            'uriPrefix': request.base_url.rsplit('/', 1)[0],
            'apiVersions': [{
                'version': '1.1.0',
                # 'isDeprecated': 'False',
                # 'retirementDate': ''
            }]
        }


@api_ims_performance.route('/api_version')
class PerformanceVersion(Resource):
    api_version = api_ims_inventory.model(
        'PerformanceApiVersionStructure',
        {
            'version': fields.String(
                required=True,
                example='1.0.0',
                description='Identifies a supported version.'
            )
        },
        mask='{version,}'
    )
    model = api_ims_inventory.model(
        "PerformanceAPIVersion",
        {
            'uriPrefix': fields.String(
                required=True,
                example='https://128.224.115.36:30205/' +
                'o2ims-infrastructurePerformance',
                description='Specifies the URI prefix for the API'),
            'apiVersions': fields.List(
                fields.Nested(api_version),
                example=[{'version': '1.0.0'}],
                description='Version(s) supported for the API ' +
                'signaled by the uriPrefix attribute.'),
        },
        mask='{uriPrefix,apiVersions}'
    )

    @api_ims_performance.doc('Get Performance Version')
    @api_ims_monitoring.marshal_with(model)
    def get(self):
        """Get Performance Version"""
        return {
            'uriPrefix': request.base_url.rsplit('/', 1)[0],
            'apiVersions': [{
                'version': '1.0.0',
                # 'isDeprecated': 'False',
                # 'retirementDate': ''
            }]
        }

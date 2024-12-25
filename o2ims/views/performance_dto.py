# Copyright (C) 2024 Wind River Systems, Inc.
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
from o2common.views.flask_restx_fields import Json2Dict
from o2ims.views.api_ns import api_ims_performance as api_performance_v1


class PerformanceApiV1DTO:
    api_version = api_performance_v1.model(
        'PerformanceV1ApiVersionStructure',
        {
            'version': fields.String(
                required=True,
                example='1.0.0',
                description='Identifies a supported version.'
            )
        },
        mask='{version,}'
    )

    api_version_info_get = api_performance_v1.model(
        "PerformanceV1APIVersion",
        {
            'uriPrefix': fields.String(
                required=True,
                example='https://128.224.115.36:30205/' +
                'o2ims-infrastructurePerformance/v1',
                description='Specifies the URI prefix for the API'),
            'apiVersions': fields.List(
                fields.Nested(api_version),
                example=[{'version': '1.0.0'}],
                description='Version(s) supported for the API ' +
                'signaled by the uriPrefix attribute.'),
        },
        mask='{uriPrefix,apiVersions}'
    )


class PerformanceDTO:
    measurement_job_get = api_performance_v1.model(
        "MeasurementJobGetDto",
        {
            'performanceMeasurementJobId': fields.String(
                required=True,
                example='97cc2b01-0e71-4a93-a911-2e87f04d996f',
                description='Identifier of this instance of Performance ' +
                'Meaurement Job within the IMS'),
            'consumerPerformanceJobId': fields.String(
                example='3F20D850-AF4F-A84F-FB5A-0AD585410361',
                description='Identifier provided by the consumer for its ' +
                'purpose of managing performance jobs'),
            'state': fields.String(
                example='ACTIVE',
                description='The current state of the Performance ' +
                'Measurement Job'),
            'collectionInterval': fields.Integer(
                example=300,
                description='The interval at which performance measures ' +
                'will be collected and stored'),
            'resourceScopeCriteria': Json2Dict(
                example={'resourceType': 'compute_node'},
                description='Key value pairs of resource attributes which ' +
                'are used to select resources'),
            'measurementSelectionCriteria': Json2Dict(
                example=[{"measurementGroup": "MemoryUsage"},
                         {"measurementName": "cpuAverageUtilization"}],
                description='Key value pairs that identify the distinct ' +
                'set of measurements'),
            'status': fields.String(
                example='RUNNING',
                description='This reflects the condition within the state'),
            'preinstalledJob': fields.Boolean(
                example=False,
                description='Boolean which is True if created by O-Cloud ' +
                'and False for external consumer'),
            'qualifiedResourceTypes': fields.List(
                fields.String,
                example=['7c491f8f-7207-4c00-9b67-3d2ee8b008f0',
                         '31040dec-8106-44db-83bc-62e1d618ea17'],
                description='The distinct set of ResourceTypes among ' +
                'those measuredResources'),
            'measuredResources': fields.List(
                fields.Nested(api_performance_v1.model('MeasuredResource', {
                    'resourceId': fields.String(),
                    'resourceTypeId': fields.String()
                })),
                description='Historical list of resources measured by this job'
            ),
            'collectedMeasurements': fields.List(
                fields.Nested(api_performance_v1.model(
                    'CollectedMeasurement', {
                        'measurementId': fields.String()
                    })),
                description='Historical list of measurements collected ' +
                'by this job'
            ),
            'extensions': Json2Dict(attribute='extensions')
        }
    )

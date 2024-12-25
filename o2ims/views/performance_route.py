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

from flask import request
from flask_restx import Resource, reqparse

from o2common.service.messagebus import MessageBus
from o2common.views.pagination_route import link_header, PAGE_PARAM
from o2common.views.route_exception import NotFoundException
from o2ims.views.api_ns import api_ims_performance as api_performance_v1
from o2ims.views.performance_dto import PerformanceDTO, PerformanceApiV1DTO
from o2ims.views import performance_view

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


def configure_api_route():
    # Set global bus for resource
    global bus
    bus = MessageBus.get_instance()


# ----------  API versions ---------- #
@api_performance_v1.route("/v1/api_versions")
class VersionRouter(Resource):
    model = PerformanceApiV1DTO.api_version_info_get

    @api_performance_v1.doc('Get Performance API version')
    @api_performance_v1.marshal_list_with(model)
    def get(self):
        """Get Performance API Version"""
        return {
            'uriPrefix': request.base_url.rsplit('/', 1)[0],
            'apiVersions': [{
                'version': '1.0.0',
                # 'isDeprecated': 'False',
                # 'retirementDate': ''
            }]
        }


@api_performance_v1.route("/v1/measurementJobs")
@api_performance_v1.param(PAGE_PARAM,
                          'Page number of the results to fetch.' +
                          ' Default: 1',
                          _in='query', default=1)
@api_performance_v1.param(
    'filter',
    'Filter of the query.',
    _in='query')
class MeasurementJobListRouter(Resource):
    model = PerformanceDTO.measurement_job_get

    @api_performance_v1.doc('Get Measurement Job List')
    @api_performance_v1.marshal_list_with(model)
    def get(self):
        """Get Measurement Job List"""
        parser = reqparse.RequestParser()
        parser.add_argument(PAGE_PARAM, location='args')
        parser.add_argument('filter', location='args')
        args = parser.parse_args()
        kwargs = {}
        if args.nextpage_opaque_marker is not None:
            kwargs['page'] = args.nextpage_opaque_marker
        kwargs['filter'] = args.filter if args.filter is not None else ''

        ret = performance_view.measurement_jobs(bus.uow, **kwargs)
        return link_header(request.full_path, ret)


@api_performance_v1.route("/v1/measurementJobs/<measurementJobId>")
@api_performance_v1.param('measurementJobId', 'ID of the measurement job')
@api_performance_v1.response(404, 'Measurement Job not found')
class MeasurementJobGetRouter(Resource):
    model = PerformanceDTO.measurement_job_get

    @api_performance_v1.doc('Get Measurement Job Information')
    @api_performance_v1.marshal_with(model)
    def get(self, measurementJobId):
        """Get Measurement Job Information"""
        result = performance_view.measurement_job_one(measurementJobId,
                                                      bus.uow)
        if result is not None:
            return result
        raise NotFoundException(
            "Measurement Job {} doesn't exist".format(measurementJobId))

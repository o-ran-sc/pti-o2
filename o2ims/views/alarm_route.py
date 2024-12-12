# Copyright (C) 2021-2024 Wind River Systems, Inc.
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

from o2common.config import config
from o2common.service.messagebus import MessageBus
from o2common.views.pagination_route import link_header, PAGE_PARAM
from o2common.views.route_exception import NotFoundException, \
    BadRequestException
from o2ims.domain.alarm_obj import PerceivedSeverityEnum
from o2ims.views import alarm_view
from o2ims.views.api_ns import api_ims_monitoring as api_monitoring_v1
from o2ims.views.alarm_dto import AlarmDTO, SubscriptionDTO, \
    MonitoringApiV1DTO, AlarmServiceConfigurationDTO

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


def configure_api_route():
    # Set global bus for resource
    global bus
    bus = MessageBus.get_instance()


# ----------  API versions ---------- #
@api_monitoring_v1.route("/v1/api_versions")
class VersionRouter(Resource):
    model = MonitoringApiV1DTO.api_version_info_get

    @api_monitoring_v1.doc('Get Monitoring API version')
    @api_monitoring_v1.marshal_list_with(model)
    def get(self):
        return {
            'uriPrefix': request.base_url.rsplit('/', 1)[0],
            'apiVersions': [{
                'version': '1.1.0',
                # 'isDeprecated': 'False',
                # 'retirementDate': ''
            }]
        }


# ----------  Alarm Event Record ---------- #
@api_monitoring_v1.route("/v1/alarms")
@api_monitoring_v1.param(PAGE_PARAM,
                         'Page number of the results to fetch.' +
                         ' Default: 1',
                         _in='query', default=1)
@api_monitoring_v1.param(
    'all_fields',
    'Set any value for show all fields. This value will cover "fields" ' +
    'and "all_fields".',
    _in='query')
@api_monitoring_v1.param(
    'fields',
    'Set fields to show, split by comma, "/" for parent and children.' +
    ' Like "name,parent/children". This value will cover' +
    ' "exculde_fields".',
    _in='query')
@api_monitoring_v1.param(
    'exclude_fields',
    'Set fields to exclude showing, split by comma, "/" for parent and ' +
    'children. Like "name,parent/children". This value will cover ' +
    '"exclude_default".',
    _in='query')
@api_monitoring_v1.param(
    'exclude_default',
    'Exclude showing all default fields, Set "true" to enable.',
    _in='query')
@api_monitoring_v1.param(
    'filter',
    'Filter of the query.',
    _in='query')
class AlarmListRouter(Resource):

    model = AlarmDTO.alarm_event_record_get

    @api_monitoring_v1.doc('Get Alarm Event Record List')
    @api_monitoring_v1.marshal_list_with(model)
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument(PAGE_PARAM, location='args')
        parser.add_argument('filter', location='args')
        args = parser.parse_args()
        kwargs = {}
        if args.nextpage_opaque_marker is not None:
            kwargs['page'] = args.nextpage_opaque_marker
        kwargs['filter'] = args.filter if args.filter is not None else ''

        ret = alarm_view.alarm_event_records(bus.uow, **kwargs)
        return link_header(request.full_path, ret)


@api_monitoring_v1.route("/v1/alarms/<alarmEventRecordId>")
@api_monitoring_v1.param('alarmEventRecordId', 'ID of the alarm event record')
@api_monitoring_v1.response(404, 'Alarm Event Record not found')
@api_monitoring_v1.param(
    'all_fields',
    'Set any value for show all fields. This value will cover "fields" ' +
    'and "all_fields".',
    _in='query')
@api_monitoring_v1.param(
    'fields',
    'Set fields to show, split by comma, "/" for parent and children.' +
    ' Like "name,parent/children". This value will cover' +
    ' "exculde_fields".',
    _in='query')
@api_monitoring_v1.param(
    'exclude_fields',
    'Set fields to exclude showing, split by comma, "/" for parent and ' +
    'children. Like "name,parent/children". This value will cover ' +
    '"exclude_default".',
    _in='query')
@api_monitoring_v1.param(
    'exclude_default',
    'Exclude showing all default fields, Set "true" to enable.',
    _in='query')
class AlarmGetRouter(Resource):

    model = AlarmDTO.alarm_event_record_get
    patch = AlarmDTO.alarm_event_record_patch

    @api_monitoring_v1.doc('Get Alarm Event Record Information')
    @api_monitoring_v1.marshal_with(model)
    def get(self, alarmEventRecordId):
        result = alarm_view.alarm_event_record_one(alarmEventRecordId, bus.uow)
        if result is not None:
            return result
        raise NotFoundException(
            "Alarm Event Record {} doesn't exist".format(alarmEventRecordId))

    @api_monitoring_v1.doc('Patch Alarm Event Record Information')
    @api_monitoring_v1.expect(patch)
    @api_monitoring_v1.marshal_with(patch)
    def patch(self, alarmEventRecordId):
        data = api_monitoring_v1.payload
        ack_action = data.get('alarmAcknowledged', None)
        clear_action = data.get('perceivedSeverity', None)

        ack_is_none = ack_action is None
        clear_is_none = clear_action is None
        if (ack_is_none and clear_is_none) or (not ack_is_none and
                                               not clear_is_none):
            raise BadRequestException('Either "alarmAcknowledged" or '
                                      '"perceivedSeverity" shall be included '
                                      'in a request, but not both.')
        if ack_action:
            result = alarm_view.alarm_event_record_ack(alarmEventRecordId,
                                                       bus.uow)
            if result is not None:
                return result
        elif clear_action:
            if clear_action != PerceivedSeverityEnum.CLEARED.value:
                raise BadRequestException(
                    'Only the value "5" for "CLEARED" is permitted of '
                    '"perceivedSeverity".')

            result = alarm_view.alarm_event_record_clear(alarmEventRecordId,
                                                         bus.uow)
            if result is not None:
                return result
        raise NotFoundException(
            "Alarm Event Record {} doesn't exist".format(alarmEventRecordId))


# ----------  Alarm Subscriptions ---------- #
@api_monitoring_v1.route("/v1/alarmSubscriptions")
class SubscriptionsListRouter(Resource):

    model = SubscriptionDTO.subscription_get
    expect = SubscriptionDTO.subscription_create

    @api_monitoring_v1.doc('Get Alarm Subscription List')
    @api_monitoring_v1.marshal_list_with(model)
    @api_monitoring_v1.param(
        PAGE_PARAM,
        'Page number of the results to fetch. Default: 1',
        _in='query', default=1)
    @api_monitoring_v1.param(
        'all_fields',
        'Set any value for show all fields. This value will cover "fields" ' +
        'and "all_fields".',
        _in='query')
    @api_monitoring_v1.param(
        'fields',
        'Set fields to show, split by comma, "/" for parent and children.' +
        ' Like "name,parent/children". This value will cover' +
        ' "exculde_fields".',
        _in='query')
    @api_monitoring_v1.param(
        'exclude_fields',
        'Set fields to exclude showing, split by comma, "/" for parent and ' +
        'children. Like "name,parent/children". This value will cover ' +
        '"exclude_default".',
        _in='query')
    @api_monitoring_v1.param(
        'exclude_default',
        'Exclude showing all default fields, Set "true" to enable.',
        _in='query')
    @api_monitoring_v1.param(
        'filter',
        'Filter of the query.',
        _in='query')
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument(PAGE_PARAM, location='args')
        parser.add_argument('filter', location='args')
        args = parser.parse_args()
        kwargs = {}
        if args.nextpage_opaque_marker is not None:
            kwargs['page'] = args.nextpage_opaque_marker
        kwargs['filter'] = args.filter if args.filter is not None else ''

        ret = alarm_view.subscriptions(bus.uow, **kwargs)
        return link_header(request.full_path, ret)

    @api_monitoring_v1.doc('Create a Alarm Subscription')
    @api_monitoring_v1.expect(expect)
    @api_monitoring_v1.marshal_with(
        model, code=201,
        mask='{alarmSubscriptionId,callback,consumerSubscriptionId,filter}')
    def post(self):
        data = api_monitoring_v1.payload
        callback = data.get('callback', None)
        if not callback:
            raise BadRequestException('The callback parameter is required')

        result = alarm_view.subscription_create(data, bus.uow)
        return result, 201


@api_monitoring_v1.route("/v1/alarmSubscriptions/<alarmSubscriptionID>")
@api_monitoring_v1.param('alarmSubscriptionID', 'ID of the Alarm Subscription')
@api_monitoring_v1.response(404, 'Alarm Subscription not found')
class SubscriptionGetDelRouter(Resource):

    model = SubscriptionDTO.subscription_get

    @api_monitoring_v1.doc('Get Alarm Subscription Information')
    @api_monitoring_v1.marshal_with(model)
    @api_monitoring_v1.param(
        'all_fields',
        'Set any value for show all fields. This value will cover "fields" ' +
        'and "all_fields".',
        _in='query')
    @api_monitoring_v1.param(
        'fields',
        'Set fields to show, split by comma, "/" for parent and children.' +
        ' Like "name,parent/children". This value will cover' +
        ' "exculde_fields".',
        _in='query')
    @api_monitoring_v1.param(
        'exclude_fields',
        'Set fields to exclude showing, split by comma, "/" for parent and ' +
        'children. Like "name,parent/children". This value will cover ' +
        '"exclude_default".',
        _in='query')
    @api_monitoring_v1.param(
        'exclude_default',
        'Exclude showing all default fields, Set "true" to enable.',
        _in='query')
    def get(self, alarmSubscriptionID):
        result = alarm_view.subscription_one(
            alarmSubscriptionID, bus.uow)
        if result is not None:
            return result
        raise NotFoundException(
            "Subscription {} doesn't exist".format(alarmSubscriptionID))

    @api_monitoring_v1.doc('Delete an Alarm Subscription')
    @api_monitoring_v1.response(200, 'Subscription deleted')
    def delete(self, alarmSubscriptionID):
        result = alarm_view.subscription_delete(alarmSubscriptionID, bus.uow)
        return result, 200


# ----------  Alarm Event Record ---------- #
@api_monitoring_v1.route("/v1/alarmServiceConfiguration")
@api_monitoring_v1.param(
    'all_fields',
    'Set any value for show all fields. This value will cover "fields" ' +
    'and "all_fields".',
    _in='query')
@api_monitoring_v1.param(
    'fields',
    'Set fields to show, split by comma, "/" for parent and children.' +
    ' Like "name,parent/children". This value will cover' +
    ' "exculde_fields".',
    _in='query')
@api_monitoring_v1.param(
    'exclude_fields',
    'Set fields to exclude showing, split by comma, "/" for parent and ' +
    'children. Like "name,parent/children". This value will cover ' +
    '"exclude_default".',
    _in='query')
@api_monitoring_v1.param(
    'exclude_default',
    'Exclude showing all default fields, Set "true" to enable.',
    _in='query')
class AlarmServiceConfigurationRouter(Resource):

    model = AlarmServiceConfigurationDTO.alarm_service_configuration_get
    expect = AlarmServiceConfigurationDTO.alarm_service_configuration_expect

    @api_monitoring_v1.doc('Get Alarm Service Configuration')
    @api_monitoring_v1.marshal_with(model)
    def get(self):
        result = alarm_view.alarm_service_configuration(bus.uow)
        if result is not None:
            return result

    @api_monitoring_v1.doc('Patch Alarm Service Configuration')
    @api_monitoring_v1.expect(expect)
    @api_monitoring_v1.marshal_with(model)
    def patch(self):
        data = api_monitoring_v1.payload
        retention_period = data.get('retentionPeriod', None)

        min_retention_period = config.get_min_retention_period()
        print(min_retention_period)

        if retention_period is None:
            raise BadRequestException(
                'The "retentionPeriod" parameter is required')
        elif retention_period < min_retention_period:
            raise BadRequestException(
                f'The "retentionPeriod" parameter shall more than '
                f'{min_retention_period} days')

        result = alarm_view.alarm_service_configuration_update(data, bus.uow)
        if result is not None:
            return result

        raise BadRequestException(
            'Failed to update alarm service configuration')

    @api_monitoring_v1.doc('Update Alarm Service Configuration')
    @api_monitoring_v1.expect(expect)
    @api_monitoring_v1.marshal_with(model)
    def put(self):
        data = api_monitoring_v1.payload
        retention_period = data.get('retentionPeriod', None)

        min_retention_period = config.get_min_retention_period()

        if retention_period is None:
            raise BadRequestException(
                'The "retentionPeriod" parameter is required')
        elif retention_period < min_retention_period:
            raise BadRequestException(
                f'The "retentionPeriod" parameter shall more than '
                f'{min_retention_period} days')

        result = alarm_view.alarm_service_configuration_update(data, bus.uow)
        if result is not None:
            return result

        raise BadRequestException(
            'Failed to update alarm service configuration')

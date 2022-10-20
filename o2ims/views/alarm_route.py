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

from flask import request
from flask_restx import Resource, reqparse

from o2common.service.messagebus import MessageBus
from o2common.views.pagination_route import link_header, PAGE_PARAM
from o2ims.views import alarm_view
from o2ims.views.api_ns import api_monitoring_v1
from o2ims.views.alarm_dto import AlarmDTO, SubscriptionDTO

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


def configure_api_route():
    # Set global bus for resource
    global bus
    bus = MessageBus.get_instance()


# ----------  Alarm Event Record ---------- #
@api_monitoring_v1.route("/alarms")
@api_monitoring_v1.param(PAGE_PARAM,
                         'Page number of the results to fetch.' +
                         ' Default: 1',
                         _in='query', default=1)
class AlarmListRouter(Resource):

    model = AlarmDTO.alarm_event_record_get

    @api_monitoring_v1.marshal_list_with(model)
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument(PAGE_PARAM, location='args')
        args = parser.parse_args()
        kwargs = {}
        if args.nextpage_opaque_marker is not None:
            kwargs['page'] = args.nextpage_opaque_marker

        ret = alarm_view.alarm_event_records(bus.uow, **kwargs)
        return link_header(request.full_path, ret)


@api_monitoring_v1.route("/alarms/<alarmEventRecordId>")
@api_monitoring_v1.param('alarmEventRecordId', 'ID of the alarm event record')
@api_monitoring_v1.response(404, 'Alarm Event Record not found')
class AlarmGetRouter(Resource):

    model = AlarmDTO.alarm_event_record_get

    @api_monitoring_v1.doc('Get resource type')
    @api_monitoring_v1.marshal_with(model)
    def get(self, alarmEventRecordId):
        result = alarm_view.alarm_event_record_one(alarmEventRecordId, bus.uow)
        if result is not None:
            return result
        api_monitoring_v1.abort(
            404, "Resource type {} doesn't exist".format(alarmEventRecordId))


# ----------  Alarm Subscriptions ---------- #
@api_monitoring_v1.route("/alarmSubscriptions")
class SubscriptionsListRouter(Resource):

    model = SubscriptionDTO.subscription_get
    expect = SubscriptionDTO.subscription
    post_resp = SubscriptionDTO.subscription_post_resp

    @api_monitoring_v1.doc('List alarm subscriptions')
    @api_monitoring_v1.marshal_list_with(model)
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument(PAGE_PARAM, location='args')
        args = parser.parse_args()
        kwargs = {}
        if args.nextpage_opaque_marker is not None:
            kwargs['page'] = args.nextpage_opaque_marker

        ret = alarm_view.subscriptions(bus.uow, **kwargs)
        return link_header(request.full_path, ret)

    @api_monitoring_v1.doc('Create a alarm subscription')
    @api_monitoring_v1.expect(expect)
    @api_monitoring_v1.marshal_with(post_resp, code=201)
    def post(self):
        data = api_monitoring_v1.payload
        result = alarm_view.subscription_create(data, bus.uow)
        return result, 201


@api_monitoring_v1.route("/alarmSubscriptions/<alarmSubscriptionID>")
@api_monitoring_v1.param('alarmSubscriptionID', 'ID of the Alarm Subscription')
@api_monitoring_v1.response(404, 'Alarm Subscription not found')
class SubscriptionGetDelRouter(Resource):

    model = SubscriptionDTO.subscription_get

    @api_monitoring_v1.doc('Get Alarm Subscription by ID')
    @api_monitoring_v1.marshal_with(model)
    def get(self, alarmSubscriptionID):
        result = alarm_view.subscription_one(
            alarmSubscriptionID, bus.uow)
        if result is not None:
            return result
        api_monitoring_v1.abort(404, "Subscription {} doesn't exist".format(
            alarmSubscriptionID))

    @api_monitoring_v1.doc('Delete subscription by ID')
    @api_monitoring_v1.response(204, 'Subscription deleted')
    def delete(self, alarmSubscriptionID):
        result = alarm_view.subscription_delete(alarmSubscriptionID, bus.uow)
        return result, 204

# Copyright (C) 2022-2024 Wind River Systems, Inc.
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

from typing import List, Tuple

from o2ims.domain import alarm_obj
from o2ims.domain.alarm_repo import AlarmDefinitionRepository, \
    AlarmEventRecordRepository, AlarmSubscriptionRepository, \
    AlarmProbableCauseRepository, AlarmDictionaryRepository, \
    AlarmServiceConfigurationRepository
from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


class AlarmEventRecordSqlAlchemyRepository(AlarmEventRecordRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, alarm_event_record: alarm_obj.AlarmEventRecord):
        self.session.add(alarm_event_record)

    def _get(self, alarm_event_record_id) -> alarm_obj.AlarmEventRecord:
        return self.session.query(alarm_obj.AlarmEventRecord).filter_by(
            alarmEventRecordId=alarm_event_record_id).first()

    def _list(self, *args, **kwargs) -> Tuple[
            int, List[alarm_obj.AlarmEventRecord]]:
        size = kwargs.pop('limit') if 'limit' in kwargs else None
        offset = kwargs.pop('start') if 'start' in kwargs else 0

        result = self.session.query(alarm_obj.AlarmEventRecord).filter(
            *args).order_by('alarmEventRecordId')
        count = result.count()
        if size is not None and size != -1:
            return (count, result.limit(size).offset(offset))
        return (count, result)

    def _update(self, alarm_event_record: alarm_obj.AlarmEventRecord):
        self.session.merge(alarm_event_record)

    def _delete(self, alarm_event_record):
        self.session.delete(alarm_event_record)


class AlarmDefinitionSqlAlchemyRepository(AlarmDefinitionRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, definition: alarm_obj.AlarmDefinition):
        self.session.add(definition)

    def _get(self, definition_id) -> alarm_obj.AlarmDefinition:
        return self.session.query(alarm_obj.AlarmDefinition).filter_by(
            alarmDefinitionId=definition_id).first()

    def _list(self) -> List[alarm_obj.AlarmDefinition]:
        return self.session.query(alarm_obj.AlarmDefinition)

    def _update(self, definition: alarm_obj.AlarmDefinition):
        self.session.add(definition)

    def _delete(self, alarm_definition_id):
        self.session.query(alarm_obj.AlarmDefinition).filter_by(
            alarmDefinitionId=alarm_definition_id).delete()


class AlarmDictionarySqlAlchemyRepository(AlarmDictionaryRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, alarm_dict: alarm_obj.AlarmDictionary):
        self.session.add(alarm_dict)

    def _get(self, dictionary_id) -> alarm_obj.AlarmDictionary:
        return self.session.query(alarm_obj.AlarmDictionary).filter_by(
            id=dictionary_id).first()

    def _list(self) -> List[alarm_obj.AlarmDictionary]:
        return self.session.query(alarm_obj.AlarmDictionary)

    def _delete(self, dictionary_id):
        self.session.query(alarm_obj.AlarmDictionary).filter_by(
            id=dictionary_id).delete()


class AlarmSubscriptionSqlAlchemyRepository(AlarmSubscriptionRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, subscription: alarm_obj.AlarmSubscription):
        self.session.add(subscription)

    def _get(self, subscription_id) -> alarm_obj.AlarmSubscription:
        return self.session.query(alarm_obj.AlarmSubscription).filter_by(
            alarmSubscriptionId=subscription_id).first()

    def _list(self, *args, **kwargs) -> Tuple[
            int, List[alarm_obj.AlarmSubscription]]:
        size = kwargs.pop('limit') if 'limit' in kwargs else None
        offset = kwargs.pop('start') if 'start' in kwargs else 0

        result = self.session.query(alarm_obj.AlarmSubscription).filter(
            *args).order_by('alarmSubscriptionId')
        count = result.count()
        if size is not None and size != -1:
            return (count, result.limit(size).offset(offset))
        return (count, result)

    def _update(self, subscription: alarm_obj.AlarmSubscription):
        self.session.add(subscription)

    def _delete(self, alarm_subscription_id):
        self.session.query(alarm_obj.AlarmSubscription).filter_by(
            alarmSubscriptionId=alarm_subscription_id).delete()


class AlarmProbableCauseSqlAlchemyRepository(AlarmProbableCauseRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, probable_cause: alarm_obj.ProbableCause):
        self.session.add(probable_cause)

    def _get(self, probable_cause_id) -> alarm_obj.ProbableCause:
        return self.session.query(alarm_obj.ProbableCause).filter_by(
            probableCauseId=probable_cause_id).first()

    def _list(self) -> List[alarm_obj.ProbableCause]:
        return self.session.query(alarm_obj.ProbableCause)

    def _update(self, probable_cause: alarm_obj.ProbableCause):
        self.session.add(probable_cause)

    def _delete(self, probable_cause_id):
        self.session.query(alarm_obj.ProbableCause).filter_by(
            probableCauseId=probable_cause_id).delete()


class AlarmServiceConfigurationSqlAlchemyRepository(
        AlarmServiceConfigurationRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add_default(self) -> alarm_obj.AlarmServiceConfiguration:
        query = self.session.query(
            alarm_obj.AlarmServiceConfiguration).first()
        if not query:
            default_config = alarm_obj.AlarmServiceConfiguration(
                retention_period=14
            )
            self.session.add(default_config)
            self.session.commit()
            logger.info(
                "Inserted default AlarmServiceConfiguration record.")
            return default_config
        return query

    def _get(self) -> alarm_obj.AlarmServiceConfiguration:
        return self.session.query(alarm_obj.AlarmServiceConfiguration).first()

    def _update(self, service_config: alarm_obj.AlarmServiceConfiguration):
        print(service_config.retentionPeriod)
        self.session.merge(service_config)

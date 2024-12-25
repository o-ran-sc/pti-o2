# Copyright (C) 2021-2025 Wind River Systems, Inc.
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

# pylint: disable=attribute-defined-outside-init
from __future__ import annotations
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from o2common.config import config
from o2common.service.unit_of_work import AbstractUnitOfWork

from o2ims.adapter import ocloud_repository, alarm_repository, \
    performance_repository
from o2dms.adapter import dms_repository

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


engine = create_engine(
    config.get_postgres_uri(),
    isolation_level="REPEATABLE READ",
    pool_size=200, max_overflow=0,
    pool_recycle=3600
)

DEFAULT_SESSION_FACTORY = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):

    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()  # type: Session
        self.oclouds = ocloud_repository\
            .OcloudSqlAlchemyRepository(self.session)
        self.resource_types = ocloud_repository\
            .ResouceTypeSqlAlchemyRepository(self.session)
        self.resource_pools = ocloud_repository\
            .ResourcePoolSqlAlchemyRepository(self.session)
        self.resources = ocloud_repository\
            .ResourceSqlAlchemyRepository(self.session)
        self.subscriptions = ocloud_repository\
            .SubscriptionSqlAlchemyRepository(self.session)
        self.deployment_managers = ocloud_repository\
            .DeploymentManagerSqlAlchemyRepository(self.session)
        self.nfdeployment_descs = dms_repository\
            .NfDeploymentDescSqlAlchemyRepository(self.session)
        self.nfdeployments = dms_repository\
            .NfDeploymentSqlAlchemyRepository(self.session)
        self.ocloudvresources = dms_repository\
            .NfOCloudVResourceSqlAlchemyRepository(self.session)
        self.alarm_event_records = alarm_repository\
            .AlarmEventRecordSqlAlchemyRepository(self.session)
        self.alarm_definitions = alarm_repository\
            .AlarmDefinitionSqlAlchemyRepository(self.session)
        self.alarm_dictionaries = alarm_repository\
            .AlarmDictionarySqlAlchemyRepository(self.session)
        self.alarm_subscriptions = alarm_repository\
            .AlarmSubscriptionSqlAlchemyRepository(self.session)
        self.alarm_probable_causes = alarm_repository\
            .AlarmProbableCauseSqlAlchemyRepository(self.session)
        self.alarm_service_config = alarm_repository\
            .AlarmServiceConfigurationSqlAlchemyRepository(self.session)
        self.measurement_jobs = performance_repository\
            .MeasurementJobSqlAlchemyRepository(self.session)

        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()

    def _commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    def _collect_new_events(self):
        for entry in self.oclouds.seen:
            # while hasattr(entry, 'events') and len(entry.events) > 0:
            while entry.events is not None and len(entry.events) > 0:
                yield entry.events.pop(0)
        for entry in self.resource_pools.seen:
            while entry.events is not None and len(entry.events) > 0:
                yield entry.events.pop(0)
        for entry in self.resources.seen:
            while entry.events is not None and len(entry.events) > 0:
                yield entry.events.pop(0)
        for entry in self.resource_types.seen:
            while hasattr(entry, 'events') and len(entry.events) > 0:
                yield entry.events.pop(0)
        for entry in self.deployment_managers.seen:
            while hasattr(entry, 'events') and len(entry.events) > 0:
                yield entry.events.pop(0)
        for entry in self.subscriptions.seen:
            while hasattr(entry, 'events') and len(entry.events) > 0:
                yield entry.events.pop(0)
        for entry in self.nfdeployment_descs.seen:
            while hasattr(entry, 'events') and len(entry.events) > 0:
                yield entry.events.pop(0)
        for entry in self.nfdeployments.seen:
            while hasattr(entry, 'events') and len(entry.events) > 0:
                yield entry.events.pop(0)
        for entry in self.ocloudvresources.seen:
            while hasattr(entry, 'events') and len(entry.events) > 0:
                yield entry.events.pop(0)
        for entry in self.alarm_event_records.seen:
            while hasattr(entry, 'events') and len(entry.events) > 0:
                yield entry.events.pop(0)
        for entry in self.alarm_subscriptions.seen:
            while hasattr(entry, 'events') and len(entry.events) > 0:
                yield entry.events.pop(0)

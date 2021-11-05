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

# pylint: disable=attribute-defined-outside-init
from __future__ import annotations
import abc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from o2ims import config
from o2ims.adapter import ocloud_repository


class AbstractUnitOfWork(abc.ABC):
    oclouds: ocloud_repository.OcloudRepository

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        self._commit()

    def collect_new_events(self):
        for ocloud in self.oclouds.seen:
            while ocloud.events:
                yield ocloud.events.pop(0)

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError


engine = create_engine(
    config.get_postgres_uri(),
    isolation_level="REPEATABLE READ",
)

DEFAULT_SESSION_FACTORY = sessionmaker(
    bind=engine
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
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()

    def _commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

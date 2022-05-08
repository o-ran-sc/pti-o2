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

from retry import retry
from sqlalchemy import (
    Table,
    MetaData,
    Column,
    Integer,
    String,
    Text,
    # Date,
    DateTime,
    # ForeignKey,
    # engine,
    # event,
    exc
)

from sqlalchemy.orm import mapper
from o2dms.domain import dms as dmsModel

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)

metadata = MetaData()

nfDeploymentDesc = Table(
    "nfDeploymentDesc",
    metadata,
    Column("updatetime", DateTime),
    Column("createtime", DateTime),
    Column("hash", String(255)),
    Column("version_number", Integer),

    Column("id", String(255), primary_key=True),
    Column("deploymentManagerId", String(255)),
    Column("name", String(255)),
    Column("description", String(255)),
    Column("inputParams", Text()),
    Column("outputParams", String(255)),
    Column("artifactRepoUrl", String(255)),
    Column("artifactName", String(255)),
    # Column("extensions", String(1024))
)

nfDeployment = Table(
    "nfDeployment",
    metadata,
    Column("updatetime", DateTime),
    Column("createtime", DateTime),
    Column("hash", String(255)),
    Column("version_number", Integer),

    Column("id", String(255), primary_key=True),
    Column("deploymentManagerId", String(255)),
    Column("name", String(255)),
    Column("description", String(255)),
    Column("descriptorId", String(255)),
    Column("parentDeploymentId", String(255)),
    Column("status", Integer)
)

nfOCloudVResource = Table(
    "nfOcloudVRes",
    metadata,
    Column("updatetime", DateTime),
    Column("createtime", DateTime),
    Column("hash", String(255)),
    Column("version_number", Integer),

    Column("id", String(255), primary_key=True),
    Column("deploymentManagerId", String(255)),
    Column("name", String(255)),
    Column("description", String(255)),
    Column("descriptorId", String(255)),
    Column("vresourceType", String(255)),
    Column("status", Integer),
    Column("metadata", String(2048)),
    Column("nfDeploymentId", String(255))
)


@retry((exc.IntegrityError), tries=3, delay=2)
def wait_for_metadata_ready(engine):
    # wait for mapper ready
    metadata.create_all(engine, checkfirst=True)
    logger.info("metadata is ready")


def start_o2dms_mappers(engine=None):
    logger.info("Starting O2 DMS mappers")

    mapper(dmsModel.NfDeploymentDesc, nfDeploymentDesc)
    mapper(dmsModel.NfDeployment, nfDeployment)
    mapper(dmsModel.NfOCloudVResource, nfOCloudVResource)

    if engine is not None:
        wait_for_metadata_ready(engine)

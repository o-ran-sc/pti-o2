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

from typing import List
from o2dms.domain import dms, dms_repo


class NfDeploymentDescSqlAlchemyRepository(dms_repo
                                           .NfDeploymentDescRepository):

    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, nfdeployment_desc: dms.NfDeploymentDesc):
        self.session.add(nfdeployment_desc)

    def _get(self, nfdeployment_desc_id) -> dms.NfDeploymentDesc:
        return self.session.query(dms.NfDeploymentDesc).filter_by(
            id=nfdeployment_desc_id).first()

    def _list(self) -> List[dms.NfDeploymentDesc]:
        return self.session.query()

    def _update(self, nfdeployment_desc_id, **kwargs):
        self.session.query(dms.NfDeploymentDesc).filter_by(
            id=nfdeployment_desc_id).update(**kwargs)

    def _delete(self, nfdeployment_desc_id):
        self.session.query(dms.NfDeploymentDesc).filter_by(
            id=nfdeployment_desc_id
        ).delete()

    def _count(self, **kwargs):
        return self.session.query(
            dms.NfDeploymentDesc).filter_by(**kwargs).count()


class NfDeploymentSqlAlchemyRepository(
        dms_repo.NfDeploymentRepository):

    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, nfdeployment: dms.NfDeployment):
        self.session.add(nfdeployment)

    def _get(self, nfdeployment_id) -> dms.NfDeployment:
        return self.session.query(dms.NfDeployment).filter_by(
            id=nfdeployment_id).first()

    def _list(self) -> List[dms.NfDeployment]:
        return self.session.query()

    def _update(self, nfdeployment_id, **kwargs):
        self.session.query(dms.NfDeployment).filter_by(
            id=nfdeployment_id).update(**kwargs)

    def _delete(self, nfdeployment_id):
        self.session.query(dms.NfDeployment).filter_by(
            id=nfdeployment_id
        ).delete()

    def _count(self, **kwargs):
        return self.session.query(
            dms.NfDeployment).filter_by(**kwargs).count()


class NfOCloudVResourceSqlAlchemyRepository(
        dms_repo.NfOCloudVResourceRepository):

    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, nfocloudvres: dms.NfOCloudVResource):
        self.session.add(nfocloudvres)

    def _get(self, nfocloudvres_id) -> dms.NfOCloudVResource:
        return self.session.query(dms.NfOCloudVResource).filter_by(
            id=nfocloudvres_id).first()

    def _list(self) -> List[dms.NfOCloudVResource]:
        return self.session.query()

    def _update(self, nfocloudvres, **kwargs):
        self.session.query(dms.NfOCloudVResource).filter_by(
            id=nfocloudvres).update(**kwargs)

    def _delete(self, nfocloudvres):
        self.session.query(dms.NfOCloudVResource).filter_by(
            id=nfocloudvres
        ).delete()

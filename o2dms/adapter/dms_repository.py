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
            nfDeploymentDescId=nfdeployment_desc_id).first()

    def _list(self) -> List[dms.NfDeploymentDesc]:
        return self.session.query()

    def _update(self, nfdeployment_desc: dms.NfDeploymentDesc):
        self.session.add(nfdeployment_desc)

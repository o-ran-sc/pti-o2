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

import os
from locust import HttpUser, task, constant

# bearer_token="Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IkJJb3A2V2JSb29nNjR2YnpzOE12VXpzRHJVNjVSLUp1dWhZX2kzV0hjc2cifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6InNtby10b2tlbi1xNjcyZyIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50Lm5hbWUiOiJzbW8iLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC51aWQiOiIwNmQzNDY1Ny0yZGFlLTQyNDItODMzMC05OTI4MjFmYzk0N2UiLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6ZGVmYXVsdDpzbW8ifQ.PbDAaLwi4OdQ4CZUFa1TC2vP0IWJqTP2ECmv287uHCho4vpZU63pkS2SgdtbDHLbPK29wZKJ1q9mqv4fci2WdJ7w87sfbHT1dcC8VzfAq7aQ4Rx6xRtsnTmerWqgsXYF_JqpfpHQFVO2stkV5zvg902J5Yco09xez0V6tIGNNORyBXc0SrQ7nuyMoH4gxAunfE_nFB5bQd9dfJnD7gHdDmh2v0HzKEnOV2KUJVhVLGnXZRJmYq1hoDc9YrJRoXmGucescnMDqUh0t8bwVG5a0BQZlLcc1y7i3WXUWPbXsmJ-7RN2_jYERUlS70SmOfaKNSC-t2BvGuh1lmF6yQaoKA"
bearer_token="Bearer "+os.environ.get("SMO_TOKEN_DATA", "")

class QuickstartUser(HttpUser):
    wait_time = constant(0)

    @task
    def ocloud(self):
        self.client.get("/o2ims-infrastructureInventory/v1/")

    @task
    def resource(self):
        resp = self.client.get(
            "/o2ims-infrastructureInventory/v1/resourcePools")
        json_resp_dict = resp.json()
        self.client.get(
            "/o2ims-infrastructureInventory/v1/resourcePools/%s/resources" %
            json_resp_dict[0]['resourcePoolId'])

    @task
    def dms(self):
        self.client.get("/o2ims-infrastructureInventory/v1/deploymentManagers")

    def on_start(self):
        self.client.headers = {
            'Authorization':bearer_token
        }
        self.client.verify = False

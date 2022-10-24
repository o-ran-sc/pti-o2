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

#!/bin/bash

# pull latest code to debug
# cd /root/
# git clone "https://gerrit.o-ran-sc.org/r/pti/o2"
# cd o2
# git pull https://gerrit.o-ran-sc.org/r/pti/o2 refs/changes/85/7085/5
# pip install retry

# pip install -e /root/o2
pip install -e /src

cat <<EOF>>/etc/hosts
127.0.0.1  api
127.0.0.1  postgres
127.0.0.1  redis
EOF


flask run --host=0.0.0.0 --port=80 --cert /configs/ca.cert  --key /configs/server.key

sleep infinity

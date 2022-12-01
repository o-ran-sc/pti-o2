# Copyright (C) 2022 Wind River Systems, Inc.
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

apk add --no-cache openssh

if [ -z "${HELM_USER_PASSWD}" ];
then
    HELM_USER_PASSWD=St8rlingX*
fi

adduser helm << EOF
${HELM_USER_PASSWD}
${HELM_USER_PASSWD}
EOF

ssh-keygen -A
exec /usr/sbin/sshd -D -e "$@"
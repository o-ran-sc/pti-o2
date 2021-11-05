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

# from datetime import datetime
from flask import Flask
# request
# from o2ims.domain import commands
# from o2ims.service.handlers import InvalidResourceType
from o2ims import bootstrap
from o2ims.views.ocloud_route import configure_routes


app = Flask(__name__)
bus = bootstrap.bootstrap()
configure_routes(app, bus)

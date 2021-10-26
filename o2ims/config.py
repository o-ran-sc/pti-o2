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


def get_postgres_uri():
    host = os.environ.get("DB_HOST", "localhost")
    port = 54321 if host == "localhost" else 5432
    password = os.environ.get("DB_PASSWORD", "o2ims123")
    user, db_name = "o2ims", "o2ims"
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"


def get_api_url():
    host = os.environ.get("API_HOST", "localhost")
    port = 5005 if host == "localhost" else 80
    return f"http://{host}:{port}"


def get_o2ims_api_base():
    return '/o2ims_infrastructureInventory/v1'


def get_redis_host_and_port():
    host = os.environ.get("REDIS_HOST", "localhost")
    port = 63791 if host == "localhost" else 6379
    return dict(host=host, port=port)


def get_smo_o2endpoint():
    smo_o2endpoint = os.environ.get(
        "SMO_O2_ENDPOINT", "http://localhost/smo_sim")
    return smo_o2endpoint


def get_stx_access_info():
    authurl = os.environ.get("STX_AUTH_URL", "http://192.168.204.1:5000/v3")
    username = os.environ.get("STX_USERNAME", "admin")
    pswd = os.environ.get("STX_PASSWORD", "passwd1")
    stx_access_info = (authurl, username, pswd)
    return stx_access_info

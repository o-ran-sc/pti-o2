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
import sys
from urllib.parse import urlparse

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


_DEFAULT_DCMANAGER_URL = "http://192.168.204.1:8119/v1.0"
_DEFAULT_STX_URL = "http://192.168.204.1:5000/v3"


def get_postgres_uri():
    host = os.environ.get("DB_HOST", "localhost")
    port = 54321 if host == "localhost" else 5432
    password = os.environ.get("DB_PASSWORD", "o2ims123")
    user, db_name = "o2ims", "o2ims"
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"


def get_api_url():
    host_interal = os.environ.get("API_HOST", "localhost")
    host_external = os.environ.get("API_HOST_EXTERNAL_FLOATING")
    host = host_interal if host_external is None or host_external == '' \
        else host_external

    port_internal = 5005 if host == "localhost" else 80
    port_external = 30205
    port = port_internal if host_external is None or host_external == '' \
        else port_external
    return f"http://{host}:{port}"


def get_root_api_base():
    return "/"


def get_o2ims_api_base():
    return get_root_api_base() + 'o2ims_infrastructureInventory/v1'


def get_provision_api_base():
    return get_root_api_base() + 'provision/v1'


def get_o2dms_api_base():
    return get_root_api_base() + "o2dms/v1"


def get_redis_host_and_port():
    host = os.environ.get("REDIS_HOST", "localhost")
    port = 63791 if host == "localhost" else 6379
    return dict(host=host, port=port)


def get_smo_o2endpoint():
    smo_o2endpoint = os.environ.get(
        "SMO_O2_ENDPOINT", "http://localhost/smo_sim")
    return smo_o2endpoint


def get_stx_access_info(region_name="RegionOne", subcloud_hostname: str = ""):
    # authurl = os.environ.get("STX_AUTH_URL", "http://192.168.204.1:5000/v3")
    # username = os.environ.get("STX_USERNAME", "admin")
    # pswd = os.environ.get("STX_PASSWORD", "passwd1")
    # stx_access_info = (authurl, username, pswd)
    try:
        client_args = dict(
            auth_url=os.environ.get('OS_AUTH_URL', _DEFAULT_STX_URL),
            username=os.environ.get('OS_USERNAME', "admin"),
            api_key=os.environ.get('OS_PASSWORD', "fakepasswd1"),
            project_name=os.environ.get('OS_PROJECT_NAME', "admin"),
        )
        # dc_client_args = dict(
        #     auth_url=os.environ['OS_AUTH_URL'],
        #     username=os.environ['OS_USERNAME'],
        #     api_key=os.environ['OS_PASSWORD'],
        #     project_name=os.environ['OS_PROJECT_NAME'],
        #     user_domain_name=os.environ['OS_USER_DOMAIN_NAME'],
        #     project_domain_name=os.environ['OS_PROJECT_NAME'],
        #     project_domain_id=os.environ['OS_PROJECT_DOMAIN_ID']
        # )
    except KeyError:
        logger.error('Please source your RC file before execution, '
                     'e.g.: `source ~/downloads/admin-rc.sh`')
        sys.exit(1)

    os_client_args = {}
    for key, val in client_args.items():
        os_client_args['os_{key}'.format(key=key)] = val
    if "" != subcloud_hostname:
        orig_auth_url = urlparse(_DEFAULT_STX_URL)
        new_auth_url = orig_auth_url._replace(
            netloc=orig_auth_url.netloc.replace(
                orig_auth_url.hostname, subcloud_hostname))
        # new_auth_url = new_auth_url._replace(
        #     netloc=new_auth_url.netloc.replace(str(new_auth_url.port),
        # "18002"))
        new_auth_url = new_auth_url._replace(
            scheme=new_auth_url.scheme.
            replace(new_auth_url.scheme, 'https'))
        os_client_args['os_auth_url'] = new_auth_url.geturl()
        os_client_args['os_endpoint_type'] = 'public'
        os_client_args['insecure'] = True
    # os_client_args['system_url'] = os_client_args['os_auth_url']
    os_client_args['os_password'] = os_client_args.pop('os_api_key')
    os_client_args['os_region_name'] = region_name
    os_client_args['api_version'] = 1
    # os_client_args['user_domain_name'] = 'Default'
    # os_client_args['project_domain_name'] = 'Default'
    return os_client_args


def get_dc_access_info():
    try:
        client_args = dict(
            auth_url=os.environ.get('OS_AUTH_URL', _DEFAULT_STX_URL),
            username=os.environ.get('OS_USERNAME', "admin"),
            api_key=os.environ.get('OS_PASSWORD', "fakepasswd1"),
            project_name=os.environ.get('OS_PROJECT_NAME', "admin"),
        )
    except KeyError:
        logger.error('Please source your RC file before execution, '
                     'e.g.: `source ~/downloads/admin-rc.sh`')
        sys.exit(1)

    os_client_args = {}
    for key, val in client_args.items():
        os_client_args['os_{key}'.format(key=key)] = val
    auth_url = urlparse(os_client_args.pop('os_auth_url'))
    dcmanager_url = urlparse(_DEFAULT_DCMANAGER_URL)
    dcmanager_url = dcmanager_url._replace(netloc=dcmanager_url.netloc.replace(
        dcmanager_url.hostname, auth_url.hostname))

    os_client_args['dcmanager_url'] = dcmanager_url.geturl()
    os_client_args['auth_url'] = auth_url.geturl()
    os_client_args['username'] = os_client_args.pop('os_username')
    os_client_args['api_key'] = os_client_args.pop('os_api_key')
    os_client_args['project_name'] = os_client_args.pop('os_project_name')
    os_client_args['user_domain_name'] = 'Default'
    os_client_args['project_domain_name'] = 'Default'

    return os_client_args


def get_k8s_api_endpoint():
    K8S_KUBECONFIG = os.environ.get("K8S_KUBECONFIG", None)
    K8S_APISERVER = os.environ.get("K8S_APISERVER", None)
    K8S_TOKEN = os.environ.get("K8S_TOKEN", None)
    return K8S_KUBECONFIG, K8S_APISERVER, K8S_TOKEN


def get_helm_cli():
    return '/usr/local/bin/helm'


def get_system_controller_as_respool():
    return True

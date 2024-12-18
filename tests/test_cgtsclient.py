#!/usr/bin/env python3

import os
from cgtsclient.client import get_client as get_stx_client
from cgtsclient.exc import EndpointException
from dcmanagerclient.api.client import client as get_dc_client


def get_stx_client_args():
    """Get StarlingX client arguments from environment variables"""
    client_args = dict(
        auth_url=os.environ.get('OS_AUTH_URL', 'http://192.168.204.1:5000/v3'),
        username=os.environ.get('OS_USERNAME', 'admin'),
        api_key=os.environ.get('OS_PASSWORD', 'fakepasswd1'),
        project_name=os.environ.get('OS_PROJECT_NAME', 'admin'),
    )
    return client_args


def get_stx_access_info():
    """Convert client args to StarlingX format"""
    try:
        client_args = get_stx_client_args()
    except KeyError as e:
        print('Error: Please source your RC file before execution')
        print('e.g.: source ~/downloads/admin-rc.sh')
        raise e

    os_client_args = {}
    for key, val in client_args.items():
        os_client_args['os_' + key] = val

    os_client_args['os_password'] = os_client_args.pop('os_api_key')
    os_client_args['os_region_name'] = os.environ.get('OS_REGION_NAME',
                                                      'RegionOne')
    os_client_args['api_version'] = 1

    # Add certificate related parameters
    os_client_args['insecure'] = os.environ.get(
        'OS_INSECURE', "False").lower() == "true"
    os_client_args['ca_file'] = os.environ.get(
        'OS_CACERT', '/etc/ssl/certs/ca-certificates.crt')
    os_client_args['cert_file'] = os.environ.get('OS_CERT', None)
    os_client_args['key_file'] = os.environ.get('OS_KEY', None)

    return os_client_args


def get_dc_access_info():
    """Convert client args to DC Manager format"""
    try:
        client_args = get_stx_client_args()
    except KeyError as e:
        print('Error: Please source your RC file before execution')
        print('e.g.: source ~/downloads/admin-rc.sh')
        raise e

    os_client_args = {}
    for key, val in client_args.items():
        os_client_args['os_' + key] = val

    # Convert to dcmanager format
    dc_client_args = {
        'auth_url': os_client_args['os_auth_url'],
        'username': os_client_args['os_username'],
        'api_key': os_client_args['os_api_key'],
        'project_name': os_client_args['os_project_name'],
        'user_domain_name': 'Default',
        'project_domain_name': 'Default',
        'insecure': os.environ.get('OS_INSECURE', "False").lower() == "true",
        'cacert': os.environ.get('OS_CACERT',
                                 '/etc/ssl/certs/ca-certificates.crt')
    }

    # Set dcmanager URL
    dc_port = os.environ.get("DCMANAGER_API_PORT", "8119")
    dc_path = os.environ.get("DCMANAGER_API_PATH", "/v1.0")
    auth_url = os.environ.get("DCMANAGER_OS_AUTH_URL")

    if not auth_url:
        from urllib.parse import urlparse
        u = urlparse(dc_client_args['auth_url'])
        auth_url = u._replace(
            netloc=f"{u.hostname}:{dc_port}", path=dc_path).geturl()

    dc_client_args['dcmanager_url'] = auth_url

    return dc_client_args


def test_stx_client():
    """Test StarlingX client connection"""
    try:
        # Get client configuration
        os_client_args = get_stx_access_info()
        print("\nTrying to connect with STX args:")
        for k, v in os_client_args.items():
            print("{0}: {1}".format(k, v))

        # Create client
        print("\nCreating StarlingX client...")
        client = get_stx_client(**os_client_args)

        # Test system information retrieval
        print("\nGetting system information...")
        systems = client.isystem.list()

        if systems:
            system = systems[0]
            print("\nSystem information:")
            print("Name: {0}".format(system.name))
            print("UUID: {0}".format(system.uuid))
            print("System Type: {0}".format(system.system_type))
            print("System Mode: {0}".format(system.system_mode))
            print("Software Version: {0}".format(system.software_version))
            print("Capabilities: {0}".format(system.capabilities))
        else:
            print("No systems found!")

    except EndpointException as e:
        print("\nEndpoint Error: {0}".format(str(e)))
    except Exception as e:
        print("\nError: {0}".format(str(e)))
        raise


def test_dc_client():
    """Test DC Manager client connection"""
    try:
        # Get client configuration
        dc_client_args = get_dc_access_info()
        print("\nTrying to connect with DC args:")
        for k, v in dc_client_args.items():
            print("{0}: {1}".format(k, v))

        # Create DC Manager client
        print("\nCreating DC Manager client...")
        client = get_dc_client(**dc_client_args)

        # Get subcloud list
        print("\nGetting subcloud list...")
        subclouds = client.subcloud_manager.list_subclouds()

        if subclouds:
            print("\nFound {0} subclouds:".format(len(subclouds)))
            for subcloud in subclouds:
                print("\nSubcloud information:")
                print("Name: {0}".format(subcloud.name))
                print("Region Name: {0}".format(subcloud.region_name))
                print("Management State: {0}".format(
                    subcloud.management_state))
                print("Availability Status: {0}".format(
                    subcloud.availability_status))
                print("Sync Status: {0}".format(subcloud.sync_status))
        else:
            print("No subclouds found!")

    except Exception as e:
        print("\nDC Manager Error: {0}".format(str(e)))
        raise


if __name__ == "__main__":
    print("Testing StarlingX and DC Manager Client Connections...")
    print("\n=== Testing StarlingX Client ===")
    test_stx_client()
    print("\n=== Testing DC Manager Client ===")
    test_dc_client()

########
# Copyright (c) 2019 Cloudify Platform Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

import json

from .exceptions import CloudifyHelmSDKError
from helm_sdk.utils import (
    run_subprocess,
    prepare_parameter,
    prepare_set_parameters,
    validate_no_collisions_between_params_and_flags)

# Helm cli flags names
HELM_KUBECONFIG_FLAG = 'kubeconfig'
HELM_KUBE_API_SERVER_FLAG = 'kube-apiserver'
HELM_KUBE_TOKEN_FLAG = 'kube-token'
HELM_VALUES_FLAG = 'values'
APPEND_FLAG_STRING = '--{name}={value}'


class Helm(object):

    def __init__(self,
                 logger,
                 binary_path,
                 environment_variables
                 ):
        self.binary_path = binary_path
        self.logger = logger
        if not isinstance(environment_variables, dict):
            raise Exception(
                "Unexpected type for environment variables (should be a "
                "dict): {0}".format(type(
                    environment_variables)))

        self.env = environment_variables

    def execute(self, command, return_output=False):
        return run_subprocess(
            command,
            self.logger,
            cwd=None,
            additional_env=self.env,
            additional_args=None,
            return_output=return_output)

    def _helm_command(self, args):
        cmd = [self.binary_path]
        cmd.extend(args)
        return cmd

    @staticmethod
    def handle_auth_params(cmd,
                           kubeconfig=None,
                           token=None,
                           apiserver=None):
        """
            Validation of authentication params.
            Until helm will support --insecure, kubeconfig must be provided.
            :param kubeconfig: Kubeconfig file path
            :param: token: bearer token used for authentication.
            :param: apiserver: the address and the port for the Kubernetes API
            server.
        """
        if kubeconfig is None:
            raise CloudifyHelmSDKError(
                'Must provide kubeconfig file path.')
        else:
            cmd.append(APPEND_FLAG_STRING.format(name=HELM_KUBECONFIG_FLAG,
                                                 value=kubeconfig))

        if token:
            cmd.append(APPEND_FLAG_STRING.format(name=HELM_KUBE_TOKEN_FLAG,
                                                 value=token))

        if apiserver:
            cmd.append(
                APPEND_FLAG_STRING.format(name=HELM_KUBE_API_SERVER_FLAG,
                                          value=apiserver))

    def install(self,
                name,
                chart,
                flags=None,
                set_values=None,
                values_file=None,
                kubeconfig=None,
                token=None,
                apiserver=None,
                **_):
        """
        Execute helm install command.
        :param name: name for the created release.
        :param chart: chart name to install.
        :param flags: list of flags to add to the install command.
        :param set_values: list of variables and their values for --set.
        :param kubeconfig: path to kubeconfig file.
        :param values_file: values file path.
        :param token: bearer token used for authentication.
        :param apiserver: the address and the port for the Kubernetes API
        server.
        :return output of install command.
        """
        cmd = ['install', name, chart, '--wait', '--output=json']
        self.handle_auth_params(cmd, kubeconfig, token, apiserver)
        if values_file:
            cmd.append(APPEND_FLAG_STRING.format(name=HELM_VALUES_FLAG,
                                                 value=values_file))
        flags = flags or []
        validate_no_collisions_between_params_and_flags(flags)
        cmd.extend([prepare_parameter(flag) for flag in flags])
        set_arguments = set_values or []
        cmd.extend(prepare_set_parameters(set_arguments))
        output = self.execute(self._helm_command(cmd), True)
        return json.loads(output)

    def uninstall(self,
                  name,
                  flags=None,
                  kubeconfig=None,
                  token=None,
                  apiserver=None,
                  **_):
        cmd = ['uninstall', name]
        self.handle_auth_params(cmd, kubeconfig, token, apiserver)
        flags = flags or []
        validate_no_collisions_between_params_and_flags(flags)
        cmd.extend([prepare_parameter(flag) for flag in flags])
        self.execute(self._helm_command(cmd))

    def repo_add(self,
                 name,
                 repo_url,
                 flags=None,
                 **_):
        cmd = ['repo', 'add', name, repo_url]
        flags = flags or []
        cmd.extend([prepare_parameter(flag) for flag in flags])
        self.execute(self._helm_command(cmd))

    def repo_remove(self,
                    name,
                    flags=None,
                    **_):
        cmd = ['repo', 'remove', name]
        flags = flags or []
        cmd.extend([prepare_parameter(flag) for flag in flags])
        self.execute(self._helm_command(cmd))

    def repo_list(self):
        cmd = ['repo', 'list', '--output=json']
        output = self.execute(self._helm_command(cmd), True)
        return json.loads(output)

    def repo_update(self, flags):
        cmd = ['repo', 'update']
        flags = flags or []
        cmd.extend([prepare_parameter(flag) for flag in flags])
        self.execute(self._helm_command(cmd))

    def upgrade(self,
                release_name,
                chart=None,
                flags=None,
                set_values=None,
                values_file=None,
                kubeconfig=None,
                token=None,
                apiserver=None,
                **_):
        """
        Execute helm upgrade command.
        :param release_name: name of the release to upgrade.
        :param chart: The chart to upgrade the release with.
        The chart argument can be either: a chart reference('example/mariadb'),
        a packaged chart, or a fully qualified URL.
        :param flags: list of flags to add to the upgrade command.
        :param set_values: list of variables and their values for --set.
        :param kubeconfig: path to kubeconfig file.
        :param values_file: values file path.
        :param token: bearer token used for authentication.
        :param apiserver: the address and the port for the Kubernetes API
        server.
        :return output of helm upgrade command.
        """
        if not chart:
            raise CloudifyHelmSDKError(
                'Must provide chart for upgrade release.')
        cmd = ['upgrade', release_name, chart, '--atomic', '-o=json']
        self.handle_auth_params(cmd, kubeconfig, token, apiserver)
        if values_file:
            cmd.append(APPEND_FLAG_STRING.format(name=HELM_VALUES_FLAG,
                                                 value=values_file))
        flags = flags or []
        validate_no_collisions_between_params_and_flags(flags)
        cmd.extend([prepare_parameter(flag) for flag in flags])
        set_arguments = set_values or []
        cmd.extend(prepare_set_parameters(set_arguments))
        output = self.execute(self._helm_command(cmd), True)
        return json.loads(output)

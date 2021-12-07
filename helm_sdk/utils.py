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

import os
import copy
import threading
import subprocess

from helm_sdk.filters import obfuscate_passwords

from helm_sdk._compat import StringIO, text_type
from helm_sdk.exceptions import CloudifyHelmSDKError

FLAGS_LIST_TO_VALIDATE = ['kube-apiserver', 'kube-token', 'kubeconfig']


def run_subprocess(command,
                   logger,
                   cwd=None,
                   additional_env=None,
                   additional_args=None,
                   return_output=False):
    if additional_args is None:
        additional_args = {}
    args_to_pass = copy.deepcopy(additional_args)
    if additional_env:
        passed_env = args_to_pass.setdefault('env', {})
        passed_env.update(os.environ)
        passed_env.update(additional_env)

    logger.info(
        "Running: command={cmd}, cwd={cwd}, additional_args={args}".format(
            cmd=obfuscate_passwords(command),
            cwd=cwd,
            args=obfuscate_passwords(args_to_pass)))

    process = subprocess.Popen(
        args=command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=None,
        cwd=cwd,
        **args_to_pass)

    if return_output:
        stdout_consumer = CapturingOutputConsumer(
            process.stdout)
    else:
        stdout_consumer = LoggingOutputConsumer(
            process.stdout, logger, "<out> ")
    stderr_consumer = LoggingOutputConsumer(
        process.stderr, logger, "<err> ")

    return_code = process.wait()
    stdout_consumer.join()
    stderr_consumer.join()

    if return_code:
        raise subprocess.CalledProcessError(return_code,
                                            [obfuscate_passwords(cmd_element)
                                             for cmd_element in command])

    output = stdout_consumer.buffer.getvalue() if return_output else None
    logger.info("Returning output:\n{0}".format(
        obfuscate_passwords(output) if output is not None else '<None>'))

    return output


# Stolen from the script plugin, until this class
# moves to a utils module in cloudify-common.
class OutputConsumer(object):
    def __init__(self, out):
        self.out = out
        self.consumer = threading.Thread(target=self.consume_output)
        self.consumer.daemon = True

    def consume_output(self):
        for line in self.out:
            self.handle_line(line)
        self.out.close()

    def handle_line(self, line):
        raise NotImplementedError("Must be implemented by subclass.")

    def join(self):
        self.consumer.join()


class LoggingOutputConsumer(OutputConsumer):
    def __init__(self, out, logger, prefix):
        OutputConsumer.__init__(self, out)
        self.logger = logger
        self.prefix = prefix
        self.consumer.start()

    def handle_line(self, line):
        self.logger.info(
            "{0}{1}".format(text_type(self.prefix),
                            obfuscate_passwords(
                                line.decode('utf-8').rstrip('\n'))))


class CapturingOutputConsumer(OutputConsumer):
    def __init__(self, out):
        OutputConsumer.__init__(self, out)
        self.buffer = StringIO()
        self.consumer.start()

    def handle_line(self, line):
        self.buffer.write(line.decode('utf-8'))

    def get_buffer(self):
        return self.buffer


def prepare_parameter(arg_dict):
    """
    Prepare single parameter.
    :param arg_dict: dictionary with the name of the flag and value(optional)
    :return: "--name=value" or -"-name"
    """
    try:
        param_string = "--" + arg_dict["name"]
        return param_string + '=' + arg_dict.get("value") if arg_dict.get(
            "value") else param_string
    except KeyError:
        raise CloudifyHelmSDKError("Parameter name doesen't exist.")


def prepare_set_parameters(set_values):
    """
    Prepare set parameters for install command.
    :param set_values: list of dictionaries with the name of the variable to
    set command and its value.
    :return list like: ["--set", "name=value","--set",
    """
    set_list = []
    for set_dict in set_values:
        set_list.append('--set')
        try:
            set_list.append(set_dict["name"] + "=" + set_dict["value"])
        except KeyError:
            raise CloudifyHelmSDKError(
                "\"set\" parameter name or value is missing.")
    return set_list


def validate_no_collisions_between_params_and_flags(flags):
    if [flag for flag in flags if flag['name'] in FLAGS_LIST_TO_VALIDATE]:
        raise CloudifyHelmSDKError(
            'Please do not pass {flags_list} under "flags" property,'
            'each of them has a known property.'.format(
                flags_list=FLAGS_LIST_TO_VALIDATE))

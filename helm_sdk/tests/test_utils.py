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

import unittest

from helm_sdk.exceptions import CloudifyHelmSDKError
from helm_sdk.utils import (
    prepare_parameter,
    prepare_set_parameters,
    validate_no_collisions_between_params_and_flags)


class TestUtils(unittest.TestCase):

    def test_prepare_parameter(self):
        param_dict = {'name': 'param1'}
        self.assertEqual(prepare_parameter(param_dict), '--param1')
        param_dict.update({'value': 'value1'})
        self.assertEqual(prepare_parameter(param_dict), '--param1=value1')

    def test_prepare_set_parameters(self):
        set_no_val = [{'name': 'x'}]
        with self.assertRaisesRegexp(
                CloudifyHelmSDKError,
                "\"set\" parameter name or value is missing"):
            prepare_set_parameters(set_no_val)

        with self.assertRaisesRegexp(
                CloudifyHelmSDKError,
                "\"set\" parameter name or value is missing"):
            set_no_name = [{'value': 'y'}]
            prepare_set_parameters(set_no_name)
        # Now set_dict_no_val is a valid set parameter dictionary
        valid_set_list = [{'name': 'x', 'value': 'y'}]
        self.assertEqual(prepare_set_parameters(valid_set_list),
                         ['--set', 'x=y'])

    def test_validate_no_collisions_between_params_and_flags(self):
        fake_flags = [{'name': 'kube-apiserver', 'value': 'https://0.0.0.0'}]
        with self.assertRaisesRegexp(CloudifyHelmSDKError,
                                     "Please do not pass"):
            validate_no_collisions_between_params_and_flags(fake_flags)
        fake_flags = [{'name': 'debug'}]
        self.assertEqual(
            validate_no_collisions_between_params_and_flags(fake_flags),
            None)
        fake_flags = []
        self.assertEqual(
            validate_no_collisions_between_params_and_flags(fake_flags),
            None)

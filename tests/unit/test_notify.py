# Copyright (C) 2023 Wind River Systems, Inc.
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
from o2ims.service.command import notify_handler


def test_handle_filter():
    assert notify_handler.handle_filter(
        "(eq,resourceId,resid1234)", "ResourceInfo") == (
        1, ['(eq,resourceId,resid1234)'])
    assert notify_handler.handle_filter(
        "[(eq,objectType,ResourceInfo);(eq,resourceId,resid1234)]",
        "ResourceInfo") == (
        1, ['(eq,objectType,ResourceInfo);(eq,resourceId,resid1234)'])
    assert notify_handler.handle_filter(
        "[eq,objectType,ResourceTypeInfo|eq,objectType,ResourcePoolInfo]",
        "ResourceInfo") == (0, [])
    assert notify_handler.handle_filter(
        "", "ResourceInfo") is None
    assert notify_handler.handle_filter(
        "", "ResourceTypeInfo") is None
    assert notify_handler.handle_filter(
        "[eq,objectType,ResourceInfo|eq,objectType,ResourceTypeInfo]",
        "ResourceInfo") == (1, ['eq,objectType,ResourceInfo'])
    assert notify_handler.handle_filter(
        "[(eq,objectType,ResourceInfo);(eq,resourceId,resourceid1234) | " +
        "(eq,objectType,ResourceInfo);(eq,resourceTypeId,restype1234)",
        "ResourceInfo") == \
        (2, ['(eq,objectType,ResourceInfo);(eq,resourceId,resourceid1234) ',
             ' (eq,objectType,ResourceInfo);(eq,resourceTypeId,restype1234)'
             ])
    assert notify_handler.handle_filter(
        "(eq,objectType,ResourceTypeInfo)|(eq,objectType,ResourcePoolInfo)" +
        "|(eq,objectType,CloudInfo)|(eq,objectType,ResourceInfo)",
        "DeploymentManagerInfo"
    ) == (0, [])

    assert notify_handler.handle_filter(
        "(eq,objectType,ResourceInfo)", "ResourceInfo") == (
        1, ['(eq,objectType,ResourceInfo)'])

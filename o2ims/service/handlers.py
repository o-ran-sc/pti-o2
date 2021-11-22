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

# pylint: disable=unused-argument
from __future__ import annotations
# from dataclasses import asdict
from typing import List, Dict, Callable, Type
# TYPE_CHECKING
from o2ims.domain import commands, events
from o2ims.service.auditor import ocloud_handler

# if TYPE_CHECKING:
#     from . import unit_of_work


class InvalidResourceType(Exception):
    pass


EVENT_HANDLERS = {
}  # type: Dict[Type[events.Event], List[Callable]]


COMMAND_HANDLERS = {
    commands.UpdateOCloud: ocloud_handler.update_ocloud,
}  # type: Dict[Type[commands.Command], Callable]

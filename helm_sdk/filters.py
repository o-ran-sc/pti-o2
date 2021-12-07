# Copyright (c) 2016-2020 Cloudify Platform Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from copy import deepcopy
import re

from ._compat import text_type

OBFUSCATION_KEYWORDS = ('PASSWORD', 'SECRET', 'TOKEN',)
OBFUSCATION_RE = re.compile(r'((password|secret|token)(:|=)\s*)(\S+)',
                            flags=re.IGNORECASE | re.MULTILINE)
OBFUSCATED_SECRET = 'x' * 16


def obfuscate_passwords(obj):
    """Obfuscate passwords in dictionary or list of dictionaries.

    Returns a copy of original object with elements potentially containing
    passwords obfuscated.  A copy.deepcopy() is used for copying dictionaries
    but only when absolutely necessary.  If a given object does not contain
    any passwords, original is returned and deepcopy never performed.
    """
    if isinstance(obj, (text_type, bytes,)):
        return OBFUSCATION_RE.sub('\\1{0}'.format(OBFUSCATED_SECRET), obj)
    if isinstance(obj, list):
        return [obfuscate_passwords(elem) for elem in obj]
    if not isinstance(obj, dict):
        return obj
    result = obj
    for k, v in list(result.items()):
        if any(x for x in OBFUSCATION_KEYWORDS if x in k.upper()):
            a_copy = deepcopy(result)
            a_copy[k] = OBFUSCATED_SECRET
            result = a_copy
        if isinstance(v, (dict, list,)):
            obfuscated_v = obfuscate_passwords(v)
            if obfuscated_v is not v:
                a_copy = deepcopy(result)
                a_copy[k] = obfuscated_v
                result = a_copy
    return result


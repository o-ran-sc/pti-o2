# Copyright (C) 2021-2022 Wind River Systems, Inc.
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

from urllib.parse import urlparse
from flask import abort

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)

PAGE_PARAM = 'nextpage_opaque_marker'


def link_header(full_path: str, ret):
    base_url = urlparse(full_path)
    count = ret.pop('count')
    page_total = ret.pop('page_total')
    page_current = ret.pop('page_current')

    if page_current > page_total:
        abort(400, "Page size {} bad request.".format(page_current))

    if 0 == count:
        return [], {'X-Total-Count': count}

    query = "&".join(["{}".format(q) for q in base_url.query.split(
        '&') if q.split('=')[0] != PAGE_PARAM])
    if query != '':
        query = query + '&'

    link_list = []
    if (page_current > 1):
        parsed = base_url._replace(query=query + PAGE_PARAM + '=1')
        link_list.append('<' + parsed.geturl() + '>; rel="first"')
    if (page_current > 1):
        parsed = base_url._replace(
            query=query + PAGE_PARAM + '=' + str(page_current - 1))
        link_list.append('<' + parsed.geturl() + '>; rel="prev"')
    if (page_current < page_total):
        parsed = base_url._replace(
            query=query + PAGE_PARAM + '=' + str(page_current + 1))
        link_list.append('<' + parsed.geturl() + '>; rel="next"')
    if (page_current < page_total):
        parsed = base_url._replace(
            query=query + PAGE_PARAM + '=' + str(page_total))
        link_list.append('<' + parsed.geturl() + '>; rel="last"')
    if 0 == len(link_list):
        return ret.pop('results'), {'X-Total-Count': count}
    link = ','.join(link_list)
    return ret.pop('results'), {'X-Total-Count': count, 'Link': link}

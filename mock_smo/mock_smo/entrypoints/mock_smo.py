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

import json
import redis
import http.client
from flask import Flask, request
from flask.helpers import url_for

import mock_smo.config as config
import mock_smo.logging as logging
logger = logging.get_logger(__name__)

apibase = config.get_o2ims_api_base()
app = Flask(__name__)

r = redis.Redis(**config.get_redis_host_and_port())
REDIS_SUB_KEY = 'mock_smo_sub_key'
REDIS_O2IMS_URL = 'mock_smo_o2ims_url'


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        consumerSubscriptionId = request.form['consumerSubscriptionId']
        sub_id = subscription_ims(url, consumerSubscriptionId)
        return """
<h1>Subscribed O2IMS</h1>
<h3>Subscription ID: %s</h3>
<h3>Subscribed O2IMS URL: %s</h3>
<a href="%s">
   <input type="button" value="Unsubscription" />
</a>
""" % (sub_id, url, url_for('unsubscription'))
    return """
<h1>Subscribe O2IMS</h1>
<form method="POST">
    O2 IMS URL: <input type="text" name="url" value="api:80"></br>
    Consumer Subscription ID: <input type="text" name="consumerSubscriptionId"></br>
    <input type="submit" value="Submit">
</form>
"""


@app.route('/unsubscription')
def unsubscription():
    sub_key = r.get(REDIS_SUB_KEY)
    logger.info('Subscription key is {}'.format(sub_key))
    if sub_key is None:
        return '<h1>Already unsubscribed</h1>'
    url = r.get(REDIS_O2IMS_URL).decode('utf-8')
    logger.info('O2 IMS API is: {}'.format(url))
    unsubscription_ims(url, sub_key.decode('utf-8'))
    r.delete(REDIS_O2IMS_URL)
    r.delete(REDIS_SUB_KEY)
    return """
<h1>Unsubscribed O2IMS</h1>
<a href="/">
   <input type="button" value="Go Back" />
</a>
"""


@app.route('/callback', methods=['POST'])
def callback():
    logger.info('Callback data: {}'.format(request.get_data()))
    return '', 202


def subscription_ims(url, consumerSubscriptionId):
    sub_key = r.get(REDIS_SUB_KEY)
    logger.info('Subscription key is {}'.format(sub_key))
    if sub_key is not None:
        return sub_key.decode('utf-8')

    logger.info(request.host_url)
    conn = http.client.HTTPConnection(url)
    headers = {'Content-type': 'application/json'}
    post_val = {
        'callback': 'http://mock_smo:80' + url_for('callback'),
        'consumerSubscriptionId': consumerSubscriptionId,
        'filter': '["pserver"]'  # '["pserver","pserver_mem"]'
    }
    json_val = json.dumps(post_val)
    conn.request('POST', apibase+'/subscriptions', json_val, headers)
    resp = conn.getresponse()
    data = resp.read().decode('utf-8')
    logger.info('Subscription response: {} {}, data: {}'.format(
        resp.status, resp.reason, data))
    json_data = json.loads(data)

    r.set(REDIS_SUB_KEY, json_data['subscriptionId'])
    r.set(REDIS_O2IMS_URL, url)
    return json_data['subscriptionId']


def unsubscription_ims(url, subId):
    conn = http.client.HTTPConnection(url)
    conn.request('DELETE', apibase + '/subscriptions/' + subId)
    resp = conn.getresponse()
    logger.info('Unsubscription response: {} {}'.format(
        resp.status, resp.reason))

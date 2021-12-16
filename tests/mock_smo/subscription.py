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

import redis
import json
import signal
import http.client
# from o2common.config import config

# from o2common.helper import o2logging
# logger = o2logging.get_logger(__name__)

# r = redis.Redis(**config.get_redis_host_and_port())
r = redis.Redis(host='127.0.0.1', port=63791)

# apibase = config.get_o2ims_api_base()
# url = config.get_api_url()
apibase = '/o2ims_infrastructureInventory/v1'
url = '127.0.0.1:5005'


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Subscription(metaclass=Singleton):

    def __init__(self, sub_id='') -> None:
        self.url = url
        self.subId = sub_id

    def subscription_ims(self):
        conn = http.client.HTTPConnection(self.url)
        headers = {'Content-type': 'application/json'}
        post_val = {
            'callback': self.url,
            'consumerSubscriptionId': 'mock_smo',
            'filter': '["pserver","pserver_ram"]'
        }
        json_val = json.dumps(post_val)
        conn.request('POST', apibase+'/subscriptions', json_val, headers)
        resp = conn.getresponse()
        data = resp.read().decode('utf-8')
        print(resp.status, resp.reason)
        print(data)
        json_data = json.loads(data)
        self.subId = json_data['subscriptionId']

    def subscription_mq(self):
        sub = r.pubsub(ignore_subscribe_messages=True)
        sub.subscribe(self.subId)

        for m in sub.listen():
            try:
                # logger.info("handling %s", m)
                print("handling %s", m)
                channel = m['channel'].decode("UTF-8")
                if channel == self.subId:
                    datastr = m['data']
                    data = json.loads(datastr)
                    # logger.info('notification: {}'.format(data))
                    print('notification: {}'.format(data))
                else:
                    # logger.info("unhandled:{}".format(channel))
                    print("unhandled:{}".format(channel))
            except Exception as ex:
                # logger.warning("{}".format(str(ex)))
                print("[WARNING]{}".format(str(ex)))
                continue

    def unsubscription_ims(self):
        conn = http.client.HTTPConnection(self.url)
        conn.request('DELETE', apibase + '/subscriptions/' + self.subId)
        resp = conn.getresponse()
        print(resp.status, resp.reason)


def handler(signum, frame):
    print('\nCtrl-c was pressed. Call to delete subscription')
    sub = Subscription()
    sub.unsubscription_ims()
    exit()


def main():
    sub = Subscription()
    sub.subscription_ims()
    signal.signal(signal.SIGINT, handler)
    sub.subscription_mq()


if __name__ == "__main__":
    main()

# locust for load testing

## Start procedure

Here is the sample command to run one master worker with 7 sub worker

```bash
# main worker:  
locust -f ocloud.py -H http://128.224.115.34:30205 --master

# worker_1:  
locust -f ocloud.py --worker
#worker_2:  
locust -f ocloud.py --worker
#worker_3:  
locust -f ocloud.py --worker
#worker_4:  
locust -f ocloud.py --worker
#worker_5:  
locust -f ocloud.py --worker
#worker_6:  
locust -f ocloud.py --worker
#worker_7:  
locust -f ocloud.py --worker
```

If you can use goreman to run [goreman](github.com/mattn/goreman), feel free to use it.

```bash
cat Procfile<<
ocloud:  locust -f ocloud.py -H http://128.224.115.34:30205 --master
ocloud_1:  locust -f ocloud.py --worker
ocloud_2:  locust -f ocloud.py --worker
ocloud_3:  locust -f ocloud.py --worker
ocloud_4:  locust -f ocloud.py --worker
ocloud_5:  locust -f ocloud.py --worker
ocloud_6:  locust -f ocloud.py --worker
ocloud_7:  locust -f ocloud.py --worker
>>EOF
```

Run locust with 7 sub workers through goreman
```bash
goreman -f Procfile start
```
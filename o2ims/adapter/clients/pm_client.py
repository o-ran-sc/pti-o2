# Copyright (C) 2025 Wind River Systems, Inc.
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

from typing import List
from elasticsearch import Elasticsearch
from cgtsclient.client import get_client as get_stx_client
from o2common.config import config
from o2common.service.client.base_client import BaseClient
from o2ims.domain import performance_obj as pm_obj

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


class MeasurementJobClient(BaseClient):
    def __init__(self, uow, driver=None):
        super().__init__()
        self.driver = driver if driver else EsPmClientImp()
        self.uow = uow

    def _get(self, id):
        return self.driver.getMeasurementJobInfo(id)

    def _list(self, **filters) -> List[pm_obj.MeasurementJob]:
        return self.driver.getMeasurementJobList(**filters)

    def _set_stx_client(self):
        pass


class EsPmClientImp(object):
    def __init__(self, es_client=None, stx_client=None):
        super().__init__()
        self.stxclient = stx_client if stx_client else self.getStxClient()
        self.es_client = es_client if es_client else self.getEsClient()

    def getStxClient(self):
        os_client_args = config.get_stx_access_info()
        config_client = get_stx_client(**os_client_args)
        return config_client

    def getEsClient(self):
        # Get OAM floating IP from iextoam
        try:
            iextoams = self.stxclient.iextoam.list()
            if iextoams and hasattr(iextoams[0], 'oam_floating_ip'):
                oam_ip = iextoams[0].oam_floating_ip
                logger.debug(f"Using OAM floating IP for ES connection: "
                             f"{oam_ip}")
            else:
                logger.warning("No OAM floating IP found, using default")
                return None
        except Exception as e:
            logger.warning(f"Failed to get OAM floating IP: {str(e)}, "
                           f"using default")
            return None

        # Get ES connection info using OAM floating IP
        es_config = config.get_es_access_info(ip=oam_ip)

        es_client = Elasticsearch(
            es_config['url'],
            basic_auth=(es_config['username'], es_config['password']),
            verify_certs=False
        )
        if not es_client.ping():
            logger.error("Failed to connect to Elasticsearch")
            return None
        return es_client

    def getMeasurementJobList(self, **filters) -> List[pm_obj.MeasurementJob]:
        # Check ES client connection first
        try:
            if not self.es_client or not self.es_client.ping():
                logger.warning("Elasticsearch client is not available")
                return []
        except Exception as e:
            logger.error(f"Failed to ping Elasticsearch: {str(e)}")
            return []

        filters['host_name'] = 'controller-0'
        query = self._build_query(**filters)
        try:
            response = self.es_client.search(
                body=query
            )
            return [self._convert_to_measurement_job(bucket)
                    for bucket in
                    response['aggregations']['unique_datasets']['buckets']]
        except Exception as e:
            logger.error(f"Error querying Elasticsearch: {str(e)}")
            return []

    def getMeasurementJobInfo(self, id) -> pm_obj.MeasurementJob:
        """Get detailed information for a specific measurement job."""
        query = {
            "size": 1,
            "query": {
                "bool": {
                    "must": [
                        {"term": {"event.dataset": id}},
                        {"term": {"host.name": "controller-0"}}
                    ]
                }
            }
        }

        try:
            response = self.es_client.search(
                body=query
            )
            if response['hits']['hits']:
                return self._convert_to_measurement_job_detail(
                    response['hits']['hits'][0], id)
            else:
                logger.warning(f"No data found for measurement job {id}")
                return None
        except Exception as e:
            logger.error(f"Error getting measurement job info for {id}: "
                         f"{str(e)}")
            raise

    @staticmethod
    def _build_query(**filters):
        must_conditions = [
            {
                "term": {
                    "type": "beats"
                }
            },
            {
                "term": {
                    "service.type": "system"
                }
            },
            {
                "range": {
                    "@timestamp": {
                        "gte": "now-1h"
                    }
                }
            }
        ]

        # Add host filter if provided
        if 'host_name' in filters:
            must_conditions.append({
                "term": {
                    "host.name": filters['host_name']
                }
            })

        query = {
            "size": 0,
            "query": {
                "bool": {
                    "must": must_conditions
                }
            },
            "aggs": {
                "unique_datasets": {
                    "terms": {
                        "field": "event.dataset",
                        "size": filters.get('size', 100)
                    }
                }
            }
        }

        return query

    @staticmethod
    def _convert_to_measurement_job(bucket) -> pm_obj.MeasurementJob:
        """Convert ES aggregation bucket to MeasurementJob."""
        job_id = bucket['key']  # e.g., "system.cpu"
        doc_count = bucket['doc_count']

        return pm_obj.MeasurementJob(
            job_id=job_id,
            consumer_job_id=f"consumer_{job_id}",
            state=pm_obj.MeasurementJobState.ACTIVE,
            status=pm_obj.MeasurementJobStatus.RUNNING,
            collection_interval=60,  # Default collection interval in seconds
            measurement_criteria=[{
                "measurementType": job_id,
                "measurementName": job_id,
                "sampleCount": doc_count
            }],
            preinstalled_job=True,
            resource_criteria={
                "resourceType": "pserver"
            }
        )

    @staticmethod
    def _convert_to_measurement_job_detail(hit, job_id) -> \
            pm_obj.MeasurementJob:
        """Convert ES document to detailed MeasurementJob."""
        source = hit['_source']
        return pm_obj.MeasurementJob(
            job_id=job_id,
            consumer_job_id=f"consumer_{job_id}",
            state=pm_obj.MeasurementJobState.ACTIVE,
            status=pm_obj.MeasurementJobStatus.RUNNING,
            collection_interval=60,
            measurement_criteria=[
                {
                    "measurementType": job_id,
                    "measurementName": source.get('event', {}).get('dataset'),
                    "performanceMetric": source.get('metricset', {}).
                    get('name', '')
                }
            ],
            resource_criteria={
                "resourceType": "pserver",
                "resourceName": source.get('host', {}).get('name')
            },
            preinstalled_job=True
        )

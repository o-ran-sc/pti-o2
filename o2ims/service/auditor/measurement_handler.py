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

# pylint: disable=unused-argument
from __future__ import annotations
import json

from o2common.service.unit_of_work import AbstractUnitOfWork
from o2ims.domain import commands, ocloud
from o2ims.domain.performance_obj import (
    MeasurementJob, MeasurementJobState, MeasurementJobStatus,
    MeasuredResource, CollectedMeasurement
)

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


def update_measurement(
    cmd: commands.UpdateMeasurement,
    uow: AbstractUnitOfWork
):
    job = cmd.measurement
    logger.info(f"Processing measurement job: "
                f"{job.performanceMeasurementJobId}")

    with uow:
        resourcepool = uow.resource_pools.get(cmd.parentid)

        # Check if measurement job already exists
        measurement_job = uow.measurement_jobs.get(
            job.performanceMeasurementJobId)
        if not measurement_job:
            # Create new measurement job
            measurement_job = create_measurement_job(job)
            # Link to resources
            restype = uow.resource_types.get_by_name('pserver')
            if restype:
                measurement_job.qualifiedResourceTypes.append(
                    restype.resourceTypeId)
                args = [ocloud.Resource.resourceTypeId ==
                        restype.resourceTypeId]
                hosts = uow.resources.list(resourcepool.resourcePoolId, *args)

                for host in hosts:
                    # Add measured resource
                    measured_resource = MeasuredResource(
                        host.resourceId,
                        restype.resourceTypeId,
                        is_currently_measured=True
                    )
                    measurement_job.measuredResources.append(measured_resource)

                    # Add collected measurement
                    collected_measurement = CollectedMeasurement(
                        f"{job.performanceMeasurementJobId}_{host.resourceId}",
                        restype.resourceTypeId,
                        job.performanceMeasurementJobId,
                        [],  # timeAdded
                        is_currently_measured=True
                    )
                    measurement_job.collectedMeasurements.append(
                        collected_measurement)

            uow.measurement_jobs.add(measurement_job)
            logger.info(f"Added measurement job: "
                        f"{job.performanceMeasurementJobId}")

        else:
            # Update existing job
            if is_job_changed(measurement_job, job):
                logger.info(f"Updating measurement job: "
                            f"{job.performanceMeasurementJobId}")
                update_measurement_job(measurement_job, job)
                uow.measurement_jobs.update(measurement_job)

        uow.commit()


def is_job_changed(current_job: MeasurementJob,
                   new_job: MeasurementJob) -> bool:
    """Check if measurement job needs updating."""
    return (current_job.state != new_job.state or
            current_job.status != new_job.status or
            current_job.collectionInterval != new_job.collectionInterval)


def create_measurement_job(job: MeasurementJob) -> MeasurementJob:
    """Create new measurement job."""
    return MeasurementJob(
        job_id=job.performanceMeasurementJobId,
        consumer_job_id=job.consumerPerformanceJobId,
        state=job.state or MeasurementJobState.ACTIVE,
        collection_interval=job.collectionInterval,
        measurement_criteria=job.measurementSelectionCriteria,
        status=job.status or MeasurementJobStatus.RUNNING,
        preinstalled_job=job.preinstalledJob,
        resource_criteria=job.resourceScopeCriteria
    )


def update_measurement_job(target: MeasurementJob,
                           source: MeasurementJob) -> None:
    """Update existing measurement job with new data."""
    target.state = source.state
    target.status = source.status
    target.collectionInterval = source.collectionInterval
    target.measurementSelectionCriteria = source.measurementSelectionCriteria
    target.resourceScopeCriteria = source.resourceScopeCriteria

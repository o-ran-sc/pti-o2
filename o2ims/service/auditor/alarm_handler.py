# Copyright (C) 2022 Wind River Systems, Inc.
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

# from o2common.config import config
# from o2common.service.messagebus import MessageBus
from o2common.service.unit_of_work import AbstractUnitOfWork
from o2ims.domain import events, commands, alarm_obj, ocloud
from o2ims.domain.alarm_obj import AlarmEventRecord, FaultGenericModel,\
    AlarmNotificationEventEnum

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


def update_alarm(
    cmd: commands.UpdateAlarm,
    uow: AbstractUnitOfWork
):
    fmobj = cmd.data
    logger.info("add alarm event record:" + fmobj.name
                + " update_at: " + str(fmobj.updatetime)
                + " id: " + str(fmobj.id)
                + " hash: " + str(fmobj.hash))
    with uow:
        resourcepool = uow.resource_pools.get(cmd.parentid)

        alarm_event_record = uow.alarm_event_records.get(fmobj.id)
        if not alarm_event_record:
            logger.info("add alarm event record:" + fmobj.name
                        + " update_at: " + str(fmobj.updatetime)
                        + " id: " + str(fmobj.id)
                        + " hash: " + str(fmobj.hash))
            localmodel = create_by(fmobj)
            content = json.loads(fmobj.content)
            entity_type_id = content['entity_type_id']
            entity_instance_id = content['entity_instance_id']
            logger.info('alarm entity instance id: ' + entity_instance_id)
            if 'host' == entity_type_id:
                # TODO: handle different resource type
                hostname = entity_instance_id.split('.')[0].split('=')[1]
                logger.debug('hostname: ' + hostname)

                restype = uow.resource_types.get_by_name('pserver')
                localmodel.resourceTypeId = restype.resourceTypeId
                args = [ocloud.Resource.resourceTypeId ==
                        restype.resourceTypeId]
                hosts = uow.resources.list(resourcepool.resourcePoolId, *args)
                for host in hosts:
                    logger.debug('host extensions: ' + host.extensions)
                    extensions = json.loads(host.extensions)
                    if extensions['hostname'] == hostname:
                        localmodel.resourceId = host.resourceId
                uow.alarm_event_records.add(localmodel)
                logger.info("Add the alarm event record: " + fmobj.id
                            + ", name: " + fmobj.name)
            else:
                restype = uow.resource_types.get_by_name('undefined_aggregate')
                localmodel.resourceTypeId = restype.resourceTypeId

                args = [ocloud.Resource.resourceTypeId ==
                        restype.resourceTypeId]
                undefined_res = uow.resources.list(
                    resourcepool.resourcePoolId, *args)
                localmodel.resourceId = undefined_res[0].resourceId
                uow.alarm_event_records.add(localmodel)
                logger.info("Add the alarm event record: " + fmobj.id
                            + ", name: " + fmobj.name)

        else:
            localmodel = alarm_event_record
            if is_outdated(localmodel, fmobj):
                logger.info("update alarm event record:" + fmobj.name
                            + " update_at: " + str(fmobj.updatetime)
                            + " id: " + str(fmobj.id)
                            + " hash: " + str(fmobj.hash))
                update_by(localmodel, fmobj)
                uow.alarm_event_records.update(localmodel)

            logger.info("Update the alarm event record: " + fmobj.id
                        + ", name: " + fmobj.name)
        uow.commit()


def is_outdated(alarm_event_record: AlarmEventRecord,
                fmobj: FaultGenericModel):
    return True if alarm_event_record.hash != fmobj.hash else False


def create_by(fmobj: FaultGenericModel) -> AlarmEventRecord:
    content = json.loads(fmobj.content)
    # globalcloudId = fmobj.id  # to be updated
    alarm_definition_id = fmobj.alarm_def_id
    alarm_event_record = AlarmEventRecord(
        fmobj.id, "", "",
        alarm_definition_id, "",
        fmobj.timestamp)

    def severity_switch(val):
        if val == 'critical':
            return alarm_obj.PerceivedSeverityEnum.CRITICAL
        elif val == 'major':
            return alarm_obj.PerceivedSeverityEnum.MAJOR
        elif val == 'minor':
            return alarm_obj.PerceivedSeverityEnum.MINOR
        else:
            return alarm_obj.PerceivedSeverityEnum.WARNING
    alarm_event_record.perceivedSeverity = severity_switch(content['severity'])
    alarm_event_record.probableCauseId = fmobj.probable_cause_id
    alarm_event_record.hash = fmobj.hash
    # logger.info('severity: ' + content['severity'])
    # logger.info('perceived severity: '
    # + alarm_event_record.perceivedSeverity)
    alarm_event_record.events.append(events.AlarmEventChanged(
        id=fmobj.id,
        notificationEventType=AlarmNotificationEventEnum.NEW,
        updatetime=fmobj.updatetime
    ))

    return alarm_event_record


def update_by(target: AlarmEventRecord, fmobj: FaultGenericModel
              ) -> None:
    # content = json.loads(fmobj.content)
    if fmobj.status == 'clear':
        target.perceivedSeverity = alarm_obj.PerceivedSeverityEnum.CLEARED

    target.hash = fmobj.hash
    target.events.append(events.AlarmEventChanged(
        id=fmobj.id,
        notificationEventType=AlarmNotificationEventEnum.CLEAR,
        updatetime=fmobj.updatetime
    ))


def check_restype_id(uow: AbstractUnitOfWork, fmobj: FaultGenericModel) -> str:
    content = json.loads(fmobj.content)
    entity_type_id = content['entity_type_id']
    # Entity_Instance_ID: <hostname>.lvmthinpool=<VG name>/<Pool name>
    # Entity_Instance_ID: ["image=<image-uuid>, instance=<instance-uuid>",
    # Entity_Instance_ID: [host=<hostname>.command=provision,
    # Entity_Instance_ID: [host=<hostname>.event=discovered,
    # Entity_Instance_ID: [host=<hostname>.state=disabled,
    # Entity_Instance_ID: [subcloud=<subcloud>.resource=<compute | network
    # | platform | volumev2>]
    # Entity_Instance_ID: cinder_io_monitor
    # Entity_Instance_ID: cluster=<dist-fs-uuid>
    # Entity_Instance_ID: cluster=<dist-fs-uuid>.peergroup=<group-x>
    # Entity_Instance_ID: fs_name=<image-conversion>
    # Entity_Instance_ID: host=<host_name>
    # Entity_Instance_ID: host=<host_name>.network=<network>
    # Entity_Instance_ID: host=<host_name>.services=compute
    # Entity_Instance_ID: host=<hostname>
    # Entity_Instance_ID: host=<hostname>,agent=<agent-uuid>,
    # bgp-peer=<bgp-peer>
    # Entity_Instance_ID: host=<hostname>.agent=<agent-uuid>
    # Entity_Instance_ID: host=<hostname>.interface=<if-name>
    # Entity_Instance_ID: host=<hostname>.interface=<if-uuid>
    # Entity_Instance_ID: host=<hostname>.ml2driver=<driver>
    # Entity_Instance_ID: host=<hostname>.network=<mgmt | oam | cluster-host>
    # Entity_Instance_ID: host=<hostname>.openflow-controller=<uri>
    # Entity_Instance_ID: host=<hostname>.openflow-network=<name>
    # Entity_Instance_ID: host=<hostname>.port=<port-name>
    # Entity_Instance_ID: host=<hostname>.port=<port-uuid>
    # Entity_Instance_ID: host=<hostname>.process=<processname>
    # Entity_Instance_ID: host=<hostname>.processor=<processor>
    # Entity_Instance_ID: host=<hostname>.sdn-controller=<uuid>
    # Entity_Instance_ID: host=<hostname>.sensor=<sensorname>
    # Entity_Instance_ID: host=<hostname>.service=<service>
    # Entity_Instance_ID: host=<hostname>.service=networking.providernet=
    # <pnet-uuid>
    # Entity_Instance_ID: host=controller
    # Entity_Instance_ID: itenant=<tenant-uuid>.instance=<instance-uuid>
    # Entity_Instance_ID: k8s_application=<appname>
    # Entity_Instance_ID: kubernetes=PV-migration-failed
    # Entity_Instance_ID: orchestration=fw-update
    # Entity_Instance_ID: orchestration=kube-rootca-update
    # Entity_Instance_ID: orchestration=kube-upgrade
    # Entity_Instance_ID: orchestration=sw-patch
    # Entity_Instance_ID: orchestration=sw-upgrade
    # Entity_Instance_ID: resource=<crd-resource>,name=<resource-name>
    # Entity_Instance_ID: server-group<server-group-uuid>
    # Entity_Instance_ID: service=networking.providernet=<pnet-uuid>
    # Entity_Instance_ID: service_domain=<domain>.service_group=<group>
    # Entity_Instance_ID: service_domain=<domain>.service_group=<group>.
    # host=<host_name>
    # Entity_Instance_ID: service_domain=<domain_name>.service_group=
    # <group_name>
    # Entity_Instance_ID: service_domain=<domain_name>.service_group=
    # <group_name>.host=<hostname>
    # Entity_Instance_ID: storage_backend=<storage-backend-name>
    # Entity_Instance_ID: subcloud=<subcloud>
    # Entity_Instance_ID: subsystem=vim
    # Entity_Instance_ID: tenant=<tenant-uuid>.instance=<instance-uuid>
    if 'host' == entity_type_id:
        with uow:
            restype = uow.resource_types.get_by_name('pserver')
            return restype.resourceTypeId
    else:
        return ""


def check_res_id(uow: AbstractUnitOfWork, fmobj: FaultGenericModel) -> str:
    content = json.loads(fmobj.content)
    entity_type_id = content['entity_type_id']
    entity_instance_id = content['entity_instance_id']
    if 'host' == entity_type_id:
        logger.info('host: ' + entity_instance_id)
        hostname = entity_instance_id.split('.')[0].split('=')[1]
        with uow:
            respools = uow.resource_pools.list()
            respoolids = [respool.resourcePoolId for respool in respools
                          if respool.oCloudId == respool.resourcePoolId]
            restype = uow.resource_types.get_by_name('pserver')
            hosts = uow.resources.list(respoolids[0], **{
                'resourceTypeId': restype.resourceTypeId
            })
            for host in hosts:
                if host.name == hostname:
                    return host.resourceId
    else:
        return ""

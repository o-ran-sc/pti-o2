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

import os
import json
import yaml
import errno
import collections
import uuid as uuid_gen

from o2common.service import unit_of_work
from o2common.config import config
from o2ims.domain import alarm_obj as alarm

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


def load_alarm_dictionary_from_conf_file(uow: unit_of_work.AbstractUnitOfWork):
    conf_path = config.get_alarm_yaml_filename()
    logger.info(f"Converting alarm.yaml to dictionary: {conf_path}")

    if not os.path.isfile(conf_path):
        logger.error("file %s doesn't exist. Ending execution" %
                     (conf_path))
        raise OSError(
            errno.ENOENT, os.strerror(errno.ENOENT), conf_path
        )

    try:
        with open(conf_path, 'r') as stream:
            alarm_yaml = yaml.load(stream, Loader=yaml.FullLoader)
        dictionaries = alarm_yaml.get('alarmDictionary')['schema']
        schema_ver = alarm_yaml.get('alarmDictionary')['schemaVersion']
    except Exception as exp:
        logger.error(exp)
        raise RuntimeError(exp)

    for dictionary in list(dictionaries.keys()):
        # res_type = uow.resource_types.get_by_name(dictionary)
        # logger.info('res_type: ' + res_type.resourceTypeName)
        version = dictionaries[dictionary]['version']
        definitions = dictionaries[dictionary]['alarmDefinition']
        dict_id = str(uuid_gen.uuid3(
            uuid_gen.NAMESPACE_URL,
            str(f"{dictionary}_alarmdictionary")))

        with uow:
            alarm_dict = uow.alarm_dictionaries.get(dict_id)
            if alarm_dict:
                alarm_dict.alarmDictionaryVersion = version
                alarm_dict.alarmDictionarySchemaVersion = schema_ver
            else:
                alarm_dict = alarm.AlarmDictionary(dict_id)
                alarm_dict.entityType = dictionary
                alarm_dict.alarmDictionaryVersion = version
                alarm_dict.alarmDictionarySchemaVersion = schema_ver

            definition_list = list()
            if definitions:
                for definition in definitions:
                    def_uuid = str(uuid_gen.uuid3(
                        uuid_gen.NAMESPACE_URL, str(definition)))
                    def_obj = uow.alarm_definitions.get(def_uuid)
                    definition_list.append(def_obj)
            alarm_dict.alarmDefinition = definition_list
            uow.alarm_dictionaries.add(alarm_dict)
            uow.commit()
        # conf.alarm_dictionaries.add(alarm_dict)


def prettyDict(dict):
    output = json.dumps(dict, sort_keys=True, indent=4)
    return output


def load_alarm_definition(uow: unit_of_work.AbstractUnitOfWork):
    EVENT_TYPES_FILE = config.get_events_yaml_filename()
    logger.info(f"Converting events.yaml to dict: {EVENT_TYPES_FILE}")

    if not os.path.isfile(EVENT_TYPES_FILE):
        logger.error("file %s doesn't exist. Ending execution" %
                     (EVENT_TYPES_FILE))
        raise OSError(
            errno.ENOENT, os.strerror(errno.ENOENT), EVENT_TYPES_FILE
        )

    try:
        with open(EVENT_TYPES_FILE, 'r') as stream:
            event_types = yaml.load(stream, Loader=yaml.FullLoader)
    except Exception as exp:
        logger.error(exp)
        raise RuntimeError(exp)

    for alarm_id in list(event_types.keys()):
        if isinstance(alarm_id, float):
            # force 3 digits after the decimal point,
            # to include trailing zero's (ex.: 200.010)
            formatted_alarm_id = "{:.3f}".format(alarm_id)
            event_types[formatted_alarm_id] = event_types.pop(alarm_id)

    event_types = collections.OrderedDict(sorted(event_types.items()))

    yaml_event_list = []
    uneditable_descriptions = {'100.114', '200.007',
                               '200.02', '200.021', '200.022', '800.002'}

    # Parse events.yaml dict, and add any new alarm to definition table:
    logger.info(
        "Parsing events.yaml and adding any new alarm to definition table.")
    for event_type in event_types:

        if event_types.get(event_type).get('Type') == "Alarm":
            event_uuid = str(uuid_gen.uuid3(
                uuid_gen.NAMESPACE_URL, str(event_type)))

            string_event_type = str(event_type)

            yaml_event_list.append(string_event_type)

            if str(event_type) not in uneditable_descriptions:
                event_description = (event_types.get(event_type)
                                     .get('Description'))
            else:
                event_description = event_types.get(
                    event_type).get('Description')

            event_description = str(event_description)
            event_description = (event_description[:250] + ' ...') \
                if len(event_description) > 250 else event_description
            prop_action = event_types.get(
                event_type).get("Proposed_Repair_Action")

            with uow:
                alarm_def = uow.alarm_definitions.get(event_uuid)
                event_mgmt_affecting = str(event_types.get(event_type).get(
                    'Management_Affecting_Severity', 'warning'))
#
                event_degrade_affecting = str(event_types.get(event_type).get(
                    'Degrade_Affecting_Severity', 'none'))

                if alarm_def:
                    alarm_def.description = event_description
                    alarm_def.mgmt_affecting = event_mgmt_affecting
                    alarm_def.degrade_affecting = event_degrade_affecting
                else:
                    alarm_def = alarm.AlarmDefinition(
                        id=event_uuid,
                        name=str(event_type),
                        change_type=alarm.AlarmChangeTypeEnum.ADDED,
                        desc=event_description, prop_action=prop_action,
                        clearing_type=alarm.ClearingTypeEnum.MANUAL,
                        pk_noti_field=""
                    )
                    # logger.debug(str(event_type))
                    uow.alarm_definitions.add(alarm_def)

                uow.commit()

            prob_cause = event_types.get(event_type).get("Probable_Cause")
            prob_cause_uuid = str(uuid_gen.uuid3(
                uuid_gen.NAMESPACE_URL, prob_cause))

            with uow:
                probable_cause = uow.alarm_probable_causes.get(prob_cause_uuid)
                if probable_cause is None:
                    pc = alarm.ProbableCause(
                        prob_cause_uuid, prob_cause, prob_cause)
                    uow.alarm_probable_causes.add(pc)
                    uow.commit()

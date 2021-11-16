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

import logging
import logging.config
import logging.handlers
import os
import yaml


def get_logger(name=None):
    CONFIG_FILE = os.environ.get(
        "LOGGING_CONFIG_FILE", "/etc/o2/log.yaml")
    if os.path.exists(CONFIG_FILE):
        with open(file=CONFIG_FILE, mode='r', encoding="utf-8") as file:
            config_yaml = yaml.load(stream=file, Loader=yaml.FullLoader)
        logging.config.dictConfig(config=config_yaml)

    logger = logging.getLogger(name)

    # override logging level
    LOGGING_CONFIG_LEVEL = os.environ.get("LOGGING_CONFIG_LEVEL", None)
    if LOGGING_CONFIG_LEVEL:
        logger.setLevel(LOGGING_CONFIG_LEVEL)
    return logger

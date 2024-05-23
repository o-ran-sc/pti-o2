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
import configparser


class Error(Exception):
    """Base class for cfg exceptions."""

    def __init__(self, msg=None):
        self.msg = msg

    def __str__(self):
        return self.msg


class NoSuchOptError(Error, AttributeError):
    """Raised if an opt which doesn't exist is referenced."""

    def __init__(self, opt_name, group=None):
        self.opt_name = opt_name
        self.group = group

    def __str__(self):
        group_name = 'DEFAULT' if self.group is None else self.group.name
        return "no such option %s in group [%s]" % (self.opt_name, group_name)


class NoSuchConfigFile(Error):
    """Raised if the config file does not exist."""

    def __init__(self, file_path):
        self.file_path = file_path

    def __str__(self):
        return "no such file %s exist" % self.file_path


class Section:
    def __init__(self, section: str) -> None:
        self.group_name = section
        self._options = {}

    def _set(self, name, value):
        opt = getattr(self, name)
        if opt is None:
            setattr(self, name, value)
        if name not in self._options:
            self._options[name] = value

    def _get(self, name):
        name = name.lower()
        if name in self._options:
            return self._options[name]

    def __getattr__(self, name):
        try:
            return self._get(name)
        except ValueError:
            raise
        except Exception:
            raise NoSuchOptError(name, self.group_name)


class Config:
    def __init__(self) -> None:
        self.__cache = {'b': 456}
        self._sections = {}

    def _set(self, section, name='', value=''):
        group = getattr(self, section)
        if group is None:
            group = Section(section)
            setattr(self, section, group)
        if section not in self._sections:
            self._sections[section] = group
        if name != '':
            setattr(group, name, value)
        return group

    def _get(self, name):
        if name in self._sections:
            return self._sections[name]

        if name in self.__cache:
            return self.__cache[name]

    def __getattr__(self, name):
        try:
            return self._get(name)
        except ValueError:
            raise
        except Exception:
            raise NoSuchOptError(name)

    def load(self, file_path):
        if not os.path.exists(file_path):
            raise NoSuchConfigFile(file_path)
        conf = configparser.ConfigParser()
        conf.read(file_path)
        default_group = self._set('DEFAULT')
        for option in conf['DEFAULT']:
            default_group._set(option, conf['DEFAULT'][option])
        for section in conf.sections():
            group = self._set(section)
            for option in conf[section]:
                group._set(option, conf[section][option])


if __name__ == "__main__":
    conf = Config()
    # conf._set('default', 'a', 123)

    # print(conf.default.a)
    # print(conf.b)

    # conf = configparser.ConfigParser()
    # conf.read('configs/o2app.conf')
    # print(conf)
    # print(conf['DEFAULT'].__dict__)
    # print(conf['DEFAULT']['test'])
    conf.load('configs/o2app.conf')
    print(conf.API.test)
    print(conf.DEFAULT.test)
    print(conf.PUBSUB.ooo)
    print(conf.DEFAULT.oCloudGlobalID)

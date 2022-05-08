from enum import Enum


class ResourceTypeEnum(Enum):
    OCLOUD = 1
    RESOURCE_POOL = 2
    DMS = 3
    PSERVER = 11
    PSERVER_CPU = 12
    PSERVER_RAM = 13
    PSERVER_IF = 14
    PSERVER_IF_PORT = 15
    PSERVER_ETH = 16


class InvalidOcloudState(Exception):
    pass


class MismatchedModel(Exception):
    pass

# pylint: disable=too-few-public-methods
import abc
from o2common.config import config


SMO_O2_ENDPOINT = config.get_smo_o2endpoint()


class AbstractNotifications(abc.ABC):
    @abc.abstractmethod
    def send(self, message):
        raise NotImplementedError


class SmoO2Notifications(AbstractNotifications):
    def __init__(self, smoO2Endpoint=SMO_O2_ENDPOINT):
        self.smoO2Endpoint = smoO2Endpoint

    def send(self, message):
        pass

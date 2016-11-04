import collections

from .gui import NotificationWindow
from . import settings


class Notification(object):
    __notifications = collections.OrderedDict()
    __window = NotificationWindow()

    def __init__(self, summary, body, replaces_id, urgency):
        self.summary = summary
        self.body = body
        self.urgency = urgency
        self.message_id = replaces_id or self._get_next_message_id()

        self.__notifications.pop(self.message_id, None)
        self.__notifications[self.message_id] = self

    def show(self):
        self.__window.popup(self.summary, self.body, self.urgency)

    def close(self):
        self.__window.remove()

    @classmethod
    def get_by_id(cls, message_id):
        return cls.__notifications.get(message_id)

    @classmethod
    def _get_next_message_id(cls):
        ids = list(cls.__notifications.keys())
        if not ids:
            return 1
        else:
            if len(ids) > settings.HISTORY_SIZE:
                del cls.__notifications[ids[0]]
            return ids[-1] + 1

    def __str__(self):
        return "{} - {}".format(self.summary, self.body)

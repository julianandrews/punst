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

    def show(self, expire_timeout):
        self.__window.add_notification(self, expire_timeout)

    def close(self):
        self.__window.remove_notification(self)

    @classmethod
    def get_by_id(cls, message_id):
        return cls.__notifications.get(message_id)

    @classmethod
    def _get_next_message_id(cls):
        ids = list(cls.__notifications.keys())
        if not ids:
            return 1
        else:
            if len(ids) > settings.HISTORY_LENGTH:
                del cls.__notifications[ids[0]]
            return ids[-1] + 1

    def __str__(self):
        return "{} - {}".format(self.summary, self.body)

    def __repr__(self):
        return "Notification({})".format(self.summary)

    def __eq__(self, other):
        return self.message_id == other.message_id

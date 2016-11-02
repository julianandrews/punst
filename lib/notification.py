import collections


class Notification(object):
    HISTORY_SIZE = 20

    __notifications = collections.OrderedDict()

    def __init__(self, summary, body, replaces_id):
        self.summary = summary
        self.body = body
        self.message_id = replaces_id or self._get_next_message_id()

        self.__notifications.pop(self.message_id, None)
        self.__notifications[self.message_id] = self

    def show(self):
        print("{}: {}".format(self.message_id, self))

    def close(self):
        pass

    @classmethod
    def get_by_id(cls, message_id):
        return cls.__notifications.get(message_id)

    @classmethod
    def _get_next_message_id(cls):
        ids = list(cls.__notifications.keys())
        if not ids:
            return 1
        else:
            if len(ids) > cls.HISTORY_SIZE:
                del cls.__notifications[ids[0]]
            return ids[-1] + 1

    def __str__(self):
        return "{} - {}".format(self.summary, self.body)

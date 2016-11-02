import collections
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject


class NotificationWindow(Gtk.Window):
    DEFAULT_TIMEOUT = 3000
    MONITOR_NUMBER = 0

    def __init__(self, timeout=DEFAULT_TIMEOUT):
        super(NotificationWindow, self).__init__(type=Gtk.WindowType.POPUP)
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_accept_focus(False)
        self.draw()
        self.position()
        self.connect('button-release-event', self.remove)
        self.timeout = GObject.timeout_add(timeout, self.remove, None)

    def draw(self):
        self.width, self.height = (250, 100)

    def position(self):
        screen = Gdk.Screen.get_default()
        monitor_rect = screen.get_monitor_geometry(self.MONITOR_NUMBER)
        self.set_size_request(self.width, self.height)
        self.move(
            monitor_rect.x + monitor_rect.width - self.width - 50,
            monitor_rect.y + 50
        )

    def remove(self, event, data=None):
        self.destroy()


class Notification(object):
    HISTORY_SIZE = 20

    __notifications = collections.OrderedDict()

    def __init__(self, summary, body, replaces_id, urgency):
        self.summary = summary
        self.body = body
        self.urgency = urgency
        self.message_id = replaces_id or self._get_next_message_id()
        self.window = None

        self.__notifications.pop(self.message_id, None)
        self.__notifications[self.message_id] = self

    def show(self):
        print("{} - {}: {}".format(self.message_id, self.urgency, self))
        if not self.window:
            self.window = NotificationWindow()
        self.window.show()

    def close(self):
        if self.window:
            self.window.remove()
            self.window = None


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

import dbus
import dbus.service
import enum

from .gui import NotificationWindow
from .keybindings import KeybindingManager
from .notification import Notification
from . import settings


SPEC_VERSION = '1.2'


class NotificationClosedReason(enum.IntEnum):
    EXPIRED = 1
    DISMISSED = 2
    CLOSED = 3
    UNDEFINED = 4


class NotificationServer(dbus.service.Object):
    IFACE = 'org.freedesktop.Notifications'
    OPATH = '/org/freedesktop/Notifications'
    BUS_NAME = IFACE

    def __init__(self):
        bus = dbus.SessionBus()
        bus.request_name(self.BUS_NAME)
        bus_name = dbus.service.BusName(self.BUS_NAME, bus=bus)
        dbus.service.Object.__init__(self, bus_name, self.OPATH)
        self.window = NotificationWindow()
        self.keybindings = KeybindingManager()
        self.keybindings.add_keybinding(
            settings.SHORTCUT_CLOSE, self.window.close_last
        )
        self.keybindings.add_keybinding(
            settings.SHORTCUT_CLOSE_ALL, self.window.close_all
        )
        self.keybindings.add_keybinding(
            settings.SHORTCUT_HISTORY, self.window.history
        )
        self.keybindings.start()
        if settings.STARTUP_NOTIFICATION:
            notification = Notification(
                settings.APP_NAME, "startup", "punst is up and running", "", 0,
                settings.NotificationUrgency.LOW,
            )
            self.window.add_notification(notification, 0)

    @dbus.service.method(dbus_interface=IFACE, in_signature='i',
                         out_signature='')
    def CloseNotification(self, message_id):
        notification = Notification.get_by_id(int(message_id))
        if notification:
            self.window.remove_notification(notification)
            self.NotificationClosed(message_id, NotificationClosedReason.CLOSED)
        else:
            raise dbus.DBusException

    @dbus.service.method(dbus_interface=IFACE, in_signature=None,
                         out_signature='as')
    def GetCapabilities(self, *args, **kwargs):
        return ['body']

    @dbus.service.method(dbus_interface=IFACE, in_signature=None,
                         out_signature='ssss')
    def GetServerInformation(self):
        return [
            settings.APP_NAME, settings.VENDOR, settings.VERSION, SPEC_VERSION
        ]

    @dbus.service.method(dbus_interface=IFACE, in_signature='susssasa{sv}i',
                         out_signature='u')
    def Notify(self, app_name, replaces_id, icon, summary, body,
               actions, hints, expire_timeout):
        urgency = settings.NotificationUrgency(hints.get('urgency', 1))
        notification = Notification(
            str(app_name), str(summary), str(body), str(icon),
            int(replaces_id), urgency,
        )
        self.window.add_notification(notification, int(expire_timeout))
        return notification.message_id

    @dbus.service.signal(dbus_interface=IFACE, signature='uu')
    def NotificationClosed(self, message_id, reason):
        pass

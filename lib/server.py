import dbus
import dbus.service
import enum

from . import Notification

__version__ = '0.1'

APP_NAME = 'punst'
VENDOR = ''
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

    @dbus.service.method(dbus_interface=IFACE, in_signature='i',
                         out_signature='')
    def CloseNotification(self, message_id):
        notification = Notification.get_by_id(int(message_id))
        if notification:
            notification.close()
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
        return [APP_NAME, VENDOR, __version__, SPEC_VERSION]

    @dbus.service.method(dbus_interface=IFACE, in_signature='susssasa{sv}i',
                         out_signature='u')
    def Notify(self, app_name, replaces_id, app_icon, summary, body,
               actions, hints, expire_timeout):
        notification = Notification(str(summary), str(body), int(replaces_id))
        notification.show()
        return notification.message_id

    @dbus.service.signal(dbus_interface=IFACE, signature='uu')
    def NotificationClosed(self, message_id, reason):
        pass

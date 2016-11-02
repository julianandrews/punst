import signal

from gi.repository import GObject
from dbus.mainloop.glib import DBusGMainLoop

from lib import NotificationServer


if __name__ == '__main__':
    DBusGMainLoop(set_as_default=True)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    server = NotificationServer()
    mainloop = GObject.MainLoop()
    mainloop.run()

import gi
import signal
gi.require_version('Gtk', '3.0')  # noqa
from gi.repository import Gtk
from dbus.mainloop.glib import DBusGMainLoop

from lib.dbus_server import NotificationServer

if __name__ == '__main__':
    DBusGMainLoop(set_as_default=True)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    NotificationServer()
    Gtk.main()

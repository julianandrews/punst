import gi
gi.require_version('Gtk', '3.0')  # noqa
from gi.repository import Gdk, Gtk, GLib
import threading
from Xlib import display, error, X


class KeybindingManager(threading.Thread):
    def __init__(self):
        super(KeybindingManager, self).__init__()
        self.setDaemon(True)
        self.keybindings = {}
        self.display = display.Display()

    def add_keybinding(self, accelerator, callback):
        keyval, modifiers = Gtk.accelerator_parse(accelerator)
        keymap = Gdk.Keymap.get_default()
        keycode = keymap.get_entries_for_keyval(keyval)[1][0].keycode

        for m in (modifiers, modifiers | X.LockMask):
            self.display.screen().root.grab_key(
                keycode, m, True, X.GrabModeAsync, X.GrabModeSync,
                onerror=error.CatchError(error.BadAccess),
            )
        self.display.sync()
        self.keybindings[(keycode, modifiers)] = callback

    def run(self):
        while True:
            event = self.display.next_event()
            if event.type in {X.KeyPress, X.KeyRelease}:
                if event.type == X.KeyRelease:
                    callback = self.keybindings[(event.detail, event.state)]
                    GLib.idle_add(callback)
                self.display.allow_events(X.AsyncKeyboard, event.time)
            else:
                self.display.allow_events(X.ReplayKeyboard, event.time)

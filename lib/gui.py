import gi
gi.require_version('Gtk', '3.0')
gi.require_version('PangoCairo', '1.0')
from gi.repository import Gtk, Gdk, GObject, cairo, Pango, PangoCairo

from . import settings
from .utils import hex_to_rgb, NotificationUrgency


class NotificationDrawingArea(Gtk.DrawingArea):
    def __init__(self, *args, **kwargs):
        super(NotificationDrawingArea, self).__init__(*args, **kwargs)
        self.text = ""
        self.connect('draw', self.draw)
        self.urgency = NotificationUrgency.NORMAL

    def draw(self, widget, cr):
        width = cr.get_target().get_width()
        height = cr.get_target().get_height()
        bg_color = hex_to_rgb(settings.BG_COLORS[self.urgency])
        cr.set_source_rgb(*bg_color)
        cr.rectangle(0, 0, width, height)
        cr.fill()
        layout = PangoCairo.create_layout(cr)
        desc = Pango.FontDescription(settings.FONT)
        layout.set_font_description(desc)
        layout.set_width(
            (settings.WINDOW_WIDTH - 2 * settings.PADDING[0]) * Pango.SCALE
        )
        layout.set_alignment(Pango.Alignment.LEFT)
        layout.set_wrap(Pango.WrapMode.WORD_CHAR)
        layout.set_markup(self.text, -1)
        height = layout.get_pixel_size()[1]
        self.get_parent_window().resize(
            settings.WINDOW_WIDTH, height + 2 * settings.PADDING[1]
        )

        fg_color = hex_to_rgb(settings.FG_COLORS[self.urgency])
        cr.translate(*settings.PADDING)
        cr.set_source_rgb(*fg_color)
        PangoCairo.update_layout(cr, layout)
        PangoCairo.show_layout(cr, layout)


class NotificationWindow(Gtk.Window):
    def __init__(self):
        super(NotificationWindow, self).__init__(type=Gtk.WindowType.POPUP)
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_accept_focus(False)
        self.timeout = None
        self.drawing_area = NotificationDrawingArea()
        self.drawing_area.show()
        self.add(self.drawing_area)
        self.set_size_request(settings.WINDOW_WIDTH, 200)
        self.connect('button-release-event', self.on_click)

    def draw(self, summary, body, urgency):
        self.drawing_area.text = "<b>{}</b>\n{}".format(summary, body)
        self.drawing_area.urgency = urgency
        self.drawing_area.queue_draw()
        screen = Gdk.Screen.get_default()
        monitor_rect = screen.get_monitor_geometry(settings.MONITOR_NUMBER)
        self.move(
            monitor_rect.x + monitor_rect.width - settings.WINDOW_WIDTH - 50,
            monitor_rect.y + 50
        )

    def popup(self, summary, body, urgency):
        self.draw(summary, body, urgency)
        self.show()
        if self.timeout:
            GObject.source_remove(self.timeout)
        timeout = settings.TIMEOUTS[urgency]
        if timeout is not None:
            self.timeout = GObject.timeout_add(timeout, self.remove)

    def remove(self):
        self.hide()
        if self.timeout:
            GObject.source_remove(self.timeout)
            self.timeout = None

    def on_click(self, event, data=None):
        self.remove()

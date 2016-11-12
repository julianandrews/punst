import collections
import gi
gi.require_version('Gtk', '3.0')  # noqa
gi.require_version('PangoCairo', '1.0')  # noqa
from gi.repository import Gdk, GObject, Gtk, Pango, PangoCairo

from . import settings
from .utils import format_text, NotificationUrgency


class NotificationDrawingArea(Gtk.DrawingArea):
    def __init__(self, summary, body, urgency, width):
        super(NotificationDrawingArea, self).__init__()
        self.set_text(summary, body)
        self.urgency = urgency
        self.width = width
        self.height = 0
        self.connect('draw', self.draw)

    def set_text(self, summary, body):
        text = format_text(settings.FORMAT, summary, body)
        use_plain_text = settings.PLAIN_TEXT
        if not settings.PLAIN_TEXT:
            # Default to using plain text if the markup can't be parsed
            try:
                parsed = Pango.parse_markup(text, -1, u'\x00')
            except GObject.GError:
                use_plain_text = True

        if not settings.ALLOW_MARKUP and not use_plain_text:
            self.text = parsed.text
        else:
            if settings.ALLOW_MARKUP and use_plain_text:
                summary = GObject.markup_escape_text(summary)
                body = GObject.markup_escape_text(body)
            self.text = format_text(settings.FORMAT, summary, body)

    def build_layout(self, cr):
        # FIXME: respect settings.HEIGHT
        layout = PangoCairo.create_layout(cr)
        if settings.ALLOW_MARKUP:
            layout.set_markup(self.text, -1)
        else:
            layout.set_text(self.text, -1)
        desc = Pango.FontDescription(settings.FONT)
        layout.set_font_description(desc)
        layout.set_width(Pango.SCALE * (
            self.width - 2 * (settings.PADDING[0] + settings.FRAME_WIDTH)
        ))
        layout.set_alignment(
            getattr(Pango.Alignment, settings.ALIGNMENT.upper())
        )
        layout.set_wrap(Pango.WrapMode.WORD_CHAR)
        return layout

    def draw(self, widget, cr):
        layout = self.build_layout(cr)
        self.height = layout.get_pixel_size()[1] + \
            2 * (settings.PADDING[1] + settings.FRAME_WIDTH)

        bg_color = settings.BG_COLORS[self.urgency]
        fg_color = settings.FG_COLORS[self.urgency]
        if settings.FRAME_COLOR is None:
            frame_color = fg_color
        else:
            frame_color = settings.FRAME_COLOR

        cr.set_source_rgb(*bg_color)
        cr.rectangle(0, 0, self.width, self.height)
        cr.fill()
        cr.set_source_rgb(*frame_color)
        cr.rectangle(0, 0, self.width, self.height)
        cr.set_line_width(2 * settings.FRAME_WIDTH)
        cr.stroke()
        cr.set_source_rgb(*fg_color)
        cr.translate(*settings.PADDING)
        cr.translate(settings.FRAME_WIDTH, settings.FRAME_WIDTH)
        PangoCairo.update_layout(cr, layout)
        PangoCairo.show_layout(cr, layout)

        self.get_parent().get_parent().position()


class NotificationWindow(Gtk.Window):
    def __init__(self):
        super(NotificationWindow, self).__init__(type=Gtk.WindowType.POPUP)

        self.notifications = []
        self.timeouts = {}
        self.set_dimensions()
        self.box = Gtk.VBox()
        self.box.show()
        self.add(self.box)

        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_accept_focus(False)
        self.connect('button-release-event', self.on_click)

    def add_notification(self, notification, expire_timeout):
        self.notifications.append(notification)
        timeout = self.timeouts.get(notification.message_id)
        if timeout:
            GObject.source_remove(timeout)
            del self.timeouts[notification.message_id]
        if expire_timeout == -1:
            expire_timeout = settings.TIMEOUTS[notification.urgency]
        if expire_timeout:
            self.timeouts[notification.message_id] = GObject.timeout_add(
                expire_timeout, lambda: self.remove_notification(notification)
            )
        self.display_notifications()

    def remove_notification(self, notification):
        timeout = self.timeouts.get(notification.message_id)
        if timeout:
            GObject.source_remove(timeout)
            del self.timeouts[notification.message_id]
        if notification in self.notifications:
            self.notifications.remove(notification)
        if self.notifications and self.get_property('visible'):
            self.display_notifications()
        else:
            self.hide()

    def get_notifications_to_draw(self):
        by_urgency = collections.defaultdict(list)
        for notification in self.notifications:
            by_urgency[notification.urgency].append(notification)
        return [
            by_urgency[urgency][-1]
            for urgency in reversed(NotificationUrgency)
            if by_urgency.get(urgency)
        ]

    def display_notifications(self):
        for child in self.box.get_children():
            self.box.remove(child)
        for notification in self.get_notifications_to_draw():
            drawing_area = NotificationDrawingArea(
                notification.summary, notification.body, notification.urgency,
                self.width,
            )
            drawing_area.show()
            self.box.add(drawing_area)
        self.show()
        self.queue_draw()

    def set_dimensions(self):
        screen = Gdk.Screen.get_default()
        monitor_rect = screen.get_monitor_geometry(settings.MONITOR_NUMBER)
        self.width = min(
            (settings.WIDTH - 1) % monitor_rect.width + 1,
            monitor_rect.width - settings.X - settings.FRAME_WIDTH
        )
        if settings.INVERT_X:
            self.x_offset = monitor_rect.width - settings.X
        else:
            self.x_offset = monitor_rect.x + settings.X
        if settings.INVERT_Y:
            self.y_offset = monitor_rect.height - settings.Y
        else:
            self.y_offset = monitor_rect.y + settings.Y

    def position(self):
        height = sum(w.height for w in self.box.get_children())
        width = self.width

        y = self.y_offset - (height if settings.INVERT_Y else 0)
        x = self.x_offset - (width if settings.INVERT_X else 0)

        self.resize(width, height)
        self.move(x, y)

    def clear(self):
        self.notifications = []
        for message_id, timeout in self.timeouts.items():
            GObject.source_remove(timeout)
            del self.timeouts[message_id]

    def on_click(self, event, data=None):
        self.clear()
        self.hide()

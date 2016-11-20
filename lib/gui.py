import cairo
import collections
import datetime
import gi
gi.require_version('Gtk', '3.0')  # noqa
gi.require_version('PangoCairo', '1.0')  # noqa
from gi.repository import Gdk, GObject, Gtk, Pango, PangoCairo
import os.path

from . import settings
from .notification import Notification


def format_age(age):
    units = ((86400, 'day'), (3600, 'hour'), (60, 'min'), (1, 'sec'))
    remainder = age.seconds
    for divisor, name in units:
        value, remainder = divmod(remainder, divisor)
        if value:
            break
    return "{} {}{} ago".format(value, name, '' if value == 1 else 's')


class NotificationDrawingArea(Gtk.DrawingArea):
    def __init__(self, notification, width):
        super(NotificationDrawingArea, self).__init__()
        self.notification = notification
        self.icon = self.get_icon()
        self.width = width
        self.height = 0
        self.connect('draw', self.draw)

    def get_icon_path(self):
        for path in settings.ICON_FOLDERS:
            filename = os.path.join(path, self.notification.icon)
            if os.path.isfile(filename):
                return filename

    def get_icon(self):
        filename = self.get_icon_path()
        if filename:
            return cairo.ImageSurface.create_from_png(filename)

    @property
    def icon_width(self):
        return self.icon.get_width() + settings.PADDING[0] if self.icon else 0

    def build_layout(self, cr):
        layout = PangoCairo.create_layout(cr)
        layout.set_wrap(Pango.WrapMode.WORD_CHAR)
        layout.set_font_description(Pango.FontDescription(settings.FONT))
        layout.set_alignment(getattr(Pango.Alignment, settings.ALIGNMENT.value))

        text = self.notification.formatted_text
        age = datetime.datetime.now() - self.notification.sent_at
        if age > settings.SHOW_AGE_THRESHOLD:
            text += " ({})".format(format_age(age))
        if settings.RENDER_MARKUP:
            layout.set_markup(text, -1)
        else:
            layout.set_text(text, -1)
        layout.set_width(Pango.SCALE * (
            self.width - 2 * (settings.PADDING[0] + settings.FRAME_WIDTH)
            - self.icon_width
        ))
        if settings.HEIGHT or not settings.WORD_WRAP:
            layout.set_ellipsize(Pango.EllipsizeMode.END)
            if not settings.WORD_WRAP:
                layout.set_height(-1)
            elif settings.HEIGHT:
                layout.set_height(
                    settings.HEIGHT * Pango.SCALE -
                    2 * (settings.PADDING[1] + settings.FRAME_WIDTH)
                )

        return layout

    def draw_bg(self, cr):
        cr.set_source_rgb(*settings.BG_COLORS[self.notification.urgency])
        cr.rectangle(0, 0, self.width, self.height)
        cr.fill()
        cr.set_source_rgb(*settings.FRAME_COLOR)
        cr.rectangle(0, 0, self.width, self.height)
        cr.set_line_width(2 * settings.FRAME_WIDTH)
        cr.stroke()

    def draw_icon(self, cr):
        if self.icon:
            if settings.ICON_POSITION == settings.IconPositionType.RIGHT:
                x = self.width - self.icon_width - settings.FRAME_WIDTH
            else:
                x = settings.PADDING[0] + settings.FRAME_WIDTH
            y = settings.PADDING[0] + settings.FRAME_WIDTH
            cr.set_source_surface(self.icon, x, y)
            cr.paint()

    def draw_layout(self, cr, layout):
        cr.translate(*settings.PADDING)
        cr.translate(settings.FRAME_WIDTH, settings.FRAME_WIDTH)
        if settings.ICON_POSITION == settings.IconPositionType.LEFT:
            cr.translate(self.icon_width, 0.0)
        cr.set_source_rgb(*settings.FG_COLORS[self.notification.urgency])
        PangoCairo.update_layout(cr, layout)
        PangoCairo.show_layout(cr, layout)
        cr.identity_matrix()

    def draw(self, widget, cr):
        layout = self.build_layout(cr)
        self.height = layout.get_pixel_size()[1] + \
            2 * (settings.PADDING[1] + settings.FRAME_WIDTH)

        self.draw_bg(cr)
        self.draw_icon(cr)
        self.draw_layout(cr, layout)

        self.get_parent().get_parent().position()
        GObject.timeout_add(500, self.queue_draw)


class NotificationWindow(Gtk.Window):
    def __init__(self):
        super(NotificationWindow, self).__init__(type=Gtk.WindowType.POPUP)

        self.notifications = []
        self.timeouts = {}
        self.history_index = None
        self.history_timeout = None
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
        self.display()

    def remove_notification(self, notification):
        timeout = self.timeouts.get(notification.message_id)
        if timeout:
            GObject.source_remove(timeout)
            del self.timeouts[notification.message_id]
        if notification in self.notifications:
            self.notifications.remove(notification)
        if self.notifications and self.get_property('visible'):
            self.display()
        else:
            self.hide()

    def get_active_notifications(self):
        if self.history_index:
            return [Notification.get_by_index(self.history_index)]
        else:
            by_urgency = collections.defaultdict(list)
            for notification in self.notifications:
                by_urgency[notification.urgency].append(notification)
            return [
                by_urgency[urgency][-1]
                for urgency in reversed(settings.NotificationUrgency)
                if by_urgency.get(urgency)
            ]

    def display(self):
        notifications = self.get_active_notifications()
        self.set_dimensions()
        for child in self.box.get_children():
            self.box.remove(child)
        for notification in notifications:
            drawing_area = NotificationDrawingArea(notification, self.width)
            drawing_area.show()
            self.box.add(drawing_area)
        if notifications:
            self.show()
        else:
            self.hide()
        self.queue_draw()

    def get_selected_monitor(self):
        screen = Gdk.Screen.get_default()
        if settings.FOLLOW == settings.FollowType.MOUSE:
            pointer = screen.get_root_window().get_pointer()
            return screen.get_monitor_at_point(pointer.x, pointer.y)
        elif settings.FOLLOW == settings.FollowType.KEYBOARD:
            return screen.get_monitor_at_window(screen.get_active_window())
        else:
            return settings.MONITOR_NUMBER

    def set_dimensions(self):
        screen = Gdk.Screen.get_default()
        monitor_rect = screen.get_monitor_geometry(self.get_selected_monitor())
        self.width = min(
            (settings.WIDTH - 1) % monitor_rect.width + 1,
            monitor_rect.width - settings.X - settings.FRAME_WIDTH
        )
        if settings.INVERT_X:
            self.x_offset = monitor_rect.x + monitor_rect.width - settings.X
        else:
            self.x_offset = monitor_rect.x + settings.X
        if settings.INVERT_Y:
            self.y_offset = monitor_rect.y + monitor_rect.height - settings.Y
        else:
            self.y_offset = monitor_rect.y + settings.Y

    def position(self):
        height = sum(w.height for w in self.box.get_children())
        width = self.width

        y = self.y_offset - (height if settings.INVERT_Y else 0)
        x = self.x_offset - (width if settings.INVERT_X else 0)

        self.resize(width, height)
        self.move(x, y)

    def close_all(self):
        self.history_index = None
        if self.history_timeout:
            GObject.source_remove(self.history_timeout)
            self.history_timeout = None
        for notification in list(self.notifications):
            self.remove_notification(notification)
        self.display()

    def close_last(self):
        self.history_index = None
        if self.notifications:
            self.remove_notification(self.notifications[-1])
        self.display()

    def history(self):
        if self.history_index is None:
            self.history_index = 0
        if abs(self.history_index) < Notification.count():
            self.history_index -= 1
        if settings.HISTORY_TIMEOUT:
            if self.history_timeout:
                GObject.source_remove(self.history_timeout)
            self.history_timeout = GObject.timeout_add(
                settings.HISTORY_TIMEOUT, self.close_all
            )
        self.display()

    def on_click(self, event, data=None):
        self.close_all()  # FIXME - should only remove the clicked message

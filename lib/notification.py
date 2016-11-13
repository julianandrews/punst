import collections
import gi
gi.require_version('Gtk', '3.0')  # noqa
from gi.repository import GObject, Pango
import os.path

from .gui import NotificationWindow
from . import settings


class Notification(object):
    __notifications = collections.OrderedDict()
    __window = NotificationWindow()

    def __init__(self, app_name, summary, body, icon, replaces_id, urgency):
        self.app_name = app_name
        self.summary = summary
        self.body = body
        self.icon = icon
        self.urgency = urgency
        self.message_id = replaces_id or self._get_next_message_id()
        self.formatted_text = self.get_formatted_text()

        self.__notifications.pop(self.message_id, None)
        self.__notifications[self.message_id] = self

    def show(self, expire_timeout):
        self.__window.add_notification(self, expire_timeout)

    def close(self):
        self.__window.remove_notification(self)

    def get_formatted_text(self):
        formatted = ""
        i = 0
        format_string = settings.FORMAT
        while i < len(format_string):
            c1 = format_string[i]
            c2 = format_string[i + 1] if i < len(format_string) + 1 else None
            if c1 == '%' and c2 in '%asbiI':
                if c2 == '%':
                    formatted += '%'
                elif c2 == 'a':
                    formatted += self.clean_text(self.app_name)
                elif c2 == 's':
                    formatted += self.clean_text(self.summary)
                elif c2 == 'b':
                    formatted += self.clean_text(self.body)
                elif c2 == 'i':
                    formatted += self.clean_text(self.icon)
                elif c2 == 'I':
                    formatted += self.clean_text(os.path.basename(self.icon))
                i += 2
            else:
                formatted += c1
                i += 1
        return formatted

    def clean_text(self, text):
        if settings.IGNORE_NEWLINE:
            text = text.replace('\n', '')
        use_plain_text = settings.PLAIN_TEXT
        if not use_plain_text:
            # Default to using plain text if the markup can't be parsed
            try:
                parsed = Pango.parse_markup(text, -1, u'\x00')
            except GObject.GError:
                use_plain_text = True

        if settings.ALLOW_MARKUP:
            if use_plain_text:
                return GObject.markup_escape_text(text)
            else:
                return text
        else:
            if use_plain_text:
                return text
            else:
                return parsed.text

    @classmethod
    def get_by_id(cls, message_id):
        return cls.__notifications.get(message_id)

    @classmethod
    def close_last(cls):
        cls.__window.close_last()

    @classmethod
    def close_all(cls):
        cls.__window.close_all()

    @classmethod
    def history(cls):
        cls.__window.history()

    @classmethod
    def _get_next_message_id(cls):
        ids = list(cls.__notifications.keys())
        if not ids:
            return 1
        else:
            if len(ids) > settings.HISTORY_LENGTH:
                del cls.__notifications[ids[0]]
            return ids[-1] + 1

    def __str__(self):
        return "{} - {}".format(self.summary, self.body)

    def __repr__(self):
        return "Notification({})".format(self.summary)

    def __eq__(self, other):
        return self.message_id == other.message_id

from collections import namedtuple
try:
    from configparser import RawConfigParser
except ImportError:  # Python 2
    from ConfigParser import RawConfigParser
import gi
gi.require_version('Gtk', '3.0')  # noqa
from gi.repository import Gtk
import re


Geometry = namedtuple(
    'Geometry', ['width', 'height', 'invert_x', 'x', 'invert_y', 'y']
)
Color = namedtuple('Color', ['red', 'green', 'blue'])


def hex_to_rgb(s):
    if s[0] == s[-1] == '"' or s[0] == s[-1] == "'":
        s = s[1:-1]
    if s[0] == '#':
        s = s[1:]
    if len(s) != 6:
        raise ValueError("Invalid hex literal")
    return Color(*(int(s[i:i+2], 16) / 255.0 for i in range(0, 5, 2)))


def parse_geometry(s):
    if s[0] == s[-1] == '"' or s[0] == s[-1] == "'":
        s = s[1:-1]
    results = re.match('^(?:(-?\d+)?x(\d+)?)?(?:([+-])(\d+)([+-])(\d+))?$', s)
    if not results:
        raise ValueError("Invalid geometry literal")
    else:
        vals = results.groups()
        return Geometry(
            width=int(vals[0] or 0),
            height=int(vals[1] or 0),
            invert_x=vals[2] == '-',
            x=int(vals[3] or 0),
            invert_y=vals[4] == '-',
            y=int(vals[5] or 0)
        )


class ConfigError(Exception):
    def __init__(self, section, option, reason):
        self.section = section
        self.option = option
        message = "Failed to parse config for [{}]: {} - {}".format(
            section, option, reason
        )
        super(ConfigError, self).__init__(message)


class PunstConfigParser(RawConfigParser):
    def getaccelerator(self, section, option):
        value = self.get(section, option)
        keyval, modifiers = Gtk.accelerator_parse(value)
        if not (keyval or modifiers):
            raise ConfigError(section, option, "invalid keybinding")
        return value

    def getenum(self, section, option, enum):
        value = self.get(section, option)
        try:
            return enum[value.upper()]
        except KeyError:
            raise ConfigError("invalid {}".format(enum.__name__))

    def getint(self, section, option):
        try:
            return super(PunstConfigParser, self).getint(section, option)
        except ValueError:
            raise ConfigError(section, option, "invalid integer")

    def getnonnegativeint(self, section, option):
        value = self.getint(section, option)
        if value < 0:
            raise ConfigError(section, option, "non-negative integer required")
        return value

    def getboolean(self, section, option):
        try:
            return super(PunstConfigParser, self).getboolean(section, option)
        except ValueError:
            raise ConfigError(section, option, "invalid bool")

    def gethexcolor(self, section, option):
        value = self.get(section, option)
        try:
            return hex_to_rgb(value)
        except ValueError:
            raise ConfigError(section, option, "invalid hex color")

    def getgeometry(self, section, option):
        value = self.get(section, option)
        try:
            return parse_geometry(value)
        except ValueError:
            raise ConfigError(section, option, "invalid geometry")

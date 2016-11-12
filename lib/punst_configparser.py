try:
    from configparser import RawConfigParser
except ImportError:  # Python 2
    from ConfigParser import RawConfigParser

import re


def hex_to_rgb(s):
    if s[0] == s[-1] == '"' or s[0] == s[-1] == "'":
        s = s[1:-1]
    if s[0] == '#':
        s = s[1:]
    if len(s) != 6:
        raise ValueError("Invalid hex literal")
    return tuple(int(s[i:i+2], 16) / 255.0 for i in range(0, 5, 2))


def parse_geometry(s):
    if s[0] == s[-1] == '"' or s[0] == s[-1] == "'":
        s = s[1:-1]
    results = re.match('^(?:(-?\d+)?x(\d+)?)?(?:([+-])(\d+)([+-])(\d+))?$', s)
    if not results:
        raise ValueError("Invalid geometry literal")
    else:
        vals = results.groups()
        return (
            int(vals[0] or 0),
            int(vals[1] or 0),
            vals[2] == '-',
            int(vals[3] or 0),
            vals[4] == '-',
            int(vals[5] or 0)
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
    def getalignment(self, section, option):
        value = self.get(section, option)
        if not value.upper() in ('LEFT', 'RIGHT', 'CENTER'):
            raise ConfigError("invalid alignment")
        return value

    def getint(self, section, option):
        try:
            return super(PunstConfigParser, self).getint(section, option)
        except ValueError:
            raise ConfigError(section, option, "invalid integer")

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

try:
    from configparser import RawConfigParser
except ImportError:  # Python 2
    from ConfigParser import RawConfigParser

from .utils import hex_to_rgb, parse_geometry


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

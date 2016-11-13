from __future__ import print_function
import enum
import os
import sys
import xdg.BaseDirectory

from .punst_configparser import PunstConfigParser, ConfigError


class NotificationUrgency(enum.Enum):
    LOW = 0
    NORMAL = 1
    CRITICAL = 2


class AlignmentType(enum.Enum):
    LEFT = 'LEFT'
    RIGHT = 'RIGHT'
    CENTER = 'CENTER'


class FollowType(enum.Enum):
    NONE = 0
    MOUSE = 1
    KEYBOARD = 2


APP_NAME = 'punst'
VENDOR = ''
VERSION = '0.1'
DEBUG = False

config_files = [os.path.join(os.path.dirname(__file__), 'defaults.cfg')] + [
    os.path.join(d, '{}.cfg'.format(APP_NAME))
    for d in xdg.BaseDirectory.load_config_paths(APP_NAME)
]
config = PunstConfigParser()
config.read(config_files)

try:
    FONT = config.get('global', 'font')
    ALLOW_MARKUP = config.getboolean('global', 'allow_markup')
    PLAIN_TEXT = config.getboolean('global', 'plain_text')
    FORMAT = config.get('global', 'format').encode().decode('unicode_escape')
    ALIGNMENT = config.getenum('global', 'alignment', AlignmentType)
    WORD_WRAP = config.getboolean('global', 'word_wrap')
    IGNORE_NEWLINE = config.getboolean('global', 'ignore_newline')
    WIDTH, HEIGHT, INVERT_X, X, INVERT_Y, Y = config.getgeometry(
        'global', 'geometry'
    )
    MONITOR_NUMBER = config.getint('global', 'monitor')
    FOLLOW = config.getenum('global', 'follow', FollowType)
    HISTORY_LENGTH = config.getint('global', 'history_length')
    PADDING = (
        config.getint('global', 'horizontal_padding'),
        config.getint('global', 'padding'),
    )
    STARTUP_NOTIFICATION = config.getboolean('global', 'startup_notification')

    FRAME_WIDTH = config.getint('frame', 'width')
    FRAME_COLOR = config.gethexcolor('frame', 'color')

    SHORTCUT_CLOSE = config.getaccelerator('shortcuts', 'close')
    SHORTCUT_CLOSE_ALL = config.getaccelerator('shortcuts', 'close_all')
    SHORTCUT_HISTORY = config.getaccelerator('shortcuts', 'history')

    BG_COLORS = {
        NotificationUrgency.LOW: config.gethexcolor(
            'urgency_low', 'background'
        ),
        NotificationUrgency.NORMAL: config.gethexcolor(
            'urgency_normal', 'background'
        ),
        NotificationUrgency.CRITICAL: config.gethexcolor(
            'urgency_critical', 'background'
        ),
    }

    FG_COLORS = {
        NotificationUrgency.LOW: config.gethexcolor(
            'urgency_low', 'foreground'
        ),
        NotificationUrgency.NORMAL: config.gethexcolor(
            'urgency_normal', 'foreground'
        ),
        NotificationUrgency.CRITICAL: config.gethexcolor(
            'urgency_critical', 'foreground'
        ),
    }

    TIMEOUTS = {
        NotificationUrgency.LOW: config.getint(
            'urgency_low', 'timeout'
        ) * 1000,
        NotificationUrgency.NORMAL: config.getint(
            'urgency_normal', 'timeout'
        ) * 1000,
        NotificationUrgency.CRITICAL: config.getint(
            'urgency_critical', 'timeout'
        ) * 1000,
    }
except ConfigError as e:
    if DEBUG:
        raise
    else:
        print(e, file=sys.stderr)
        sys.exit(1)

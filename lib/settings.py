from __future__ import print_function
import os
import sys
import xdg.BaseDirectory

from .punst_configparser import PunstConfigParser, ConfigError
from .utils import NotificationUrgency

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
    USE_MARKUP = config.getboolean('global', 'allow_markup')
    FORMAT = config.get('global', 'format').encode().decode('unicode_escape')
    WIDTH, HEIGHT, INVERT_X, X, INVERT_Y, Y = config.getgeometry(
        'global', 'geometry'
    )
    MONITOR_NUMBER = config.getint('global', 'monitor')
    HISTORY_LENGTH = config.getint('global', 'history_length')
    PADDING = (
        config.getint('global', 'horizontal_padding'),
        config.getint('global', 'padding'),
    )

    FRAME_WIDTH = config.getint('frame', 'width')
    FRAME_COLOR = config.gethexcolor('frame', 'color')

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
        print(e.message, file=sys.stderr)
        sys.exit(1)

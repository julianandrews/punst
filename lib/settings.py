from .utils import NotificationUrgency


HISTORY_SIZE = 20
MONITOR_NUMBER = 0
WIDTH = 300
HEIGHT = None
X = -10
Y = 10
PADDING = (10, 10)
FONT = "Sans 10"
FORMAT = "<b>%s</b>\n%b"
FRAME_WIDTH = 1
FRAME_COLOR = "#FF00FF"

BG_COLORS = {
    NotificationUrgency.LOW: "#222222",
    NotificationUrgency.NORMAL: "#014421",
    NotificationUrgency.CRITICAL: "#FFFF00",
}

FG_COLORS = {
    NotificationUrgency.LOW: "#888888",
    NotificationUrgency.NORMAL: "#FFFFFF",
    NotificationUrgency.CRITICAL: "#000000",
}

TIMEOUTS = {
    NotificationUrgency.LOW: 10000,
    NotificationUrgency.NORMAL: 10000,
    NotificationUrgency.CRITICAL: None,
}

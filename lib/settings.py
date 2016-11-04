from .utils import NotificationUrgency


HISTORY_SIZE = 20
MONITOR_NUMBER = 0
WINDOW_WIDTH = 400
PADDING = (15, 15)
FONT = "Sans 10"
FORMAT = "<b>%s</b>\n%b"

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

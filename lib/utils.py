import enum


class NotificationUrgency(enum.Enum):
    LOW = 0
    NORMAL = 1
    CRITICAL = 2


def hex_to_rgb(s):
    return tuple(int(s[i:i+2], 16) / 255.0 for i in range(1, 6, 2))

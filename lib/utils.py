import enum
import re


class NotificationUrgency(enum.Enum):
    LOW = 0
    NORMAL = 1
    CRITICAL = 2


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

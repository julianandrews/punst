import enum
import re


class NotificationUrgency(enum.Enum):
    LOW = 0
    NORMAL = 1
    CRITICAL = 2


def format_text(format_string, summary, body):
    formatted = ""
    i = 0
    while i < len(format_string):
        c1 = format_string[i]
        c2 = format_string[i + 1] if i < len(format_string) + 1 else None
        if c1 == '%' and c2 in '%sb':
            if c2 == '%':
                formatted += '%'
            elif c2 == 's':
                formatted += summary
            elif c2 == 'b':
                formatted += body
            i += 2
        else:
            formatted += c1
            i += 1
    return formatted


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
    results = re.match('^(?:(-?\d+)?x(\d+)?)?(?:([+-]\d+)([+-]\d+))?$', s)
    if not results:
        raise ValueError("Invalid geometry literal")
    else:
        return (int(x) if x else 0 for x in results.groups())

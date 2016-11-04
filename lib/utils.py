import enum


class NotificationUrgency(enum.Enum):
    LOW = 0
    NORMAL = 1
    CRITICAL = 2


def hex_to_rgb(s):
    return tuple(int(s[i:i+2], 16) / 255.0 for i in range(1, 6, 2))


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

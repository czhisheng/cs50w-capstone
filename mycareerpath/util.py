import math

def convert_time(time):
    seconds = time.total_seconds()
    if seconds < 60:
        return "just now"
    minutes = math.floor(seconds / 60)
    if minutes < 60:
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    hours = math.floor(minutes / 60)
    if hours < 24:
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    days = math.floor(hours / 24)
    if days < 7:
        return f"{days} day{'s' if days > 1 else ''} ago"
    weeks = math.floor(days / 7)
    if weeks < 4:
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"
    months = math.floor(weeks / 4)
    if months < 12:
        return f"{months} month{'s' if months > 1 else ''} ago"
    years = math.floor(months / 12)
    return f"{years} year{'s' if years > 1 else ''} ago"

#from jinja2 import Markup
from markupsafe import Markup

from datetime import datetime

class momentjs:
    def __init__(self, timestamp):
        self.timestamp = timestamp

    def render(self, format):
        """Render date on server-side using Python datetime instead of client-side JavaScript"""
        if self.timestamp is None:
            return Markup("")
        
        # Ensure timestamp is a datetime object
        if isinstance(self.timestamp, str):
            try:
                # Try parsing ISO format first
                dt = datetime.fromisoformat(self.timestamp.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                try:
                    # Fallback to strptime for other formats
                    dt = datetime.strptime(self.timestamp, '%Y-%m-%d %H:%M:%S')
                except (ValueError, TypeError):
                    return Markup("")
        else:
            dt = self.timestamp
        
        # Python datetime format to strftime equivalent
        # Convert moment.js format strings to Python strftime format
        format_map = {
            'MMMM Do, YYYY': '%B %d, %Y',  # December 5, 2025
            'MMMM Do': '%B %d',             # December 5
            'MMM D': '%b %d',               # Dec 5
            'YYYY-MM-DD': '%Y-%m-%d',
            'DD/MM/YYYY': '%d/%m/%Y',
            'MM/DD/YYYY': '%m/%d/%Y',
        }
        
        # Get the format or use as-is if not mapped
        python_format = format_map.get(format, format)
        
        try:
            return Markup(dt.strftime(python_format))
        except (ValueError, TypeError):
            return Markup("")
    
    # Format time
    def format(self, fmt):
        return self.render(fmt)

    def calendar(self):
        """Calendar format: today/tomorrow at time, etc"""
        if self.timestamp is None:
            return Markup("")
        
        if isinstance(self.timestamp, str):
            try:
                dt = datetime.fromisoformat(self.timestamp.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                try:
                    dt = datetime.strptime(self.timestamp, '%Y-%m-%d %H:%M:%S')
                except (ValueError, TypeError):
                    return Markup("")
        else:
            dt = self.timestamp
        
        today = datetime.now().date()
        tomorrow = today.replace(day=today.day + 1) if today.day < 28 else today.replace(day=1, month=today.month + 1)
        
        if dt.date() == today:
            return Markup(f"Today at {dt.strftime('%I:%M %p')}")
        elif dt.date() == tomorrow:
            return Markup(f"Tomorrow at {dt.strftime('%I:%M %p')}")
        else:
            return Markup(dt.strftime('%B %d, %Y at %I:%M %p'))

    def fromNow(self):
        """Relative time: 2 hours ago, in 3 days, etc"""
        if self.timestamp is None:
            return Markup("")
        
        if isinstance(self.timestamp, str):
            try:
                dt = datetime.fromisoformat(self.timestamp.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                try:
                    dt = datetime.strptime(self.timestamp, '%Y-%m-%d %H:%M:%S')
                except (ValueError, TypeError):
                    return Markup("")
        else:
            dt = self.timestamp
        
        now = datetime.now()
        diff = dt - now
        
        total_seconds = int(diff.total_seconds())
        
        if total_seconds < 0:
            # Past
            abs_seconds = abs(total_seconds)
            if abs_seconds < 60:
                return Markup("just now")
            elif abs_seconds < 3600:
                minutes = abs_seconds // 60
                return Markup(f"{minutes} minute{'s' if minutes > 1 else ''} ago")
            elif abs_seconds < 86400:
                hours = abs_seconds // 3600
                return Markup(f"{hours} hour{'s' if hours > 1 else ''} ago")
            else:
                days = abs_seconds // 86400
                return Markup(f"{days} day{'s' if days > 1 else ''} ago")
        else:
            # Future
            if total_seconds < 60:
                return Markup("in a few seconds")
            elif total_seconds < 3600:
                minutes = total_seconds // 60
                return Markup(f"in {minutes} minute{'s' if minutes > 1 else ''}")
            elif total_seconds < 86400:
                hours = total_seconds // 3600
                return Markup(f"in {hours} hour{'s' if hours > 1 else ''}")
            else:
                days = total_seconds // 86400
                return Markup(f"in {days} day{'s' if days > 1 else ''}")

 
        

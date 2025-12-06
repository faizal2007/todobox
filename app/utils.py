#from jinja2 import Markup
from markupsafe import Markup

from datetime import datetime

class momentjs:
    def __init__(self, timestamp):
        self.timestamp = timestamp

    def render(self, format):
        # Escape timestamp to prevent XSS injection
        from html import escape
        safe_timestamp = escape(str(self.timestamp))
        safe_format = escape(str(format))
        return Markup("<script>\ndocument.write(moment(\"%s\").%s);\n</script>" % (safe_timestamp, safe_format))
    
    # Format time
    def format(self, fmt):
        return self.render("format(\"%s\")" % fmt)

    def calendar(self):
        return self.render("calendar()")

    def fromNow(self):
        return self.render("fromNow()")
 
        

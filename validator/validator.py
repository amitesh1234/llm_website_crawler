import re

url_regex = re.compile(
    r'^(https?|ftp):\/\/'  # Protocol: http, https, or ftp
    r'([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}'  # Domain name
    r'(\/[^\s]*)?$',  # Optional path
    re.IGNORECASE
)

def validate_url(url):
    return re.match(url_regex, url) is not None
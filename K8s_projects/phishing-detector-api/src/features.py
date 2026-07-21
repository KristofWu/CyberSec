import re

FEATURES = ["url_length", "dot_count", "hyphen_count", "digit_count", "has_https", "has_ip", "has_suspicious"]

def has_ip(url):
    if re.search(r"https?://\d+\.\d+\.\d+\.\d+", url):
        return 1
    else:
        return 0

def has_suspicious(url):
    suspicious = ["login", "verify", "secure", "account", "bank", "update"]
    url_lower = url.lower()
    for word in suspicious:
        if word in url_lower:
            return 1
    return 0

def extract_features(url):
    """Extract the 7 model features from a single URL."""
    return{
        "url_length": len(url),
        "dot_count": url.count("."),
        "hyphen_count": url.count("-"),
        "digit_count": sum(c.isdigit() for c in url),
        "has_https": int(url.startswith("https")),
        "has_ip": has_ip(url),
        "has_suspicious": has_suspicious(url)
    }
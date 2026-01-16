from urllib.parse import urlparse, urljoin
from typing import Optional


def normalize_url(url: str) -> str:
    """Normalize URL to include scheme"""
    url = url.strip()
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    return url


def is_valid_url(url: str) -> bool:
    """Check if URL is valid"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def get_base_url(url: str) -> str:
    """Extract base URL (scheme + netloc)"""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def is_same_domain(url1: str, url2: str) -> bool:
    """Check if two URLs are from the same domain"""
    domain1 = urlparse(url1).netloc
    domain2 = urlparse(url2).netloc
    return domain1 == domain2
from urllib.parse import urlparse


def validate_linkedin_url(url: str) -> bool:
    if not url:
        return False
    try:
        parsed = urlparse(url.strip())
        host = parsed.netloc.lower().replace("www.", "")
        return parsed.scheme in {"http", "https"} and host.endswith("linkedin.com") and "/in/" in parsed.path
    except Exception:
        return False


def split_lines(value: str) -> list[str]:
    return [item.strip() for item in (value or "").replace(",", "\n").splitlines() if item.strip()]


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))

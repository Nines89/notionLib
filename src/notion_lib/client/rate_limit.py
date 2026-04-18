import time
from .errors import RateLimited


def handle_rate_limit(response):
    if response.status_code != 429:
        return

    retry = response.headers.get("Retry-After")
    retry = float(retry) if retry is not None else 1.0
    time.sleep(retry)
    raise RateLimited("Rate limit hit — auto-retry dopo sleep.")

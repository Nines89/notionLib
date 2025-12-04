import time
from .errors import RateLimited


def handle_rate_limit(response):
    if response.status_code != 429:
        return

    retry = response.headers.get("Retry-After")
    if retry is None:
        retry = 1
    else:
        retry = float(retry)

    time.sleep(retry)
    raise RateLimited("Retry limit exceeded, handled by auto-retry.")

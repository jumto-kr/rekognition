import requests

REQUESTS_SESSION = requests.session()
def _fetch(session, url) -> dict:
    try:
        result = session.get(url)
        return result.json()
    except Exception:
        return {}
def fetch(url: str):
    return _fetch(REQUESTS_SESSION, url=url)

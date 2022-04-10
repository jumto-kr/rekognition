from typing import Optional, Dict, Any, IO

import requests


class ErrorResponse(Exception):
    def __init__(self, error_code: int, body: Optional[dict]):
        super(ErrorResponse, self).__init__()
        self.error_code = error_code
        self.body = body

    def __str__(self):
        return f'Error code: {self.error_code}. {str(self.body)}'


REQUESTS_SESSION = requests.session()
def _fetch(session, url: str, method: str, data: Optional[Dict[str, Any]], files: Optional[Dict[str, IO]]) -> Dict[str, Any]:
    try:
        result = session.request(method=method, url=url, data=data, files=files).json()
        if result['error_code'] != 0:
            raise ErrorResponse(error_code=result['error_code'], body=result.get('body'))
        return result['body']
    except ErrorResponse as e:
        raise
    except Exception as e:
        return dict(message="Unknown Error")
def fetch(url: str, method: str = 'GET', data: Optional[Dict[str, Any]] = None, files: Optional[Dict[str, IO]] = None) -> Dict[str, Any]:
    return _fetch(REQUESTS_SESSION, url=url, method=method, data=data, files=files)

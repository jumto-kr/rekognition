from typing import Optional, Dict, Any, IO

import requests

import streamlit_config


assert streamlit_config.api_url_protocol.endswith('://')
assert not streamlit_config.api_url_host.endswith('/')


class ErrorResponse(Exception):
    def __init__(self, error_code: int, body: Optional[dict]):
        super(ErrorResponse, self).__init__()
        self.error_code = error_code
        self.body = body

    def __str__(self):
        return f'Error code: {self.error_code}. {str(self.body)}'


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
    with requests.session() as session:
        return _fetch(session, url=url, method=method, data=data, files=files)


def call_api(url_path: str, method: str = 'GET', data: Optional[Dict[str, Any]] = None, files: Optional[Dict[str, IO]] = None) -> Dict[str, Any]:
    if not url_path.startswith('/'):
        url_path = '/' + url_path
    return fetch(url=f'{streamlit_config.api_url_protocol}{streamlit_config.api_url_host}{url_path}', method=method, data=data, files=files)

from typing import Optional, Callable, Any

import functools

import botocore.exceptions


ClientError = botocore.exceptions.ClientError


class RequestError(ValueError):
    def __init__(self, message: str, boto_exception: Optional[ botocore.exceptions.ClientError] = None):
        self.message = message

        if boto_exception is not None:
            assert isinstance(boto_exception, botocore.exceptions.ClientError)
            try:
                self.request_id = boto_exception.response['ResponseMetadata']['RequestId']
            except Exception:
                self.request_id = None

    __context__: ClientError

    def __str__(self):
        return f'{self.message}' + (f' RequestId={self.request_id}' if self.request_id is not None else '')


def handle_request_error(func: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RequestError as e:
            try:
                request_id = e.__context__.response['ResponseMetadata']['RequestId']
            except Exception:
                request_id = None
            e.request_id = request_id
            raise
    return wrapper

import mimetypes
from typing import Optional, Callable, Any, IO, Union, TypedDict, Tuple

import functools
import os

import botocore.exceptions
import boto3

try:
    from . import utils_alert
except Exception:
    import utils_alert


ClientError = botocore.exceptions.ClientError


class RequestError(ValueError):
    def __init__(self, message: str, boto_exception: Optional[botocore.exceptions.ClientError] = None):
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


@utils_alert.alert_slack_when_exception
def upload_s3(file: Union[str, IO], bucket_name: str, key: str, content_type: Optional[str] = None, content_encoding: Optional[str] = None) -> dict:
    if isinstance(file, str):
        if content_type is None and content_encoding is None:
            content_type, content_encoding = mimetypes.guess_type(file)

        file_should_be_closed = True
        file = open(file, 'rb')
    else:
        file_should_be_closed = False

    s3_client = boto3.client('s3')
    if os.sep == '\\':
        key = key.replace(os.sep, '/')
    kwargs = {key: value for key, value in dict(ContentType=content_type, ContentEncoding=content_encoding).items() if value is not None}
    returned = s3_client.put_object(Bucket=bucket_name, Body=file, Key=key, **kwargs)

    if file_should_be_closed:
        file.close()
    return returned


@utils_alert.alert_slack_when_exception
def download_s3(bucket_name: str, key: str) -> bytes:
    s3_client = boto3.client('s3')
    returned = s3_client.get_object(Bucket=bucket_name, Key=key)['Body'].read()
    return returned


class BoundingBox(TypedDict):
    Width: float
    Height: float
    Left: float
    Top: float
def to_abs_bounding_box_corners(bounding_box: BoundingBox, size: Tuple[float, float]) -> Tuple[float, float, float, float]:
    x0_rel = bounding_box['Left']
    y0_rel = bounding_box['Top']
    x1_rel = bounding_box['Left'] + bounding_box['Width']
    y1_rel = bounding_box['Top'] + bounding_box['Height']

    x0_abs, x1_abs = [(x * size[0]) for x in [x0_rel, x1_rel]]
    y0_abs, y1_abs = [(y * size[1]) for y in [y0_rel, y1_rel]]
    return x0_abs, y0_abs, x1_abs, y1_abs


class Face(TypedDict):
    FaceId: str
    BoundingBox: BoundingBox
    ImageId: str
    ExternalImageId: str
    Confidence: float


class FaceMatch(TypedDict):
    Similarity: float
    Face: Face

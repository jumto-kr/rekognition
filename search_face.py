from icecream import ic
# ic = print

import boto3

from utils import *
from utils_boto3 import *


class NoFaceInSearchingError(RequestError):
    def __init__(self, boto_exception: botocore.exceptions.ClientError):
        super(NoFaceInSearchingError, self).__init__(message=f'No Faces are found in the search. Each face must not be smaller than 40x40 in 1920x1080.', boto_exception=boto_exception)


class ImageTooLargeError(RequestError):
    def __init__(self, boto_exception: botocore.exceptions.ClientError):
        super(ImageTooLargeError, self).__init__(message=f'Image is too large. size < 5MB and (height and width) < 4096 pixels.', boto_exception=boto_exception)


@handle_request_error
def search_face_id(face_id: str, collection_id: str):
    threshold = 90
    max_faces = 2
    client = boto3.client('rekognition')
    try:
        response = client.search_faces(CollectionId=collection_id, FaceId=face_id, FaceMatchThreshold=threshold, MaxFaces=max_faces)
    except client.exceptions.InvalidParameterException as e:
        raise NoFaceInSearchingError(boto_exception=e)
    except client.exceptions.ImageTooLargeError as e:
        raise ImageTooLargeError(boto_exception=e)

    assert response['SearchedFaceId'] == face_id
    assert len(response['FaceMatches']) >= 1
    assert list(response['FaceMatches']) == list(sorted(response['FaceMatches'], key=lambda face_match: face_match['Similarity'], reverse=True))

    for face_match in list(response['FaceMatches']):
        ic(face_match['Face'])


@handle_request_error
def search_face_by_image(image_bytes: bytes, collection_id: str, max_matches: int = 10, threshold: int = 70) -> dict:
    client = boto3.client('rekognition')
    try:
        response = client.search_faces_by_image(CollectionId=collection_id, Image={'Bytes': image_bytes}, FaceMatchThreshold=threshold, MaxFaces=max_matches)
    except client.exceptions.InvalidParameterException as e:
        raise NoFaceInSearchingError(boto_exception=e)
    except client.exceptions.ImageTooLargeError as e:
        raise ImageTooLargeError(boto_exception=e)
    face_matches = response['FaceMatches']
    if len(face_matches) > 1:
        raise NotImplementedError('Not yet support multiple reference image for a single reference person.')

    return face_matches[0]


if __name__ == '__main__':
    image_path='./resources/jisu_single.jpg'
    with open(image_path, 'rb') as file:
        image_bytes = file.read()
    image_bytes = convert_image_bytes_popular(image_bytes=image_bytes)

    collection_id = 'idols'
    threshold = 70
    max_matches = 3

    ic(search_face_by_image(image_bytes=image_bytes, collection_id=collection_id, max_matches=max_matches, threshold=threshold))

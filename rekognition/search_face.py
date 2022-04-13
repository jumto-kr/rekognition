from typing import Optional

from icecream import ic
# ic = print

import boto3

try:
    from . import utils
    from . import utils_boto3

    from . import config
except ImportError:
    import utils
    import utils_boto3

    import config


class NoFaceInSearchingError(utils_boto3.RequestError):
    def __init__(self, boto_exception: utils_boto3.ClientError):
        super(NoFaceInSearchingError, self).__init__(message=f'No Faces are found in the search. Each face must not be smaller than 40x40 in 1920x1080.', boto_exception=boto_exception)


class ImageTooLargeError(utils_boto3.RequestError):
    def __init__(self, boto_exception: utils_boto3.ClientError):
        super(ImageTooLargeError, self).__init__(message=f'Image is too large. size < 5MB and (height and width) < 4096 pixels.', boto_exception=boto_exception)


class NoMatchedFaceError(LookupError):
    def __init__(self, collection_id: str):
        super(NoMatchedFaceError, self).__init__(f'No matched faces in the collection {collection_id}.')


@utils_boto3.handle_request_error
def _search_face_by_image(image_bytes: bytes, collection_id: str, max_matches: int = 10, threshold: int = 40) -> dict:
    client = boto3.client('rekognition')
    try:
        response = client.search_faces_by_image(CollectionId=collection_id, Image={'Bytes': image_bytes}, FaceMatchThreshold=threshold, MaxFaces=max_matches)
    except client.exceptions.InvalidParameterException as e:
        raise NoFaceInSearchingError(boto_exception=e)
    except client.exceptions.ImageTooLargeException as e:
        raise ImageTooLargeError(boto_exception=e)
    face_matches = response['FaceMatches']
    if len(face_matches) > 1:
        # TODO:
        # raise NotImplementedError('Not yet support multiple reference image for a single reference person.')
        pass

    if len(face_matches) == 0:
        raise NoMatchedFaceError(collection_id=collection_id)
    else:
        # TODO:
        # assert len(face_matches) == 1
        return face_matches[0]


def search_face_by_image(image_bytes: bytes, threshold: Optional[int] = None) -> dict:
    collection_id = config.idols_collection_id
    max_matches = config.max_matches
    threshold = threshold if threshold is not None else config.default_threshold
    return _search_face_by_image(image_bytes=image_bytes, collection_id=collection_id, max_matches=max_matches, threshold=threshold)


if __name__ == '__main__':
    image_path = '../resources/jisoo_single.jpg'
    with open(image_path, 'rb') as file:
        image_bytes = file.read()
    image_bytes = utils.convert_image_bytes_popular(image_bytes=image_bytes)

    ic(search_face_by_image(image_bytes=image_bytes))

from typing import List, Dict

import boto3

try:
    from . import utils_boto3
except ImportError:
    import utils_boto3


_LIST_FACES: Dict[str, List[dict]] = dict()
@utils_boto3.handle_request_error
def list_faces(collection_id: str, fresh: bool, max_results=100) -> List[dict]:
    if fresh or collection_id not in _LIST_FACES:
        client = boto3.client('rekognition')

        faces = []
        response = client.list_faces(CollectionId=collection_id, MaxResults=max_results)
        while response is not None:
            faces.extend(list(response['Faces']))
            if 'NextToken' in response:
                next_token = response['NextToken']
                response = client.list_faces(CollectionId=collection_id, MaxResults=max_results, next_token=next_token)
            else:
                response = None
        _LIST_FACES[collection_id] = faces
    return _LIST_FACES[collection_id]

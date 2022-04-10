from __future__ import annotations

import os
import glob
from tqdm import tqdm

import boto3

try:
    from . import config
    from .idol import Idol
    from . import utils_boto3
    from .caching_boto3 import list_faces
except ImportError:
    import config
    from idol import Idol
    import utils_boto3
    from caching_boto3 import list_faces
if not config.VERBOSE:
    def tqdm(iterable=None, *args, **kwargs):
        return iterable


def _clear_all_idols(collection_id: str) -> None:
    client = boto3.client('rekognition')
    client.delete_collection(CollectionId=collection_id)
    client.create_collection(CollectionId=collection_id)
def clear_all_idols() -> None:
    _clear_all_idols(collection_id=config.idols_collection_id)


def upload_idol(image_path: str, repr_name: str) -> dict:
    image_s3_bucket_name = config.idols_bucket_name
    image_s3_object_key = os.path.join(config.idols_profile_root_path, repr_name, os.path.basename(image_path))
    if os.sep == '\\' and os.sep in image_s3_object_key:
        image_s3_object_key = image_s3_object_key.replace(os.sep, '/')
    utils_boto3.upload_s3(file=image_path, bucket_name=image_s3_bucket_name, key=image_s3_object_key)

    idol = Idol(repr_name=repr_name, image_s3_bucket_name=config.idols_bucket_name, image_s3_object_key=image_s3_object_key)

    collection_id = config.idols_collection_id
    client = boto3.client('rekognition')
    return client.index_faces(Image=dict(S3Object=dict(Bucket=idol.image_s3_bucket_name, Name=idol.image_s3_object_key)), CollectionId=collection_id, ExternalImageId=idol.to_external_image_id(), DetectionAttributes=['ALL'], MaxFaces=1)


def upload_idols_from_directory(root_path: str) -> list[dict]:
    idols_responses = []
    for dir_path in filter(os.path.isdir, tqdm(glob.glob(os.path.join(root_path, '*')))):
        repr_name = os.path.basename(dir_path)
        for image_path in filter(os.path.isfile, glob.glob(os.path.join(dir_path, '*'))):
            idols_responses.append(upload_idol(image_path=image_path, repr_name=repr_name))

    return idols_responses


if __name__ == '__main__' and True:
    clear_all_idols()

    upload_idols_from_directory(root_path="C:\\Users\\gomde\\Downloads\\sample_profiles")

    faces = list_faces(collection_id=config.idols_collection_id, fresh=True)
    for face in faces:
        idol = Idol.from_face_dict_aws(face_dict=face)
        print(idol)

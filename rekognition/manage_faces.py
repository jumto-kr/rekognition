from __future__ import annotations

import logging
from typing import Union, IO, Optional, List

import os
import posixpath
import glob
import re
from tqdm import tqdm

import click

try:
    from . import utils_alert
    from . import config
    from .idol import Idol
    from . import utils_boto3
    from .caching_boto3 import list_faces, list_idols
except ImportError:
    import utils_alert
    import config
    from idol import Idol
    import utils_boto3
    from caching_boto3 import list_faces, list_idols
if not config.VERBOSE:
    def tqdm(iterable=None, *_, **__):
        return iterable


@utils_alert.alert_slack_when_exception
def _clear_all_idols(collection_id: str) -> None:
    client = utils_boto3.client('rekognition')
    client.delete_collection(CollectionId=collection_id)
    client.create_collection(CollectionId=collection_id)
def clear_all_idols() -> None:
    _clear_all_idols(collection_id=config.idols_collection_id)


@utils_alert.alert_slack_when_exception
def upload_idol_local(image_path: str, idol_id: str) -> dict:
    image_s3_bucket_name = config.idols_bucket_name
    image_s3_object_key = posixpath.join(config.idols_profile_root_path, idol_id, posixpath.basename(image_path))
    with open(image_path, 'rb') as file:
        image = file.read()
    return upload_idol(image=image, idol_id=idol_id, image_s3_bucket_name=image_s3_bucket_name, image_s3_object_key=image_s3_object_key)


@utils_alert.alert_slack_when_exception
def upload_idol(image: Union[str, IO], idol_id: str, image_s3_bucket_name: str, image_s3_object_key: str, content_type: Optional[str] = None):
    utils_boto3.upload_s3(file=image, bucket_name=image_s3_bucket_name, key=image_s3_object_key, content_type=content_type)
    idol = Idol(idol_id=idol_id, image_s3_bucket_name=config.idols_bucket_name, image_s3_object_key=image_s3_object_key)

    collection_id = config.idols_collection_id
    try:
        client = utils_boto3.client('rekognition')
        return client.index_faces(Image=dict(S3Object=dict(Bucket=idol.image_s3_bucket_name, Name=idol.image_s3_object_key)), CollectionId=collection_id, ExternalImageId=idol.to_external_image_id(), DetectionAttributes=['ALL'], MaxFaces=1)
    except BaseException:
        client = utils_boto3.client('s3')
        client.delete_object(Bucket=config.idols_bucket_name, Key=image_s3_object_key)
        raise


@utils_alert.alert_slack_when_exception
def upload_idols_from_directory(root_path: str) -> List[dict]:
    idols_responses = []
    for dir_path in filter(os.path.isdir, tqdm(glob.glob(os.path.join(root_path, '*')))):
        idol_id = os.path.basename(dir_path)
        for image_path in filter(os.path.isfile, glob.glob(os.path.join(dir_path, '*'))):
            idols_responses.append(upload_idol_local(image_path=image_path, idol_id=idol_id))

    return idols_responses


if __name__ == '__main__' and True:
    clear_all_idols()

    upload_idols_from_directory(root_path="C:\\Users\\gomde\\Downloads\\sample_profiles")

    faces = list_faces(collection_id=config.idols_collection_id, fresh=True)
    for face in faces:
        idol = Idol.from_face_dict_aws(face_dict=face)
        print(idol)


@utils_alert.alert_slack_when_exception
def list_faces_of_idol(idol_id_regex: str, fresh: bool) -> List[Idol]:
    idols = list_idols(collection_id=config.idols_collection_id, fresh=fresh)
    return [idol for idol in idols if re.fullmatch(pattern=idol_id_regex, string=idol.idol_id)]


@utils_alert.alert_slack_when_exception
def delete_face(face_id_regex: str, fresh: bool, idol_id: Optional[str] = None):
    collection_id = config.idols_collection_id

    idols: List[Idol] = list_idols(collection_id=collection_id, fresh=fresh)
    filtered_idols = [idol for idol in idols if re.fullmatch(pattern=face_id_regex, string=idol.face_id)]

    if len(filtered_idols) == 0:
        raise ValueError(f'No idol matched {face_id_regex}.')
    if len(filtered_idols) > 1:
        raise NotImplementedError(f'Multiple matches: {filtered_idols}')

    assert len(filtered_idols) == 1
    idol = filtered_idols[0]
    if idol_id != idol.idol_id:
        raise ValueError(f"Not matched idol_id({idol_id}) for face_id ({idol.face_id}")
    click.confirm(text=f"Delete {idol}?", abort=True)

    try:
        client = utils_boto3.client('rekognition')
        response = client.delete_faces(FaceIds=[idol.face_id], CollectionId=collection_id)
    except Exception as e:
        logging.warning(str(e))

    try:
        client = utils_boto3.client('s3')
        response = client.delete_object(Bucket=idol.image_s3_bucket_name, Key=Idol.escape_path(idol.image_s3_object_key))
    except Exception as e:
        logging.warning(str(e))

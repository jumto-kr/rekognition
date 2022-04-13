from typing import Optional

import os
from icecream import ic

from flask_app import app

from flask import request, render_template

import flask_app
if not flask_app.INCLUDE_VIEWS:
    def render_template(_: Optional[str], error_code: int, **kwargs) -> dict:
        assert 'error_code' not in kwargs
        return dict(error_code=error_code, body=kwargs)
from rekognition import search_face, utils, utils_boto3, config

CURRENT_USAGE = 0
MAX_USAGE = 50


@app.route('/upload', methods=['POST'])
def upload_post():
    global CURRENT_USAGE
    CURRENT_USAGE += 1
    if CURRENT_USAGE > MAX_USAGE:
        exit(1)
    ic(CURRENT_USAGE)
    try:
        file = request.files['file']
        image_bytes = utils.convert_image_bytes_popular(file.read())
        result = search_face.search_face_by_image(image_bytes=image_bytes)
    except utils_boto3.RequestError as e:
        return render_template('upload.html', error_code=-1, message=str(e))
    except Exception as e:
        return render_template('upload.html', error_code=-1, message=str(e))

    if result is None:
        message = f"Face detected, but cannot identify him/her."
        matches = []
        error_code = -1
    else:
        message = f"Found. Looks like {result['Face']['ExternalImageId']}. {result['Similarity']:3.0f}% similar."
        assert hasattr(result, 'keys') and hasattr(result, 'values'), "Result is expected as dict-like."
        matches = [result]
        error_code = 0
    return render_template('upload.html', error_code=error_code, message=message, matches=matches)


@app.route('/detail/<repr_name>')
def detail(repr_name: str):
    s3_object_key = f'{config.idols_profile_root_path}/{repr_name}/detail.md'
    returned = utils_boto3.download_s3(bucket_name=config.idols_bucket_name, key=s3_object_key)
    return render_template('', error_code=0, markdown=returned.decode())


@app.route('/resetgomdev')
def resetgomdev():
    global CURRENT_USAGE
    CURRENT_USAGE = 0

    return render_template('', error_code=0, message=f"Reset done. CURRENT_USAGE={CURRENT_USAGE}, MAX_USAGE={MAX_USAGE}")

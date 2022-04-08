from icecream import ic

from flask_app import app

from flask import request, render_template, redirect

from rekognition import search_face, utils, utils_boto3

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
        return render_template('upload.html', message=str(e))
    except Exception as e:
        return render_template('upload.html', message=str(e))

    if result is None:
        message = f"Face detected, but cannot identify him/her."
    else:
        message = f"Found. Looks like {result['Face']['ExternalImageId']}. {result['Similarity']:3.0f}% similar."
    return render_template('upload.html', message=message)


@app.route('/resetgomdev')
def resetgomdev():
    global CURRENT_USAGE
    CURRENT_USAGE = 0

    return redirect('/')
from icecream import ic

from flask import Flask
from flask import request, render_template
app = Flask(__name__)

import utils
import utils_boto3
import search_face


@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/upload', methods=['GET'])
def upload_get():
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload_post():
    try:
        file = request.files['file']
        image_bytes = utils.convert_image_bytes_popular(file.read())
        result = search_face.search_face_by_image(image_bytes=image_bytes, collection_id='idols')
    except utils_boto3.RequestError as e:
        return render_template('upload.html', message=str(e))
    except Exception as e:
        return render_template('upload.html', message=str(e))
    return render_template('upload.html', message=f"Found. Looks like {result['Face']['ExternalImageId']}. {result['Similarity']:3.0f}% similar.")


@app.errorhandler(500)
def server_error(e):
    r = render_template('error.html', body=str(e.original_exception))
    return r, 500

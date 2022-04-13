import io
from typing import TypedDict, Tuple

from PIL import Image, ImageDraw

import streamlit as st

import flask_app.models
import rekognition
import utils_streamlit


class MatchParsed(TypedDict):
    idol: rekognition.Idol
    similarity: float


def suggest_line_width(size: Tuple[float, float]) -> int:
    longer = max(size)
    return max(1, int(longer * 0.01))


if __name__ == '__main__':
    file = st.file_uploader('Image of the star you are watching.', type=['jpg', 'jpeg', 'png', 'bmp', 'gif', 'webp'])

    if file is not None:
        file_bytes = file.read()
        matches_response: flask_app.models.UploadPostPayload = utils_streamlit.call_api(url_path='/upload', method='POST', files=dict(file=file_bytes))

        column1, column2 = st.columns(2)
        with column1:
            canvas_image = Image.open(io.BytesIO(file_bytes))
            zoom = 400 / canvas_image.size[1]
            if zoom * canvas_image.size[0] > 400:
                zoom = 400 / canvas_image.size[0]
            canvas_image = canvas_image.resize(size=(int(canvas_image.size[0] * zoom), int(canvas_image.size[1] * zoom)))
            draw = ImageDraw.Draw(canvas_image)
            bounding_box_corners = rekognition.utils_boto3.to_abs_bounding_box_corners(bounding_box=matches_response['searched_face_bounding_box'], size=canvas_image.size)
            draw.rounded_rectangle(xy=bounding_box_corners, radius=suggest_line_width(canvas_image.size) * 4, width=suggest_line_width(canvas_image.size))
            st.image(image=canvas_image)
        with column2:
            for each_match in matches_response['matches']:
                idol = rekognition.Idol.from_external_image_id(each_match['Face']['ExternalImageId'])
                similarity = each_match['Similarity']

                st.write(idol.repr_name, similarity)

                detail_response: flask_app.models.DetailPayload = utils_streamlit.call_api(url_path=f'/detail/{idol.repr_name}')
                detail_md = detail_response['markdown']
                st.markdown(detail_md)

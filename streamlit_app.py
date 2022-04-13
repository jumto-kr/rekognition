from typing import TypedDict

import streamlit as st

import rekognition
import utils_streamlit


class MatchParsed(TypedDict):
    idol: rekognition.Idol
    similarity: float


st.write("hello")

st.write(utils_streamlit.call_api('/'))

file = st.file_uploader('Image of the star you are watching.', type=['jpg', 'jpeg', 'png', 'bmp', 'gif', 'webp'])

if file is not None:
    matches_response = utils_streamlit.call_api(url_path='/upload', method='POST', files=dict(file=file.read()))
    for each_match in matches_response['matches']:
        idol = rekognition.Idol.from_external_image_id(each_match['Face']['ExternalImageId'])
        similarity = each_match['Similarity']

        st.write(idol.repr_name, similarity)

        detail_response = utils_streamlit.call_api(url_path=f'/detail/{idol.repr_name}')
        detail_md = detail_response['markdown']
        st.markdown(detail_md)

    st.write(matches_response)

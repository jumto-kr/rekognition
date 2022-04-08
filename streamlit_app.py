import streamlit as st

import utils_streamlit
import rekognition.search_face

st.write("hello")

st.write(utils_streamlit.fetch(url="http://localhost:5000"))

file = st.file_uploader('Image of the star you are watching.', type=['jpg', 'jpeg', 'png', 'bmp', 'gif', 'webp'])

if file is not None:
    st.write(rekognition.search_face.search_face_by_image(image_bytes=file.read()))
import streamlit as st

import utils_streamlit


st.write("hello")

st.write(utils_streamlit.call_api('/'))

file = st.file_uploader('Image of the star you are watching.', type=['jpg', 'jpeg', 'png', 'bmp', 'gif', 'webp'])

if file is not None:
    matches_response = utils_streamlit.call_api(url_path='/upload', method='POST', files=dict(file=file.read()))
    st.write(matches_response)

import streamlit as st
import http.client
import base64
import json

###################################
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import JsCode

###################################



def _max_width_():
    max_width_str = f"max-width: 1800px;"
    st.markdown(
        f"""
    <style>
    .reportview-container .main .block-container{{
        {max_width_str}
    }}
    </style>    
    """,
        unsafe_allow_html=True,
    )

st.set_page_config(page_icon="✂️", page_title="ECG Gender Prediction")

st.image("./ecg.gif", width=300)

st.title("ECG Gender Prediction")

c30, c31 = st.columns([16, 1])

with c30:

    uploaded_file = st.file_uploader(
        "",
        type="npy",
        key="1",
        help="To activate 'wide mode', go to the hamburger menu > Settings > turn on 'wide mode'",
    )

    if uploaded_file is not None:
        content = uploaded_file.read()
        encoded_string = base64.b64encode(content).decode("utf-8")
        request_dict = {"input_params":encoded_string}
        payload = '{"input_params":' + json.dumps(request_dict) + "}"
        headers = {
            'Cnvrg-Api-Key': "dm32GHs3S9eojhMm5SsV9FbG",
            'Content-Type': "application/json"
            }


    if uploaded_file is not None:
        file_container = st.expander("Check your uploaded .csv")

        conn = http.client.HTTPSConnection("gastro-web-4-1.am22ensuxenodo5ihblszm8.cloud.cnvrg.io", 443)

        st.info('Sending POST command to the server')
        conn.request("POST", "/api/v1/endpoints/cukczelw3sytfuga7byy", payload, headers)
        st.info('Got server response')

        res = conn.getresponse()
        data = res.read()
        output = data.decode("utf-8")
        st.info(
            f"""
                {output}
                👆 The prediction result. [Gender, Probability]
                """
        )
        st.image("./logos.png")



    else:
        st.info(
            f"""
                👆 Upload a .npy ECG file first.)
                """
        )
        st.image("./logos.png")


        st.stop()
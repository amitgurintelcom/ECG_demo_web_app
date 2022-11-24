import streamlit as st
from streamlit_option_menu import option_menu
import http.client
import base64
import json
import re
import os
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
def select_host(selected):
    if selected=="AWS":
        api_key=os.getenv('api_key_aws')
        conn_addr=os.getenv('conn_addr_aws')
        conn_req=os.getenv('conn_req_aws')
        # api_key="dm32GHs3S9eojhMm5SsV9FbG"
        # conn_addr="gastro-web-4-1.am22ensuxenodo5ihblszm8.cloud.cnvrg.io"
        # conn_req="/api/v1/endpoints/cukczelw3sytfuga7byy"
    elif selected=="Intel DevCloud":
        api_key=os.getenv('api_key_intel')
        conn_addr=os.getenv('conn_addr_intel')
        conn_req=os.getenv('conn_req_intel')        
        # api_key="WeaN8QbbKmhWZHJryoJzuUM1"
        # conn_addr="ecg-web-dev-cloud-1.aaorm9bej4xwhihmdknjw5e.cloud.cnvrg.io"
        # conn_req="/api/v1/endpoints/q6wmgijl7mqesrqneoau"
    else:
        api_key=os.getenv('api_key_aws')
        conn_addr=os.getenv('conn_addr_aws')
        conn_req=os.getenv('conn_req_aws')
        # api_key="dm32GHs3S9eojhMm5SsV9FbG"
        # conn_addr="gastro-web-4-1.am22ensuxenodo5ihblszm8.cloud.cnvrg.io"
        # conn_req="/api/v1/endpoints/cukczelw3sytfuga7byy"
    return api_key, conn_addr, conn_req
    
st.set_page_config(page_icon="✂️", page_title="ECG Gender Prediction")
st.image("./logos.jpg", width=250)
st.image("./ecg.gif", width=250)
st.title("ECG Gender Prediction")
c30, c31 = st.columns([16, 1])
with c30:
    selected = option_menu(
        menu_title="Choose web host",  # required
        options=["AWS", "Intel DevCloud", "Azure (Future)"],  # required
        icons=["snow2", "bank2", "microsoft"],  # optional
        menu_icon="heart-pulse",  # optional
        default_index=0,  # optional
            )
    st.info(f'web host is {selected}')
    api_key, conn_addr, conn_req = select_host(selected)    
    # st.info(f'api_key {api_key}  conn_addr {conn_addr}  conn_req {conn_req}')
        
    uploaded_file = st.file_uploader(
        "",
        type="npy",
        key="1",
        help="To activate 'wide mode', go to the menu > Settings > turn on 'wide mode'",
    )
    if uploaded_file is not None:
        content = uploaded_file.read()
        encoded_string = base64.b64encode(content).decode("utf-8")
        request_dict = {"input_params":encoded_string}
        payload = '{"input_params":' + json.dumps(request_dict) + "}"
        headers = {
            'Cnvrg-Api-Key': api_key,
            'Content-Type': "application/json"
            }
    if uploaded_file is not None:
        file_container = st.expander("Check your uploaded .csv")
        conn = http.client.HTTPSConnection(conn_addr)
        st.info('Sending File to the server')
        conn.request("POST", conn_req, payload, headers)
        st.info('Got server POST response')
        res = conn.getresponse()
        data = res.read()
        output = data.decode("utf-8")
       # st.info(f'data from server: {output}')
        if type(output) != str:
            print("Results in empty")
            st.info('Result is empty')
            gender="Error"
            prob_perc="Error"
            mortality_chance="Error"
            Cardiac_ejection="Error"
        else:
            gender = re.sub(r'.*\":\[\"(.*le)\"\,.*',r'\1', output)
            prob = re.sub(r'.*le\"\,(0.\d{3}).*',r'\1', output)
            prob_perc = float(prob)*100       
            mortality_chance=re.sub(r'.*chance\"\,(0.\d{3}).*',r'\1', output)
            mortality_chance_perc=float(mortality_chance)*100
            cardiac_ejection=re.sub(r'.*fraction\"\,(0.\d{3}).*',r'\1', output)
            cardiac_ejection_perc=float(cardiac_ejection)*100
        st.info(f'No mortality chance: {mortality_chance_perc}% \n
                Cardiac ejective fraction: {cardiac_ejection_perc}% \n
                Gender: {gender} Confidence: {prob_perc}% ')
    else:
        st.info(
            f"""
                👆 Upload a .npy ECG file first.)
                """
        )
        st.stop()

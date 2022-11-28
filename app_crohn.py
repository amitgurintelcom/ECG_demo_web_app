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
is_exception_raised = False
output = None

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
    
st.set_page_config(page_icon="✂️", page_title="Crohn's Treatment Outcome Prediction", layout="wide")

with st.sidebar:
        selected = option_menu(
            menu_title="Choose web host",  # required
            options=["AWS", "Intel DevCloud (Future)", "Azure (Future)"],  # required
            icons=["snow2", "bank2", "microsoft"],  # optional
            menu_icon="heart-pulse",  # optional
            default_index=0,  # optional
                )
        st.info(f'web host is {selected}', icon="ℹ️")

c1_1, c1_2, _, _ = st.columns([3.5, 8, 8, 8])
with c1_1:
    st.image('./intel.png', width=100)
with c1_2:
    st.subheader('Developer Cloud')

c1, c2 = st.columns([5,5])
with c1:
    st.title("Crohn's Treatment Outcome Prediction")
    st.write('''
    Capsule endoscopy (CE) is a prime modality for diagnosing and monitoring Crohn's disease (CD). 
    However, CE's video wasn't utilized for predicting the success of biologic therapy.
    This demo runs the Timesformer model trained on Sheba data by Intel's New AI technologies group.
    The model reaches a 20% improvement over the best existing biomarker (fecal calprotectin) while providing decision explainability and confidence level
    ''')
    st.image('CE_basic.jpg', width=200)
    st.image('footer.png')

with c2:
    api_key, conn_addr, conn_req = select_host(selected)
    uploaded_file = st.file_uploader("", type="npy", key="1")
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
        with st.spinner('This might take few seconds ... '):
            try:
                conn = http.client.HTTPSConnection(conn_addr)
                st.info('Sending File to the server')
                conn.request("POST", conn_req, payload, headers)
                st.info('Got server POST response')
                res = conn.getresponse()
                data = res.read()
                output = data.decode("utf-8")
            except: 
                st.error('Cant connect to server. Try to disable VPN!')
                is_exception_raised = True
                output = None

    if not is_exception_raised and output is not None:
        gender = re.sub(r'.*\":\[\"(.*le)\"\,.*',r'\1', output)
        prob = re.sub(r'.*le\"\,(0.\d{3}).*',r'\1', output)
        prob_perc = float(prob)*100       
        mortality_chance=re.sub(r'.*chance\"\,(0.\d{3}).*',r'\1', output)
        mortality_chance_perc=float(mortality_chance)*100
        cardiac_ejection=re.sub(r'.*fraction\"\,(0.\d{3}).*',r'\1', output)
        cardiac_ejection_perc=float(cardiac_ejection)*100

        st.metric(label="Non-normal cardiac ejection fraction probability", value=f"{mortality_chance_perc}%")
        st.metric(label=f'Cardiac ejection fraction', value=f"{cardiac_ejection_perc}%")
        st.metric(label=f'Gender', value=f"{gender}")
        st.metric(label=f'Gender Confidence', value=f"{prob_perc}%")
    else:
        st.info(f"""👆 Please upload a .npy ECG file first""")
        st.stop()

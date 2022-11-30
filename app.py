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


import base64

@st.cache(allow_output_mutation=True)
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_in_footer(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img ="""<style>
    .footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: white;
color: black;
text-align: center;
}
</style>
<div class="footer">
<img src=url("data:image/png;base64,{%s}") alt="0" style="width: 90px">
</div>
"""

    st.markdown(page_bg_img, unsafe_allow_html=True)
    return

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

def present_ecg_image(content):
    st.image('ecg.gif', width=200, caption='ECG image goes here')
    
st.set_page_config(page_icon="✂️", page_title="ECG Prediction", layout="wide")

with st.sidebar:
    st.image('./intel.png', width=90)
    st.subheader('Developer Cloud')
    st.image("footer.png")
    st.write("")
    st.write("")
    selected = option_menu(
        menu_title="Choose web host",  # required
        options=["AWS", "Intel DevCloud", "Azure (Future)"],  # required
        icons=["snow2", "bank2", "microsoft"],  # optional
        menu_icon="heart-pulse",  # optional
        default_index=0,  # optional
            )
    st.info(f'web host is {selected}', icon="ℹ️")


st.title("ECG Prediction")


st.write('''ECG is an old technology, cheap, and readily available, hence a great use case for large scale training on non-standard data.
        The ability to predict diseases as well as age and gender, allows physicians to quickly and erroneously provide robust results
        to their patients. This demo runs the ViT model trained on masses of labeled ECG signals from Sheba. 
        We reached 98% accuracy, 2x over state of the art.''')


#set_png_in_footer('footer.png')

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
    present_ecg_image(content)
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

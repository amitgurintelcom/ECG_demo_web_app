import streamlit as st
from streamlit_option_menu import option_menu
import http.client
import base64
import json
import re
import os
from datetime import datetime
###################################
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import JsCode
import numpy as np
from PIL import Image
from scipy import signal
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


def signal_preprocess(ecg_npy):
    # load ecg numpy file and remove extra dimension
    ecg_npy = np.squeeze(ecg_npy, axis=0)

    # upsample if necessary
    if ecg_npy.shape[0] == 2500:
        ecg_npy = signal.resample(ecg_npy, 5000)

    # try normalizing to local min/max as npy contains negative values
    a_min = np.min(ecg_npy)
    a_max = np.max(ecg_npy)
    ecg_npy = ((ecg_npy - a_min) * (1 / (a_max - a_min)) * 255).astype('uint8')

    combo_npy = np.zeros(50176).reshape(224, 224)

    #for i in range(0, 22):
    for i in range(0, 18): # need to ignore first frames
        from_pixels=i*224
        to_pixels=(i+1)*224
        slice_npy = ecg_npy[from_pixels:to_pixels, :]

        from_dest = i*12
        to_dest = (i + 1)*12
        combo_npy[:, from_dest:to_dest] = slice_npy

    ecg_img = Image.fromarray(combo_npy)  # convert numpy array to image
    ecg_img = ecg_img.convert(mode="RGB")

    return ecg_img

def present_ecg_image(content):
    date = datetime.now().strftime("%Y_%m_%d-%I:%M:%S")
    temp_name = "temp_" + date + ".npy"
    with open(temp_name, "wb") as file_o:
        numpy_img = file_o.write(base64.b64decode(content))
    
    numpy_img = np.load(temp_name, allow_pickle=True)

    image = signal_preprocess(numpy_img)
    st.image(image, width=200, caption='Uploaded ECG image')
    
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

c_1, _, c_2 = st.columns([1,1,5])
with c_1:
    st.image('ecg.gif', width=200)
with c_2:
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

    c1, c2, c3 = st.columns([5,4,4])
    with c1:
        present_ecg_image(encoded_string)
    with c2:
        st.metric(label="Non-normal cardiac ejection fraction probability", value=f"{mortality_chance_perc}%")
        st.metric(label=f'Cardiac ejection fraction', value=f"{cardiac_ejection_perc}%")
    with c3:
        st.metric(label=f'Gender', value=f"{gender}")
        st.metric(label=f'Gender Confidence', value=f"{prob_perc}%")
else:
    st.info(f"""👆 Please upload a .npy ECG file first""")
    st.stop()

# Pablo Sagrera / Efrain Gonzalez

import streamlit as st
import pickle
import pandas as pd
from sklearn import preprocessing
import numpy as np
import plotly.express as px
html = """
  <style>
    .reportview-container {
      flex-direction: row-reverse;
    }

    header > .toolbar {
      flex-direction: row-reverse;
      left: 1rem;
      right: auto;
    }

    .sidebar .sidebar-collapse-control,
    .sidebar.--collapsed .sidebar-collapse-control {
      left: auto;
      right: 0.5rem;
    }

    .sidebar .sidebar-content {
      transition: margin-right .5s, box-shadow .5s;
    }

    .sidebar.--collapsed .sidebar-content {
      margin-left: auto;
      margin-right: -50rem;
    }

    @media (max-width: 1200.98px) {
      .sidebar .sidebar-content {
        margin-left: auto;
      }
    }
  </style>
"""
st.markdown(html, unsafe_allow_html=True)


st.write("""
## App de modelizacion del consumo de recursos del equipamiento de red de un ISP
#### ***Developed by: Efrain Gonzalez y Pablo Sagrera***
""")

st.sidebar.header('User Input Parameters:')

def user_input_features():
    
    ifd_count = st.sidebar.slider('IFD', 100, 900, 150)                                 
    ifl_count =  st.sidebar.slider('IFL', 70, 32000, 100)                                 
    protocols_igmp_groups_count = st.sidebar.slider('IGMP groups', 0, 4000, 100)                 
    protocols_instances_vpls_count = st.sidebar.slider('VPLS instances', 1, 3000, 100)             
    protocols_instances_vrf_count  = st.sidebar.slider('VRF instances', 1, 4000, 100)              
    protocols_isis_adjacency_count = st.sidebar.slider('ISIS adyancency', 1, 20, 1)             
    protocols_l2circuit_count  = st.sidebar.slider('L2circuit', 0, 100, 5)                
    protocols_ldp_session_count  = st.sidebar.slider('LDP session', 1, 80, 10)               
    protocols_lsi_count = st.sidebar.slider('LSI number', 5, 3000, 100)                        
    protocols_rsvp_session_count = st.sidebar.slider('RSVP session', 0, 120, 10)               
    route_table_summary_inet_0_BGP = st.sidebar.slider('BGP routes inet', 25000, 350000, 26000)             
    route_table_summary_inet_0_access_internal = st.sidebar.slider('access internal routes inet', 0, 25000, 100) 
    route_table_summary_inet_0_isis = st.sidebar.slider('ISIS routes', 70, 800, 80)             
    route_table_summary_inet_0_ldp = st.sidebar.slider('LDP routes inet ', 0, 1, 1)               
    route_table_summary_inet_0_static  = st.sidebar.slider('static routes inet ', 0, 50, 5)         
    route_table_summary_inet_3_BGP = st.sidebar.slider('BGP routes inet.3 ', 4000, 8000, 5000)            
    route_table_summary_inet_3_rsvp = st.sidebar.slider('RSVP routes inet.3 ', 0, 20, 5)                 

    

    data = {'ifd_count': ifd_count,
            'ifl_count': ifl_count,
            'protocols_igmp_groups_count': protocols_igmp_groups_count,
            'protocols_instances_vpls_count': protocols_instances_vpls_count,
            'protocols_instances_vrf_count': protocols_instances_vrf_count,
            'protocols_isis_adjacency_count':protocols_isis_adjacency_count,
            'protocols_l2circuit_count':protocols_l2circuit_count,
            'protocols_ldp_session_count':protocols_ldp_session_count,
            'protocols_lsi_count':protocols_lsi_count,
            'protocols_rsvp_session_count':protocols_rsvp_session_count,
            'route_table_summary_inet_0_BGP':route_table_summary_inet_0_BGP,
            'route_table_summary_inet_0_access_internal':route_table_summary_inet_0_access_internal,
            'route_table_summary_inet_0_isis':route_table_summary_inet_0_isis,
            'route_table_summary_inet_0_ldp':route_table_summary_inet_0_ldp,
            'route_table_summary_inet_0_static':route_table_summary_inet_0_static,
            'route_table_summary_inet_3_BGP':route_table_summary_inet_3_BGP,
            'route_table_summary_inet_3_rsvp':route_table_summary_inet_3_rsvp}
    features = pd.DataFrame(data, index=[0])
    return features


def load_model():
    filename = 'modelo_final.sav'
    loaded_model = pickle.load(open(filename, 'rb'))
    prediction = loaded_model.predict(df)
    df_predict = pd.DataFrame(data=prediction, columns=["Composite", "EDMEM","IDMEM","Indirect","Label","Unicast","Unilist","free-filter-memory","free-heap-memory","free-nh-memory-rsmon-percent","memory-buffer-utilization","memory-heap-utilization","nhdb","task.memory","RE_memory-buffer-utilization"])
    return df_predict

def load_model_class():
    filename = 'modelo_final_class.sav'
    loaded_model_class = pickle.load(open(filename, 'rb'))
    prediction_class = loaded_model_class.predict_proba(df)
    df_predict_class = pd.DataFrame(data=prediction_class, columns=["Carga Alta", "Carga Media","Carga Media-alta","Carga Baja"])
    return df_predict_class


df = user_input_features()

st.subheader('User Input parameters:')
st.write(df)


model_prediction = load_model()
x_values = model_prediction.values


df_predichas = pd.DataFrame(x_values,columns=load_model().columns)

row = df_predichas.iloc[0]

## TODO: div by 1M task_memory
x_value_reshape = np.reshape(x_values,(15,1))
st.subheader('Prediction:')
df_table = pd.DataFrame(x_value_reshape,index=load_model().columns,columns=["Value"])
st.write(df_table)

st.subheader('Graph:')
st.bar_chart(row[["Composite", "EDMEM","IDMEM","Indirect","Label","Unicast","Unilist","free-filter-memory","free-heap-memory","free-nh-memory-rsmon-percent","memory-buffer-utilization","memory-heap-utilization","nhdb","RE_memory-buffer-utilization"]])

st.subheader('Group:')
st.write(load_model_class())



import streamlit as st
from streamlit import caching

# Data-analytics Dependencies
import pandas as pd 
import numpy as np
from covid import Covid

# Os Dependencies
import datetime
from pathlib import Path
import base64
import re



def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded




def world_data(choropleth, total_numericals, worldTime_dict): 

    st.markdown('***')
    st.markdown('''<h3 style='font-family:poppins; text-align:center;'>The World's Data Visualised</h3>''',unsafe_allow_html=True)
    st.markdown('***')

    titleslt = st.empty() # for title
    st.markdown(' ')
    slot = st.empty() # predefined slot for choropleth chart


    viztype = st.sidebar.radio('Illustrations',['Choropleth (World Map)', 'Quantified Summary', 'Daily Reported Cases'], key='viztype')

    st.sidebar.markdown('***')
    st.sidebar.header('Global Statistics 📈')
    st.sidebar.markdown(' ') # section break
    

    # Global Status
    table='''

        *Confirmed* -  ```{:,}```\n
        *Recovered* -  ```{:,}```\n
        *Deaths*$~~~~~$ - ```{:,}```\n
        *Active*$~~~~~~$ - ```{:,}```\n
    '''.format(total_numericals['Total Confirmmed'],total_numericals['Total Active'],total_numericals['Total Deaths'],total_numericals['Total Recovered'])

    
    st.sidebar.write(table)
    st.sidebar.markdown('***')



    if viztype == 'Choropleth (World Map)':

    
        cols = st.beta_columns(4)
        attr = st.selectbox('Category',['Active','Recovered','Confirmed','Deaths'], key='choropleth')
        titleslt.markdown('''<h4 style='font-family:poppins; font-style:italic; text-align:center;'>Choropleth (World Map) - {}</h4>'''.format(attr),unsafe_allow_html=True)
        

        if attr == 'Active':
            fig = choropleth[attr]
            slot.plotly_chart(fig, use_container_width=True)
        elif attr == 'Confirmed':
            fig = choropleth[attr]
            slot.plotly_chart(fig,use_container_width=True)
        elif attr == 'Recovered':
            fig = choropleth[attr]
            slot.plotly_chart(fig,use_container_width=True)
        elif attr == 'Deaths':
            fig = choropleth[attr]
            slot.plotly_chart(fig,use_container_width=True)

        st.markdown('***')

    elif viztype == 'Quantified Summary':

        chart_title = st.empty()
        chartslt = st.empty() 
        Global_Chart_radio = st.selectbox('Visualization type', ['Pie chart', 'Time Series'], key='3')
        st.sidebar.markdown('***')

        
        if Global_Chart_radio == 'Time Series':
            chart_title.markdown('''<h3 style='font-family:poppins; font-style:italic; text-align:center;'>Time Series Plot</h3>''',unsafe_allow_html=True)
            chartslt.plotly_chart(worldTime_dict['Time Series'])
        else:
            
            chart_title.markdown('''<h3 style='font-family:poppins; font-style:italic; text-align:center;'>Quantified Summary</h3>''',unsafe_allow_html=True)
            chartslt.plotly_chart(worldTime_dict['World-Pie'])
    
    else:

        # frequency 
        freq_chart, information = worldTime_dict['Frequency']

        st.markdown('***')
        st.markdown('''<h3 style='font-family:poppins; font-style:italic; text-align:center;'>Frequency of reported Cases</h3>''',unsafe_allow_html=True)

        st.plotly_chart(freq_chart)
        st.info(information)

        
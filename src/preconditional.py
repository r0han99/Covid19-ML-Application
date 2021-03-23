# Application Front-End dependencies 
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

covid = Covid() # API Instantiation

# Image-Rendenring Dependecy Subroutine
def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded

# For contemporary Stats
@st.cache(persist=True)
def covidAPI_data(CountryName):
   
    while True:
        try:
            country = CountryName
            data = covid.get_status_by_country_name(country)

        except ValueError:
            
            continue
        
        else:
            data = covid.get_status_by_country_name(country)

        break

    country_dict = {
        key : data[key]


        for key in data.keys() & ("confirmed","active","deaths","recovered")
    }


    key = list(country_dict.keys())
    values = list(map(int,country_dict.values()))

    return country_dict


@st.cache(persist=True)
def covidAPI_data_total():

    
    active_tot = int(covid.get_total_active_cases())
    recovered_tot = int(covid.get_total_recovered())
    confirmed_tot = int(covid.get_total_confirmed_cases())


    total_numericals = dict({'Total Recovered' : recovered_tot, 'Total Active' : active_tot,'Total Deaths' : abs((active_tot+recovered_tot) - confirmed_tot), 'Total Confirmmed': confirmed_tot,})

    return total_numericals


@st.cache(persist=True)
def covidAPI_country_list():

    countries = list(covid.list_countries())
    countries_list = list()

    countries_list = [list(dict(countries[x]).values())[1] for x in range(len(countries))]
    
    return countries_list

def footer():
    st.sidebar.markdown('***')
    expander0 = st.sidebar.beta_expander(label='GitHub')
    expander0.markdown('''[<img src='data:image/png;base64,{}' class='img-fluid' width=32 height=32>](https://github.com/r0han99/Covid19-PredictiveAnalysis) <small>Source-Code | Oct 2020</small>'''.format(img_to_bytes("./assets/GitHub.png")), unsafe_allow_html=True)
    expander0.markdown('''[<img src='data:image/png;base64,{}' class='img-fluid' width=32 height=32>](https://github.com/r0han99/) <small>The Database of My Knowledge</small>'''.format(img_to_bytes("./assets/cognitive-intel.png")), unsafe_allow_html=True)




def app():

    motive = '''Analysis of the preconditional traits of a patient and determining the efficiency of virus'''
    st.markdown('***')
    st.markdown('''<h2 style='font-family:poppins; text-align:center;'>Pre-Conditional Prognosis</h2>''',unsafe_allow_html=True)
    st.markdown('''<small style='font-size:14px; text-align:center; padding-left:30px;'>{}</small>'''.format(motive),unsafe_allow_html=True)
    st.markdown('***')



    # World Status
    # API Invocation
    total_numericals = covidAPI_data_total()

    if st.sidebar.checkbox('world stats',True):
        st.sidebar.header('Global Statistics📈')
    st.sidebar.markdown(' ') # section break

    # Global Status
    table='''

        **Confirmed** -  ```{:,}```\n
        **Recovered** -  ```{:,}```\n
        **Deaths**$~~~~~$ - ```{:,}```\n
        **Active**$~~~~~$ - ```{:,}```\n
    '''.format(total_numericals['Total Confirmmed'],total_numericals['Total Active'],total_numericals['Total Deaths'],total_numericals['Total Recovered'])

    st.sidebar.write(table)
    st.sidebar.markdown('***')

    # Preset for all the Plots
    plot_template = st.sidebar.selectbox('Default Plot Theme',['Light☀️','Dark🌑'],key='VizThemeTemplate')

    if plot_template == 'Dark🌑':
        theme = 'plotly_dark'
    else:
        theme = 'plotly_white'

    st.sidebar.markdown('***')


    # footer-sidebar
    footer()
   

    

    
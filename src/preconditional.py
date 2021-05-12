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





def precondition():

    motive = '''Analytical Categorization based on Historic Covid19 Patients preconditional Data'''
    st.markdown('***')
    st.markdown('''<h2 style='font-family:poppins; text-align:center; font-weight:normal;'>Pre-Conditional Prognosis</h2>''',unsafe_allow_html=True)
    st.markdown('''<p style='font-size:14px; color:crimson; text-align:center;'>{}</p>'''.format(motive),unsafe_allow_html=True)
    st.markdown('***')

    st.info('Data Preprocessing ⌛️, Neural Network Training ⏳, Algorithm for categorization⏳')

    
    
   

    

    
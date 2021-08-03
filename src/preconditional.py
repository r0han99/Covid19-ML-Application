# Application Front-End dependencies 
import streamlit as st
from streamlit import caching

# results 
from src.results import display_results

# Data-analytics Dependencies
import pandas as pd 
import numpy as np
from covid import Covid

# Os Dependencies
import datetime
from pathlib import Path
import base64
import time
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

    st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        width: 800px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 500px;
        margin-left: -500px;
    }
    </style>
    """,
    unsafe_allow_html=True,
    )



    motive = '''Analytical Categorization based on records of COVID19 Patients & their Pre-conditions'''
    st.markdown('***')
    st.markdown('''<h2 style='font-family:sora; text-align:center; font-weight:normal;'>Pre-Conditional Prognosis</h2>''',unsafe_allow_html=True)
    st.markdown('''<p style='font-size:14px; color:#2484F7; text-align:center; font-style:italic;'>{}</p>'''.format(motive),unsafe_allow_html=True)
    st.markdown('***')

    # st.markdown('''<h3 style='font-family:Sora; text-align:center; font-weight:Extra-bold;'>Know Your Prognosis</h3>''',unsafe_allow_html=True)
    # st.markdown('***')
    # st.info('Data Preprocessing ⌛️, Neural Network Training ⏳, Algorithm for categorization⏳')

    help_info = {
            
            'tobacco' : 'Select ***Yes***, if you consider yourself to consume *Tobacco* on a regular basis, Else ***No***',
            'pneumonia' : '''Are you diagnosed with ***Infectious Pneumonia***?''',
            'pregnancy' : '''Are you currently ***Pregnant***?''',
            'diabetes' : '''Are you diagnosed with ***Diabetes***?''',
            'copd' : '''Any *historic* or *present*, positive diagnosis for ***COPD (Chronic obstructive pulmonary Dieseases)***?''',
            'asthma' : '''Are you ***Asthematic***?''',
            'inmsupr' : '''*Yes*, if you are ***Immunocompromised*** as a result of any *Medical Conditions*, Else, *No*''',
            'hypertension': '''Are you diagnosed with ***Hypertension***?''',
            'obesity' : '''''',
            'cardiovascular' : '''Any historic conditions or diagnosis relating to ***Cardiovascular Diseases***?''',
            'renal_chronic' : '''Are you diagnosed with ***Chronic Renal Infections***?''',
            'covid_res' : "***Positive*** : Positive for *COVID19*, ***Negative*** : Negative for *COVID19*, ***Awaiting/Not Taken***: Undergone Test for *COVID19* Diagnosis, Awaiting Results or Didn't take it."

    }

    fcols = ['sex', 'pneumonia', 'age', 'pregnancy', 'diabetes', 'copd', 'asthma',
       'inmsupr', 'hypertension', 'cardiovascular', 'obesity', 'renal_chronic',
       'tobacco']

    formexp = st.sidebar.beta_expander('Precondition survey',expanded=True)
    container = st.beta_container()

    with formexp.form("Form"):
        st.write("***Survey***")
        patient = st.text_input('Name', value="Nicholas Gonzalez", help='*First-Name* *Last-Name*(optional)')
        age = st.number_input('Age',min_value=10,max_value=100,step=1)

        st.markdown('***Preconditions***')
        cols = st.beta_columns(2)

        sex = cols[0].selectbox('Gender',['Male','Female'],key='tobacco')
        pregnancy = cols[1].selectbox('Pregnancy',['No','Yes'],key='pregnancy',help=help_info['pregnancy'])

        pneumonia = cols[0].selectbox('Pneumonia',['Yes','No'],key='pneumonia',help=help_info['pneumonia'])
        copd = cols[1].selectbox('COPD',['No','Yes'],key='copd',help=help_info['copd'])

    
        diabetes = cols[0].selectbox('Diabetes',['No','Yes'],key='Diabetes',help=help_info['diabetes'])
        obesity = cols[1].selectbox('Obesity', ['No','Yes'],key='obesity',help=help_info['obesity'])

        cardiovascular = cols[0].selectbox('Cardiovascular',['No','Yes'],key='cardiovascular',help=help_info['cardiovascular'])
        hypertension = cols[1].selectbox('Hypertension', ['No','Yes'],key='hypertension',help=help_info['hypertension'])
        
        inmsupr = cols[0].selectbox('Immunocompromise',['No','Yes'],key='inmsupr',help=help_info['inmsupr'])
        renal_chronic = cols[1].selectbox('Chronic Renal Infections',['No','Yes'],key='chronic_renal',help=help_info['renal_chronic'])

        asthma = cols[0].selectbox('Asthma',['No','Yes'],key='asthma',help=help_info['asthma'])
        tobacco = cols[1].selectbox('Tobacco usage',['No','Yes'],key='tobacco',help=help_info['tobacco'])

        st.markdown('***Covid-19-Diagnosis***')
        covid_res = st.selectbox('Are you tested for COVID19',['Positive','Negative','Awaiting/Not Tested'], key='covid_res',help=help_info['covid_res'])
       
        st.markdown(' ')
        submitted = st.form_submit_button("submit")
        # Every form must have a submit button.
        
        
        


    if submitted:

        
        st.markdown(
            """
            <style>
            [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
                width: 450px;
            }
            [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
                width: 500px;
                margin-left: -500px;
            }
            </style>
            """,
            unsafe_allow_html=True)
            

        
        package = {'Name': patient,'Age':age,'Sex': sex, 'Covid-Result': covid_res, 'Pneumonia': pneumonia, 'Pregnancy': pregnancy, 'Diabetes':diabetes,  'COPD':copd, 'Asthma': asthma, 'Immunocompromise': inmsupr, 'Hypertension': hypertension,'Cardiovascular': cardiovascular,  'Obesity':obesity,  'Chronic Renal': renal_chronic,  'Tobacco': tobacco}
        
        display_results(package)


    

    



    
    
   

    

    

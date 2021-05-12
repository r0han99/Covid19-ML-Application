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


def countryViz(CountryName, MR, quantsum, freq, timeline):


    
    
    st.sidebar.markdown('''<p>Selected Country is : <span style='font-style:italic; font-weight:bold; color:dodgerblue;'>{}<span>   <img src='data:image/png;base64,{}' class='img-fluid' width=24 height=24></p>'''.format(CountryName, img_to_bytes("./assets/Countries/{}.png".format(CountryName.lower()))), unsafe_allow_html=True)



    stats = st.sidebar.radio('Categories',['Mortality & Recovery', 'Quantified Summary', 'Daily Frequency', 'Timeline'], key='cateogories_country')
    st.sidebar.markdown('***')    


    if stats == 'Mortality & Recovery':
        if not CountryName == 'US':


            st.markdown('***')
            st.markdown('''<h3 style='font-family:poppins; font-style:italic; text-align:center;'>Mortality Rate and Recovery Rate, Percentiles</h3>''',unsafe_allow_html=True)
            st.markdown(' ')



            # ACCESS Mortality and Recovery 

            present_date, mortality_rate, recovery_rate = MR.values()

            # ACCESS Mortality and Recovery 


            spaces = '~~~~~~~~~~~~~~'
            st.markdown('${}$ **{}**, Recovery Rate as of Date (**{}**) : ```{:.2f}%```'.format(spaces,CountryName,present_date,recovery_rate*100))
            st.markdown('${}$ **{}**, Fatality Rate as of Date (**{}**)  : ```{:.2f}%```'.format(spaces,CountryName,present_date,mortality_rate*100))


            st.success('_**Recovery Rate**_ is the proportion of people who **Recovered** from the `Diesease` to the Total Number of people infected.')
            st.error('_**Mortality Rate**_ is the proportion of people who **Died** from the `Disease` to the Total Number of people infected.')
            st.markdown('***')
    
    
    elif stats == 'Quantified Summary':

        st.markdown('***')
        st.markdown('''<h3 style='font-family:poppins; font-style:italic; text-align:center;'>Quantified Summary - {} </h3>'''.format(CountryName),unsafe_allow_html=True)
        st.markdown(' ')
        CHART_TYPE0 = st.selectbox('Visualization type',['Pie Chart','Bar Chart'], key='ix')

        if CHART_TYPE0 == 'Pie Chart':
            fig = quantsum['Piechart']
            st.plotly_chart(fig)
        else:
            fig = quantsum['Barchart']
            st.plotly_chart(fig)
        
        st.markdown('***')


    elif stats == 'Daily Frequency':
    
        st.markdown('***')
        st.markdown('''<h3 style='font-family:poppins; font-style:italic; text-align:center;'>Quantified Daily Frequency of Cases - {} </h3>'''.format(CountryName),unsafe_allow_html=True)
        

        freqchart = freq['FreqChart']
        st.plotly_chart(freqchart)


        net_increase, last2dates, country_raise = freq['info']

        st.info('The Net Hike in Cases Between _Last Two Days_ in **{}** `&` **{}** in {} is : **{:,}**'.format(last2dates[0],last2dates[1],CountryName,country_raise))
        if st.checkbox('Note',(country_raise==0)):
            st.markdown('If this Value is ever `zero`, that means there are same number of cases reported in the last two dates, So, there is no Net Increase in Cases. However, I feel the Value `Zero` is very unlikely, So I believe it to be either **Artificiality** in the Dataset or The Data is **Not Updated** yet.')

        st.markdown('***')
    
    elif stats == 'Timeline':
        
        
        st.markdown('***')
        st.markdown('''<h3 style='font-family:poppins; font-style:italic; text-align:center;'>Time Series Plot - {}</h3>'''.format(CountryName),unsafe_allow_html=True)
        

        # retrieve Chart 
        fig = timeline
        st.plotly_chart(fig)


        if st.checkbox('Intriguing?',False):
            st.info('_I felt, the following list of countries had some **Intriguing patterns** in Time Series Plot, While the application was in the testing Phase.Why Intriguing you might ask, from the plot you can clearly see the contrast between people of different regions, reacting to the same contagion.Up Next in the Subplots Section you are enabled to choose any other 3 countries to contrast with the initial one._')
        
            # st.sidebar.markdown
            intriguing_countries = ['Ecuador','Brazil','US','China','Canada','Spain']
            st.code(intriguing_countries)

        st.markdown('***')
        
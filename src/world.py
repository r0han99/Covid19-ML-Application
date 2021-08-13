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




def world_data(choropleth, total_numericals, worldTime_dict, MR): 

    st.markdown('***')
    st.markdown('''<h3 style='font-family:Sora; text-align:center;'>The World's Data Visualised</h3>''',unsafe_allow_html=True)
    st.markdown('***')

    titleslt = st.empty() # for title
    st.markdown(' ')
    slot = st.empty() # predefined slot for choropleth chart


    viztype = st.sidebar.radio('Illustrations',['Choropleth (World Map)', 'Quantified Summary',"World's Mortality & Recovery",'Daily Reported Cases'], key='viztype')

    st.sidebar.markdown('***')
    st.sidebar.header('Global Statistics 📈')
    st.sidebar.markdown(' ') # section break
    

    # Global Status
    table='''

        *Confirmed* -  <span style='font-family:Sora; color:#2484F7;'>{:,}</span>\n
        *Recovered* -  <span style='font-family:Sora; color:#2484F7;'>{:,} </span><small style='font-size:15px;'><i>until 4th Aug, 21</i></small>\n
        *Deaths*$~~~~~$ - <span style='font-family:Sora; color:#2484F7;'>{:,}</span>\n
        *Active*$~~~~~~$ - <span style='font-family:Sora; color:#2484F7;'>{:,}</span><small style='font-size:15px;'><i> until 4th Aug, 21</i></small>\n
    '''.format(total_numericals['Total Confirmmed'],total_numericals['Total Active'],total_numericals['Total Deaths'],total_numericals['Total Recovered'])

    
    st.sidebar.markdown(table,  unsafe_allow_html=True)
    

    
    st.sidebar.markdown('***')



    if viztype == 'Choropleth (World Map)':

    
        cols = st.beta_columns(4)
        attr = st.selectbox('Category',['Confirmed','Deaths'], key='choropleth')
        titleslt.markdown('''<h4 style='font-family:Sora;  text-align:center;'>Choropleth (World Map)</h4>''',unsafe_allow_html=True)
        

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


    elif viztype == "World's Mortality & Recovery":

        
        st.markdown('''<h3 style='font-family:Sora;  text-align:center;'>Mortality Rate and Recovery Rate, Percentiles</h3>''',unsafe_allow_html=True)
        st.markdown('<br>',unsafe_allow_html=True)
    


        # ACCESS Mortality and Recovery 

        present_date, mortality_rate, recovery_rate, mrchart = MR.values()

        # ACCESS Mortality and Recovery 


        st.markdown('''<p style='text-align:center;'><b>{}'s</b> Recovery Rate : <span style='color:limegreen; font-weight:bold;'>{:.2f}%</span></span><small style='font-size:15px;'><i> until 4th Aug, 21</i></small></p>'''.format("World",recovery_rate*100),unsafe_allow_html=True)
        st.markdown('''<p style='text-align:center;'><b>{}'s</b> Mortality Rate as of Date <span style='font-weight:bold; font-family:Sora; '>({})</span> : <span style='color:crimson; font-weight:bold;'>{:.2f}%</span></p>'''.format("World",present_date,mortality_rate*100),unsafe_allow_html=True)
        
        st.success('_**Recovery Rate**_ is the proportion of people who **Recovered** from the `diesease` to the total Number of people infected.')
        st.error('_**Mortality Rate**_ is the proportion of people who **Succumbed** to the `disease` to the total Number of people infected.')
        st.markdown("| <small style='font-size:15px;text-align:center;'><i>Recovered and Active Cases represent reports recorded until 4th Aug, 21 (read deprecation notice)</i></small></h3>",unsafe_allow_html=True)
        st.markdown('***')

        st.markdown('''<h3 style='font-family:Sora;  text-align:center;'>Mortality Rate and Recovery Rate, Timeline</h3>''',unsafe_allow_html=True)
        st.markdown(' ')

        st.plotly_chart(mrchart,use_container_width=True)


        

    elif viztype == 'Quantified Summary':

        chart_title = st.empty()
        chartslt = st.empty() 
        Global_Chart_radio = st.selectbox('Visualization type', ['Pie chart', 'Time Series'], key='3')
        st.sidebar.markdown('***')

        
        if Global_Chart_radio == 'Time Series':
            chart_title.markdown('''<h3 style='font-family:Sora;  text-align:center;'>Time Series Plot</h3>''',unsafe_allow_html=True)
            chartslt.plotly_chart(worldTime_dict['Time Series'])
        else:
            st.markdown('''''',unsafe_allow_html=True)
            chart_title.markdown('''<h3 style='font-family:Sora;  text-align:center;'>Quantified Summary''',unsafe_allow_html=True)
            chartslt.plotly_chart(worldTime_dict['World-Pie'])

            st.markdown("| <small style='font-size:15px;text-align:center;'><i>Recovered and Active Cases represent reports recorded until 4th Aug, 21 (read deprecation notice)</i></small></h3>",unsafe_allow_html=True)
        
    
    else:

        # frequency 
        freq_chart, last2dates ,world_raise = worldTime_dict['Frequency']
        wconf_raise, wrecov_raise, wdeath_raise = world_raise


        st.markdown('''<h3 style='font-family:Sora;  text-align:center;'>Number of Cases Reported Daily</h3>''',unsafe_allow_html=True)
        
        st.plotly_chart(freq_chart)
        
        st.markdown('''<p style='font-family:Sora; font-weight:bold; font-size:25px; text-decoration:underline;'>Reported between the two dates, <span style='color:red; font-weight:bold;'>{} & {}</span></p>'''.format(last2dates[0], last2dates[1]),unsafe_allow_html=True)
        
        st.markdown('''> <p style='font-family:Sora; font-weight:bold; '><span style=''>Confirmed Cases</span> Reported  - {:,}</p>'''.format(wconf_raise),unsafe_allow_html=True)
        st.markdown('''> <p style='font-family:Sora; font-weight:bold; '><span style=''>Recovered Cases</span> Reported  - {:,}<small style='font-size:15px;'><i> until 4th Aug, 21</i></small></p>'''.format(wrecov_raise),unsafe_allow_html=True)
        st.markdown('''> <p style='font-family:Sora; font-weight:bold; '><span style=''>Deaths Cases</span> Reported  - {:,}</p>'''.format(wdeath_raise),unsafe_allow_html=True)

        st.markdown("| <small style='font-size:15px;text-align:center;'><i>Recovered and Active Cases represent reports recorded until 4th Aug, 21 (read deprecation notice)</i></small></h3>",unsafe_allow_html=True)
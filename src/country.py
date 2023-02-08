import streamlit as st

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


    try: 
        if not CountryName == 'US':
            st.sidebar.markdown('''<p>Selected Country is : <span style=' font-weight:bold; color:#2484F7;'>{}<span>   <img src='data:image/png;base64,{}' class='img-fluid' width=24 height=24></p>'''.format(CountryName, img_to_bytes("./assets/Countries/{}.png".format(CountryName.lower()))), unsafe_allow_html=True)

        else:
            st.sidebar.markdown('''<p>Selected Country is : <span style=' font-weight:bold; color:#2484F7;'>{}<span>   <img src='data:image/png;base64,{}' class='img-fluid' width=24 height=24></p>'''.format(CountryName, img_to_bytes("./assets/Countries/united states.png")), unsafe_allow_html=True)
    except:
        st.sidebar.markdown('''<p>Selected Country is : <span style=' font-weight:bold; color:#2484F7;'>{}<span></p>'''.format(CountryName), unsafe_allow_html=True)


    stats = st.sidebar.radio('Categories',['Daily Frequency', 'Mortality & Recovery', 'Quantified Summary', 'Timeline'], key='cateogories_country')
    st.sidebar.markdown('***')    


    if stats == 'Mortality & Recovery':
        if not CountryName == 'US':


            st.markdown('***')
            st.markdown('''<h3 style='font-family:Sora;  text-align:center;'>Mortality Rate and Recovery Rate, Percentiles</h3>''',unsafe_allow_html=True)
            st.markdown('<br>',unsafe_allow_html=True)
        


            # ACCESS Mortality and Recovery 

            present_date, mortality_rate, recovery_rate, mrchart = MR.values()

            # ACCESS Mortality and Recovery 


            st.markdown('''<p style='text-align:center;'><b>{}</b>, Recovery Rate : <span style='color:limegreen; font-weight:bold;'>{:.2f}%</span></span><small style='font-size:15px;'><i> until 4th Aug, 21</i></small></p>'''.format(CountryName,recovery_rate*100),unsafe_allow_html=True)
            st.markdown('''<p style='text-align:center;'><b>{}</b>, Mortality Rate as of Date <span style='font-weight:bold; font-family:Sora; '>({})</span> : <span style='color:crimson; font-weight:bold;'>{:.2f}%</span></p>'''.format(CountryName,present_date,mortality_rate*100),unsafe_allow_html=True)
           

            st.success('_**Recovery Rate**_ is the proportion of people who **Recovered** from the `diesease` to the total Number of people infected.')
            st.error('_**Mortality Rate**_ is the proportion of people who **Succumbed** to the `disease` to the total Number of people infected.')
            st.markdown("| <small style='font-size:15px;text-align:center;'><i>Recovered and Active Cases represent reports recorded until 4th Aug, 21 (read deprecation notice)</i></small></h3>",unsafe_allow_html=True)
            st.markdown('***')

            st.markdown('''<h3 style='font-family:Sora;  text-align:center;'>Mortality Rate and Recovery Rate, Timeline</h3>''',unsafe_allow_html=True)
            st.markdown(' ')

            st.plotly_chart(mrchart,use_container_width=True)

        else: 
            st.warning('_United States data records are probably corrupted and temporarily deprecated by the Covid19API due to inconsistency in the record maintenance._')


        st.markdown("| <small style='font-size:15px;text-align:center;'><i>Recovered and Active Cases represent reports recorded until 4th Aug, 21 (read deprecation notice)</i></small></h3>",unsafe_allow_html=True)
    
    
    elif stats == 'Quantified Summary':

        st.markdown('***')
        st.markdown('''<h3 style='font-family:Sora;  text-align:center;'>Quantified Summary - {} </h3>'''.format(CountryName),unsafe_allow_html=True)
        st.markdown(' ')
        CHART_TYPE0 = st.selectbox('Visualization type',['Pie Chart','Bar Chart'], key='ix')

        if not quantsum == None:

            if CHART_TYPE0 == 'Pie Chart':
                fig = quantsum['Piechart']
                st.plotly_chart(fig)
            else:
                fig = quantsum['Barchart']
                st.plotly_chart(fig)
            
            
        else:
            st.warning('_United States Data visualisation is temporarily deprecated by the CovidAPI due to inconsistency in the record maintenance_')

        st.markdown("| <small style='font-size:15px;text-align:center;'><i>Recovered and Active Cases represent reports recorded until 4th Aug, 21 (read deprecation notice)</i></small></h3>",unsafe_allow_html=True)


    elif stats == 'Daily Frequency':
    
        st.markdown('***')
        st.markdown('''<h3 style='font-family:Sora;  text-align:center;'>Number of Cases Reported Daily</h3>''',unsafe_allow_html=True)
        

        freqchart = freq['FreqChart']
        st.plotly_chart(freqchart)


        last2dates, country_raise, hike_status = freq['info']
        cconf_raise, crecov_raise, cdeath_raise = country_raise
        conf_status, recov_status, deaths_status = hike_status.values()

        last2dates1 = datetime.datetime.strptime(last2dates[1], '%m/%d/%y').strftime('%d/%m/%Y')
        last2dates0 = datetime.datetime.strptime(last2dates[0], '%m/%d/%y').strftime('%d/%m/%Y')
        st.markdown('''<p style='font-family:Sora; font-weight:bold; font-size:25px;'>Reported between the two dates, <span style='color:#2484F7; font-weight:bold;'><br>{} <span style="color:black;">&</span> {}</span></p>'''.format(last2dates0,last2dates1),unsafe_allow_html=True)

        st.markdown('''> <p style='font-family:Sora; font-weight:bold; '><span style=''>Confirmed Cases</span> Reported  - <span style='font-size:30px;'>{:,}</span> </span></p>'''.format(cconf_raise),unsafe_allow_html=True)
        st.markdown('''> <p style='font-family:Sora; font-weight:bold; '><span style=''>Recovered Cases</span> Reported  - <span style='font-size:30px;'>{:,}</span> </span><small style='font-size:15px;'><i>until 4th Aug, 21</i></small></p>'''.format(crecov_raise),unsafe_allow_html=True)
        st.markdown('''> <p style='font-family:Sora; font-weight:bold; '><span style=''>Deaths</span> Reported  - <span style='font-size:30px;'>{:,}</span> </span></p>'''.format(cdeath_raise),unsafe_allow_html=True)
        
        
        # if conf_status == 'positive':
        #     st.markdown('''> <p style='font-family:Sora; font-weight:bold; '><span style=''>Confirmed Cases</span> Reported  - {:,} <span> <img src='data:image/png;base64,{}' class='img-fluid' width=24 height=24></spam></p>'''.format(cconf_raise, img_to_bytes('./assets/hike/positive.png')),unsafe_allow_html=True)
        # elif conf_status == 'negative':
        #     st.markdown('''> <p style='font-family:Sora; font-weight:bold; '><span style=''>Confirmed Cases</span> Reported  - {:,} <span> <img src='data:image/png;base64,{}' class='img-fluid' width=24 height=24></spam></p>'''.format(cconf_raise, img_to_bytes('./assets/hike/negative.png')),unsafe_allow_html=True)

        # if recov_status == 'positive':
        #     st.markdown('''> <p style='font-family:Sora; font-weight:bold; '><span style=''>Recovered Cases</span> Reported  - {:,} <span> <img src='data:image/png;base64,{}' class='img-fluid' width=24 height=24></spam></p>'''.format(crecov_raise, img_to_bytes('./assets/hike/positive_r.png')),unsafe_allow_html=True)
        # elif recov_status == 'negative':
        #     st.markdown('''> <p style='font-family:Sora; font-weight:bold; '><span style=''>Recovered Cases</span> Reported  - {:,} <span> <img src='data:image/png;base64,{}' class='img-fluid' width=24 height=24></spam></p>'''.format(crecov_raise, img_to_bytes('./assets/hike/negative_r.png')),unsafe_allow_html=True)

        # if deaths_status == 'positive':
        #         st.markdown('''> <p style='font-family:Sora; font-weight:bold; '><span style=''>Deaths</span> Reported  - {:,} <span> <img src='data:image/png;base64,{}' class='img-fluid' width=24 height=24></spam></p>'''.format(cdeath_raise, img_to_bytes('./assets/hike/positive.png')),unsafe_allow_html=True)
        # elif deaths_status == 'negative':
        #     st.markdown('''> <p style='font-family:Sora; font-weight:bold; '><span style=''>Deaths</span> Reported  - {:,} <span> <img src='data:image/png;base64,{}' class='img-fluid' width=24 height=24></spam></p>'''.format(cdeath_raise, img_to_bytes('./assets/hike/negative.png')),unsafe_allow_html=True)


        # if st.checkbox('Note',(country_raise==0)):
        #     st.markdown('If this Value is ever `zero`, that means there are same number of cases reported in the last two dates, So, there is no Net Increase in Cases. However, I feel the Value `Zero` is very unlikely, So I believe it to be either **Artificiality** in the Dataset or The Data is **Not Updated** yet.')

        st.markdown("| <small style='font-size:15px;text-align:center;'><i>Recovered and Active Cases represent reports recorded until 4th Aug, 21 (read deprecation notice)</i></small></h3>",unsafe_allow_html=True)
    
    elif stats == 'Timeline':
        
        
        st.markdown('***')
        st.markdown('''<h3 style='font-family:Sora;  text-align:center;'>Time Series Plot - {}</h3>'''.format(CountryName),unsafe_allow_html=True)
        

        # retrieve Chart 
        fig = timeline
        st.plotly_chart(fig)


        if st.checkbox('Intriguing?',False):
            st.info('_I observed the following list of countries had some **Intriguing patterns** in the Time Series Plot. From the graph we can clearly see the contrast between people of different regions, reacting to the virus differntly._')
        
            # st.sidebar.markdown
            intriguing_countries = ['Ecuador','Brazil','US','China','Canada','Spain']
            st.code(intriguing_countries)


        
        st.markdown("| <small style='font-size:15px;text-align:center;'><i>Recovered and Active Cases represent reports recorded until 4th Aug, 21 (read deprecation notice)</i></small></h3>",unsafe_allow_html=True)

        

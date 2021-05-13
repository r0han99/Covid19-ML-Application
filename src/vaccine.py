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



@st.cache(persist=True)
def vacc_list(vaccloc_df, keyword='world', CountryName=None):
    vaccineList = []
    if keyword == 'world':
        for vacc in vaccloc_df['vaccines'].unique():
            vacc = vacc.split(',')
            for vaccine in vacc:
                vaccineList.append(vaccine.strip())

        vaccineList = np.unique(np.array(vaccineList))
        return vaccineList
    else:
        vaccineList = vaccloc_df[vaccloc_df['location']==CountryName]['vaccines'].values
        return vaccineList
 


def vaccineStats(vaccine):

    st.markdown('***')
    st.markdown('''<h3 style='font-family:Montserrat; font-style:italic; text-align:center;'>All About Vaccines</h3>''',unsafe_allow_html=True)
    st.markdown('<br>',unsafe_allow_html=True)
    st.markdown('***')


    vaccine_df, vaccloc_df = vaccine.values()

    vaccman = pd.read_csv('./assets/Vaccine.csv').drop('Unnamed: 0',axis=1)

    choice = st.sidebar.selectbox('Information', ['Vaccines Available', 'Vaccines Administered'],key='vaccines')
    st.sidebar.markdown('***')

    if choice == 'Vaccines Available':

        option = st.radio('Vaccine Stats By', ['Country', 'World'],key='status')
        if option == 'World':
            pass
        else:
            option = 'Country'
            country = st.selectbox('Select Country',vaccloc_df['location'],key='locations')

    
        if option == 'World':
            
            VaccineList = vaccman['vaccines'] # world
            st.markdown('''<hr>''',unsafe_allow_html=True)
            st.markdown('''<p><span style='font-style:italic; font-weight:bold;   font-size:30px'>Vaccination 💉</span> <span style='padding-left: 250px;'></span> <span style='font-style:italic; font-weight:bold;   font-size:30px'>Manufacturer</span></p>''', unsafe_allow_html=True)
            st.markdown('''<hr>''',unsafe_allow_html=True)
            # After Collecting efficacy data 
            # st.markdown('''<p><span style='font-style:italic; font-weight:bold;   font-size:30px'>Vaccination</span> <span style='padding-left: 100px;'> </span> <span style='font-style:italic; font-weight:bold;   font-size:30px'>Manufacturer</span><span style='padding-left: 90px; font-style:italic; font-weight:bold;   font-size:30px'>Efficacy</span></p>''', unsafe_allow_html=True)

            for vaccine,path in zip(VaccineList,vaccman['Paths']):

                # After Collecting efficacy data 
                # st.markdown('''<p><span style='font-style:italic; font-weight:bold; color:dodgerblue;'>{}</span> <span style='padding-left: 160px;'> </span><img src='data:image/png;base64,{}' class='img-fluid' width=220 height=120><span style='padding-left: 90px; font-style:italic; font-weight:bold; color:limegreen;'>{}</span></p>'''.format(vaccine.capitalize(), img_to_bytes("{}".format(path)), '95%'), unsafe_allow_html=True)
                
                st.markdown('''<p><span style='font-style:italic; font-weight:bold;  '>* {}</span> <span style='padding-left: 290px;'> </span><img src='data:image/png;base64,{}' class='img-fluid' width=220 height=120></p>'''.format(vaccine.capitalize(), img_to_bytes("{}".format(path))), unsafe_allow_html=True)
                st.markdown('''<br>''',unsafe_allow_html=True)
        else:
            st.markdown('***')
            try:
                st.markdown('''<p><span style='font-style:italic; font-weight:bold;   text-align:center; font-size:45px; text-decoration:underline;'>{}<span>   <img src='data:image/png;base64,{}' class='img-fluid' width=50 height=50></p>'''.format(country, img_to_bytes("./assets/Countries/{}.png".format(country.lower()))), unsafe_allow_html=True)
            except:
                # file name exception
                st.markdown('''<p><span style='font-style:italic; font-weight:bold;   text-align:center; font-size:45px; text-decoration:underline;'>{}<span></p>'''.format(country), unsafe_allow_html=True)
            
            _, _, vaccine, lastObs, provider, website = vaccloc_df[vaccloc_df['location']==country].values[0]

            st.markdown('* _Vaccines been Administered_ ~ ___{}___'.format(vaccine))
            st.markdown('* _Last Observation Date_ ~ ___{}___'.format(lastObs))
            st.markdown('* _Nationwide Vaccine Provider_ ~ ___{}___'.format(provider))
            st.markdown('* _Website_ ~ ___{}___'.format(website))


    elif choice == 'Vaccines Administered':

        # st.write(vaccine_df.columns)
        country = st.selectbox('Select Country',vaccine_df['location'].unique(),key='locations')
        st.markdown('***')
        try:
            st.markdown('''<p><span style='font-style:italic; font-weight:bold;   text-align:center; font-size:45px; text-decoration:underline;'>{}<span>   <img src='data:image/png;base64,{}' class='img-fluid' width=50 height=50></p>'''.format(country, img_to_bytes("./assets/Countries/{}.png".format(country.lower()))), unsafe_allow_html=True)
        except:
            # file name exception
            st.markdown('''<p><span style='font-style:italic; font-weight:bold;   text-align:center; font-size:45px; text-decoration:underline;'>{}<span></p>'''.format(country), unsafe_allow_html=True)
        
        total = vaccine_df[vaccine_df['location'] == country]['total_vaccinations'].sum()
        full_vacc = vaccine_df[vaccine_df['location'] == country]['people_fully_vaccinated'].sum()
        oneshot = vaccine_df[vaccine_df['location'] == country]['people_vaccinated'].sum()
        last_date = vaccine_df[vaccine_df['location'] == country]['date'][-1:].values[0]

        fully_vacc = (full_vacc/total)*100
        partially_vacc = (oneshot/total)*100

        st.markdown('''<p><span style='font-weight:bold; text-align:center; font-size:40px; '>{:.2f}% / <span style='font-size:20px;  font-weight:normal;'>{:,}</span></span> <span style='font-weight:bold; font-style:italic; padding-left: 20px; color:limegreen;'>Fully Vaccinated.</span></p>'''.format(fully_vacc, int(total)), unsafe_allow_html=True)
        st.markdown('''<p><span style='font-weight:bold;  text-align:center; font-size:40px; '>{:.2f}% / <span style='font-size:20px; font-weight:normal;'>{:,}</span></span> <span style='font-weight:bold; font-style:italic; padding-left: 20px; color:deepskyblue;'>Got their First Vaccine Shot.</span></p>'''.format(partially_vacc, int(total)), unsafe_allow_html=True)
        
        st.markdown('''<p><span style='font-style:italic; font-weight:bold;   text-align:center; font-size:15px;'>Last Date of Reports <span style='color:dodgerblue;'>{}</span></span></p>'''.format(last_date), unsafe_allow_html=True)


        



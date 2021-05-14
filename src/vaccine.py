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

    choice = st.sidebar.selectbox('Information', ['Vaccines Administered', 'Vaccines Available'],key='vaccines')
    st.sidebar.markdown('***')

    if choice == 'Vaccines Available':

        st.markdown('''> <p style='font-size:30px'><span style='font-style:italic; text-align: center; font-weight:bold; font-size:30px;'>Vaccinations of the World</span> 🌍</p>''', unsafe_allow_html=True)
        st.markdown('''<hr>''',unsafe_allow_html=True)

        VaccineList = vaccman['vaccines'] # world
        paths = vaccman['Paths']
        information = vaccman['Info']

        first = st.beta_expander(VaccineList[0].capitalize(), expanded=True)
        first.image(paths[0],width=300)
        first.markdown('_{}_'.format(information[0]))
        

        expobjs = []
        for vaccine in VaccineList[1:]:
            expobjs.append(st.beta_expander(vaccine.capitalize()))
       
        
        for obj, path, info in zip(expobjs,paths[1:],information[1:]): 
            obj.image(path,width=300)
            obj.markdown('_{}_'.format(info))
            
            


    elif choice == 'Vaccines Administered':

        # st.write(vaccine_df.columns)

        country = st.selectbox('Select Country',vaccine_df['location'].unique(),key='locations')

        st.markdown('***')
        try:
            st.markdown('''<p><span style='font-style:italic; font-weight:bold;   text-align:center; font-size:45px; text-decoration:underline;'>{}<span>   <img src='data:image/png;base64,{}' class='img-fluid' width=50 height=50></p>'''.format(country, img_to_bytes("./assets/Countries/{}.png".format(country.lower()))), unsafe_allow_html=True)
        except:
            # file name exception
            st.markdown('''<p><span style='font-style:italic; font-weight:bold;   text-align:center; font-size:45px; text-decoration:underline;'>{}<span></p>'''.format(country), unsafe_allow_html=True)
        

    
        total = vaccine_df[vaccine_df['location'] == country]['total_vaccinations'][-1:].values[0]
        full_vacc = vaccine_df[vaccine_df['location'] == country]['people_fully_vaccinated'][-1:].values[0]
        oneshot = vaccine_df[vaccine_df['location'] == country]['people_vaccinated'][-1:].values[0]
        last_date = vaccine_df[vaccine_df['location'] == country]['date'][-1:].values[0]
        


        fully_vacc = (full_vacc/total)*100
        partially_vacc = (oneshot/total)*100

        st.markdown('''> <p><span style='font-weight:bold; text-align:center; font-size:40px; '>{:,}</span> <span style='font-weight:bold; font-style:italic; padding-left: 20px;'>Total Vaccine Administrations.</span></p>'''.format(int(total)), unsafe_allow_html=True)
        st.markdown('''> <p><span style='font-weight:bold; text-align:center; font-size:40px; '>{:.2f}% / <span style='font-size:20px;  font-weight:normal;'>{:,}</span></span> <span style='font-weight:bold; font-style:italic; padding-left: 20px; color:limegreen;'>Fully Vaccinated.</span></p>'''.format(fully_vacc, int(total)), unsafe_allow_html=True)
        st.markdown('''> <p><span style='font-weight:bold;  text-align:center; font-size:40px; '>{:.2f}% / <span style='font-size:20px; font-weight:normal;'>{:,}</span></span> <span style='font-weight:bold; font-style:italic; padding-left: 20px; color:deepskyblue;'>Got their First Vaccine Shot.</span></p>'''.format(partially_vacc, int(total)), unsafe_allow_html=True)
        st.markdown('''> <p><span style='font-style:italic; font-weight:bold;   text-align:center; font-size:15px;'>Reported on <span style='color:dodgerblue;'>{}</span></span></p>'''.format(last_date), unsafe_allow_html=True)

        st.markdown('***')

        try:
            _, _, vaccine, lastObs, provider, website = vaccloc_df[vaccloc_df['location']==country].values[0]

            st.markdown('* _Vaccines been Administered_ ~ ___{}___'.format(vaccine))
            st.markdown('* _Last Observation Date_ ~ ___{}___'.format(lastObs))
            st.markdown('* _Nationwide Vaccine Provider_ ~ ___{}___'.format(provider))
            st.markdown('* _Website_ ~ ___{}___'.format(website))
        except:
            st.warning('___No Reported Data Found___')

        
        
       





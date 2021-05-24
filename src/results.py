# Application Front-End dependencies 
import streamlit as st
from streamlit import caching

# Data-analytics Dependencies
import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
from covid import Covid

# Neural networks
from tensorflow.keras.models import load_model

# Os Dependencies
import datetime
from pathlib import Path
import time
import base64
import re


fcols = ['pneumonia', 'pregnancy', 'diabetes', 'copd', 'asthma',
    'inmsupr', 'hypertension', 'cardiovascular', 'obesity', 'renal_chronic',
    'tobacco']

@st.cache(persist=True)
def load_patient_datacorpus():
    path = './data/final_cdata.csv'
    data = pd.read_csv(path).drop('Unnamed: 0',axis=1)
    data['recovery_status'] = data['date_died'].where((data['date_died'] == 'Recovered'), 'Died')

    return data 

# @st.cache(persist=True, allow_output_mutation=True)
def initialise_nets():

    path1 = './models/Nets/Agg-IcuNet.h5' # ICUNET
    path2 = './models/Nets/Agg-IntubationNet.h5' # INTUBATION NET

    # path1 = './models/Nets/icuNet.h5' # ICUNET
    # path2 = './models/Nets/intubationNet.h5' # INTUBATION NET

    net1 = load_model(path1)
    net2 = load_model(path2)

    return net1, net2


def age_pipe(age):
    
    if age >= 0 and age < 4:
        AgeGroup = 'Infant'
    elif age >= 4 and age < 7:
        AgeGroup = 'Toddler'
    elif age >= 7 and age < 16:
        AgeGroup = 'Kid'
    elif age >= 16 and age < 22:
        AgeGroup = 'Teenager'
    else:
        AgeGroup = 'Adult'
    
    return AgeGroup

def criticality_likelihood_estimator(sample,data,icuNet,intubationNet):

    classes = ['Not required', 'Required']
    
    '''
        * Data ( if present ), will be reorganised to fit the Networks Architecuture
        * Neural Networks are parameterised with the feature set;
        * probability is returned;
    
    '''
    predcols = ['Sex', 'Pneumonia', 'Age', 'Pregnancy', 'Diabetes', 'COPD', 'Asthma',
       'Immunocompromise', 'Hypertension', 'Cardiovascular', 'Obesity', 'Chronic Renal',
       'Tobacco', 'Covid-Result', 'interval_symptoms']

    sample['Covid-Result'] = 'Positive'

    # st.code(sample)

    features = []
    for key in predcols[:-1]:
        features.append(sample[key])
    features = pd.Series(features,name='preconditions')

    # st.code(features)
    

    #Altering 
    mapping = {'Yes':1, 'No':2, 'Male': 2, 'Female':1, 'Positive':1, 'Negative':2}
    features = features.map(mapping).fillna(value=sample['Age'])
    ins = int(data[data['AgeGroup']==age_pipe(sample['Age'])]['interval_symptoms'].median())
    features = np.append(features.values, ins)

    # st.code(features)
    # st.code(features.shape)

    proba_icu = icuNet.predict_classes(features.reshape(1,-1))[0][0]
    proba_intube = intubationNet.predict_classes(features.reshape(1,-1))[0][0]
    
    # st.code(proba_icu)
    # st.code(proba_intube)
    # st.code(classes[proba_icu])
    # st.code(classes[proba_intube])

    probability = (proba_icu, proba_intube)
    # probability= (0,0)

    return probability


def reporting(absprematches,data,mask1,sample):

    # report dictionary
    absolute_report = {}


    absprecondmatch = data[mask1].reset_index(drop=True).iloc[absprematches] 

    # reporting
    absolute_report['covid_res'] = sample['Covid-Result']
    absolute_report['total_on_age'] = data[mask1].shape[0]
    absolute_report['t_abs_precond_matches'] = absprecondmatch.shape[0]
    absolute_report['gender_counts'] = absprecondmatch['sex'].value_counts()
    absolute_report['status'] = absprecondmatch['patient_type'].value_counts().append(absprecondmatch['recovery_status'].value_counts())
    
    # for death 
    try:
        temp = absolute_report['status']['Died']
    except:
        absolute_report['status']['Died'] = 0

    try:
        temp = absolute_report['status']['Discharged']
    except:
        absolute_report['status']['Discharged'] = 0

    try:
        temp = absolute_report['status']['Recovered']
    except:
        absolute_report['status']['Recovered'] = 0

    try:
        temp = absolute_report['status']['Admitted']
    except:
        absolute_report['status']['Admitted'] = 0

    

    absolute_report['interval_symptoms'] = absprecondmatch['interval_symptoms'].median()
    mask1 = (absprecondmatch['intubed'] == 'Yes') & (absprecondmatch['icu'] == 'Yes')
    mask2 = (absprecondmatch['intubed'] == 'Yes') & (absprecondmatch['icu'] == 'No')
    mask3 = (absprecondmatch['intubed'] == 'No') & (absprecondmatch['icu'] == 'Yes')
    mask4 = (absprecondmatch['intubed'] == 'No') & (absprecondmatch['icu'] == 'No')

    # print('Intubed and ICU : ',absprecondmatch[mask1].shape[0])
    # print('Yes Intubed and No ICU : ',absprecondmatch[mask2].shape[0])
    # print('No Intubed and Yes ICU : ',absprecondmatch[mask3].shape[0])
    # print('No Intubed and No ICU : ',absprecondmatch[mask4].shape[0])

    absolute_report['criticality'] = {'icu_intube': absprecondmatch[mask1].shape[0],
                                  'intube_noicu': absprecondmatch[mask2].shape[0],
                                  'nointube_icu': absprecondmatch[mask3].shape[0],
                                  'nointube_noicu': absprecondmatch[mask4].shape[0],
                                 }

    return absolute_report



def find_absolute_match(data,sample):

 

    # First Initialise pivots 
    covid_res = sample['Covid-Result']
    ageGroup = age_pipe(sample['Age'])

    


    # Absolute Match Masking
    mask1 = (data['sex'] == sample['Sex']) & (data['age'] == sample['Age']) & (data['covid_res'] == 'Positive')
    
    # for future updates, mention females on same age and preconditions
    mask2 = (data['age'] == sample['Age']) & (data['covid_res'] == 'Positive')
    
    
    

    # Setting up preconditions and feature sets
    
    preconditions = [x for x in list(sample.values())[4:]]
    preconditions= pd.Series(preconditions,name='preconditions',index=fcols)

   

    if data[mask1].empty:
        
        return None
    
    else:
        # Prompt
        prompt_slot = st.empty()
        
        emoji_list = ['⏳','⌛️']


        absprematches = []

        # Emoji List for Alternating effect
        altlog = []
        for x in range(data[mask1].shape[0]): # number of records found 
            
            for i in emoji_list:
                altlog.append(i)

        
        # This will be tagged along with a progress-bar feedback on the front-end

        bar_total = list(data[mask1][fcols].reset_index(drop=True).index[-1:])[0]
        my_bar = st.progress(0)
        

        for row,logo in zip(data[mask1][fcols].reset_index(drop=True).index, altlog):
            
            prompt_slot.markdown('''<span style='font-family: Sora; text-align: center;'>Searching for people with same <i>Pre-Conditions</i> as you!{}</span>'''.format(logo), unsafe_allow_html=True)
            percent = row/bar_total
            my_bar.progress(percent)

            if (data[mask1][fcols].reset_index(drop=True).iloc[row,:].values == preconditions).all():
    
                # time.sleep(0.0001)

                absprematches.append(row)
            else:
                continue
        
        
        # only if absprematch is not empty
        if not len(absprematches) == 0:

            
            absolute_report = reporting(absprematches,data,mask1,sample)

            st.markdown('***')
            title_slot = st.empty()
            info_slot = st.empty()
            
            st.markdown("<span style='font-family:Sora; text-align:center; font-size:17px;'>Patient records, who've already gone through the COVID19 Experience.</span>",unsafe_allow_html=True)
            prompt_dict = [
                        '''> Total number of records found with Same Age as you : <span style='font-family:Sora;'>{} </span>'''.format(absolute_report['total_on_age']),
                    

            ]
            for prompts in prompt_dict:
                st.markdown(prompts,unsafe_allow_html=True)


            st.markdown('***')
            return absolute_report, preconditions
        
        
        else:


            
            return None, preconditions
        


def charts(absolute_report, chart_name):
    
    # status
    if chart_name == 'hospitalized':
        status = absolute_report['status']

        colors = ['dodgerblue','crimson']
        explode = (0, 0.1)

        langs = ['Discharged','Admitted']
        values = [status['Discharged'], status['Admitted']]         

        fig, ax = plt.subplots(figsize=(5,5))
        ax.set_title('Hopitalized Cases')
        

        ax.pie(values,labels=langs,colors=colors,wedgeprops={'edgecolor': 'black'},autopct='%1.2f%%',explode=explode)

        return fig
    
    elif chart_name == 'ICU_Intubation':

        plt.style.use('seaborn-whitegrid')
        criticality = absolute_report['criticality']
        values = list(criticality.values())
        index = ['Both ICU & Intubation', 'Only Intubation', 'Only ICU', 'Not Critical']

        fig, ax = plt.subplots()

        ax.bar(index,values,color='crimson')
        rects = ax.patches
        labels = values

        for rect, label in zip(rects, labels):
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width() / 3, height, label,
                    ha='center', va='bottom')

        ax.set_xlabel('Category')
        ax.set_ylabel('Patient Counts')
        ax.set_title('Intubation and ICU Requirement')

        return fig
    






def display_results(package):



    # Data and Neural Networks
    data = load_patient_datacorpus()
    icuNet, intubationNet = initialise_nets()


    absolute_report, preconditions = find_absolute_match(data, package)

    # Show results button 

    if not absolute_report == None:
        results = st.beta_expander('Results 🧠', expanded=False)
        # with results.form("Analytics"):
        results.markdown('***')
        agegroup = '''<span style='font-weight:bold; text-align:left; font-size:16px; font-family:Sora; color:#2484F7; padding-bottom:20px;'>Age : {}, <i>{}</i><span>'''.format(package['Age'],package['Sex'])
        results.markdown('''<p><span style='font-weight:bold; text-align:center; font-size:50px; text-decoration:underline; '>{}</span> {}</p>'''.format(package['Name'],agegroup), unsafe_allow_html=True)
        results.markdown('''<p><span style='font-weight:bold; text-align:center; font-size:22px;'>Present COVID19 Diagnosis: <span style="color:crimson; font-style:italic; font-size:17;">{}</span></span></p>'''.format(package['Covid-Result']), unsafe_allow_html=True)
        results.markdown('***')

        results.markdown('''* ***Correlating You to COVID-19 Recovered/Dead patients of the same Age and pre-conditions from the Patient DataCorpus;***''')
        
        results.markdown('''> *People with same Medical Conditions as you* :  <span style='font-family:Sora; color:#2484F7;'>{} </span>'''.format(absolute_report['t_abs_precond_matches']), unsafe_allow_html=True)
        results.markdown('***')
        
        results.markdown('''* <span style="font-weight:bold; font-style:italic; text-align:center;">What Happened to the People with Sames Conditions as You? <br><br></span>''',unsafe_allow_html=True)
        
        cols = results.beta_columns(2)
        
        status_fig = charts(absolute_report, chart_name='hospitalized')
        criticality_fig = charts(absolute_report, chart_name='ICU_Intubation')


        cols[0].pyplot(status_fig)
        cols[1].pyplot(criticality_fig)

        recovered = absolute_report['status']['Recovered']
        died = absolute_report['status']['Died']

        results.markdown('''> *Out of* <span style='font-family:Sora; color:#2484F7;'>{}</span> ***Hopitalized*** : <span style='font-family:Sora; color:#2484F7;'>{}</span> ***Recovered*** & <span style='font-family:Sora;color:#2484F7;'>{}</span> ***Succumbed*** to *COVID19*; '''.format(absolute_report['t_abs_precond_matches'], recovered, died ), unsafe_allow_html=True)
        
        results.markdown('***')
        results.markdown(" > <span style='font-size:24px; font-weight:bold; font-style:italic;'>Neural Network's Likelihood Estimation </span>",unsafe_allow_html=True)
        results.markdown('''* <span style='font-size:1px; '> *Based on your Pre-Conditions, the <b>Neural Network</b> will yield a Numerical Estimation. This Number, represents the posibility of you requiring either Intubation or an ICU, If tested +ve for COVID19* </span>''', unsafe_allow_html=True)

        results.markdown("> ***Your Medical Conditions***")
        results.code(preconditions)

        

        probability = criticality_likelihood_estimator(package,data,icuNet,intubationNet)

        results.markdown(" > <span style='font-size:24px; font-weight:bold; font-style:italic;'>Probability</span>",unsafe_allow_html=True)
        results.markdown('''> <span style='font-weight:bold; text-align:center; font-size:40px; color:#2484F7;'>{}/1</span>  ***chance to get Admitted to an ICU.***'''.format(probability[0]), unsafe_allow_html=True)
        results.markdown('''> <span style='font-weight:bold; text-align:center; font-size:40px; color:#2484F7;'>{}/1</span>   ***chance for you to require an Intubation Setup.***'''.format(probability[1]), unsafe_allow_html=True)

        results.markdown('***')

        # results.markdown(probability)
        if results.checkbox('Note',True):
            results.markdown("> _The Pre-trained Neural Network used to yield this probability estimate is trained on Data of patients related to ***Mexican Origin***; Though this numerical states the possibility in quantified terms, this whatsoever doesn't apply when we consider the complexity of Medical conditions._",unsafe_allow_html=True)

        results.markdown('<center style="font-weight:bold; font-style:italic;">End-Report</center>',unsafe_allow_html=True)
        

    else:
        results = st.beta_expander('Results 🧠', expanded=True)
        
        results.markdown('***')
        agegroup = '''<span style='font-weight:bold; text-align:left; font-size:16px; font-family:Sora; color:#2484F7; padding-bottom:20px;'>Age : {}, <i>{}</i><span>'''.format(package['Age'],package['Sex'])
        results.markdown('''<p><span style='font-weight:bold; text-align:center; font-size:50px; text-decoration:underline; '>{}</span> {}</p>'''.format(package['Name'],agegroup), unsafe_allow_html=True)
        results.markdown('''<p><span style='font-weight:bold; text-align:center; font-size:22px;'>Present COVID19 Diagnosis: <span style="color:crimson; font-style:italic; font-size:17;">{}</span></span></p>'''.format(package['Covid-Result']), unsafe_allow_html=True)
        results.markdown('***')

        results.error('***Unfortunately, there are no patients with absolute same matches as you in the DataCorpus***')
    
        results.markdown('***')


        results.markdown(" > <span style='font-size:24px; font-weight:bold; font-style:italic;'>Neural Network's Likelihood Estimation </span>",unsafe_allow_html=True)
        results.markdown('''* <span style='font-size:1px; '> *Based on your Pre-Conditions, the <b>Neural Network</b> will yield a Numerical Estimation. This Number, represents the posibility of you requiring either Intubation or an ICU, If tested +ve for COVID19* </span>''', unsafe_allow_html=True)

        results.markdown("> ***Your Medical Conditions***")
        results.code(preconditions)

        

        probability = criticality_likelihood_estimator(package,data,icuNet,intubationNet)

        results.markdown(" > <span style='font-size:24px; font-weight:bold; font-style:italic;'>Probability</span>",unsafe_allow_html=True)
        results.markdown('''> <span style='font-weight:bold; text-align:center; font-size:40px; color:#2484F7;'>{}/1</span>  ***chance to get Admitted to an ICU.***'''.format(probability[0]), unsafe_allow_html=True)
        results.markdown('''> <span style='font-weight:bold; text-align:center; font-size:40px; color:#2484F7;'>{}/1</span>   ***chance for you to require an Intubation Setup.***'''.format(probability[1]), unsafe_allow_html=True)

        results.markdown('***')

        # results.markdown(probability)
        results.markdown('<center style="font-weight:bold; font-style:italic;">End-Report</center>',unsafe_allow_html=True)
        
        
        if results.checkbox('Note',True):
            results.markdown("> _The Pre-trained Neural Network used to yield this probability estimate is trained on Data of patients related to ***Mexican Origin***; Though this numerical states the possibility in quantified terms, this whatsoever doesn't apply when we consider the complexity of Medical conditions._",unsafe_allow_html=True)

        results.markdown('<center style="font-weight:bold; font-style:italic;">End-Report</center>',unsafe_allow_html=True)
        

        beta = st.beta_expander('Beta-Testing')
        beta.warning('*The current pipeline is only constrained towards reporting `Absolute Matches` on Pre-Conditions; future versions, however, will include much more scrutiny towards finding records with partial matches while considering pre-conditions which are prominent to faciliate COVID19s potency*')


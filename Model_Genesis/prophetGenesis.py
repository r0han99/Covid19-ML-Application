#!/opt/anaconda3/bin/python
import pandas as pd
import numpy as np 
import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date
import sys
import os
import time
import pickle
from fbprophet import Prophet
# ------------------------------------------

def Model_complete_Genesis(confirmed_df,recovered_df,deaths_df):
    dates_conf = confirmed_df.drop(['Country/Region','Province/State','Lat','Long'], axis = 1).columns
    dates_recov = recovered_df.drop(['Country/Region','Province/State','Lat','Long'], axis = 1).columns
    dates_death = deaths_df.drop(['Country/Region','Province/State','Lat','Long'], axis = 1).columns
    days_conf = np.array([i for i in range(len(dates_conf))]).reshape(-1, 1)
    days_recov = np.array([i for i in range(len(dates_recov))]).reshape(-1, 1)
    days_death = np.array([i for i in range(len(dates_death))]).reshape(-1, 1)
    # -
    country_top_7 = confirmed_df[['Country/Region',confirmed_df.columns[-1]]]
    country_top_7 = country_top_7.sort_values(by=confirmed_df.columns[-1],ascending=False)
    country_top_7 = country_top_7.reset_index()
    country_top_7.drop('index',axis=1,inplace=True)
    top7 = list(country_top_7[:7]['Country/Region'])
    
    # preprocessing 
    confirmed = confirmed_df.drop(['Province/State','Lat','Long'],axis=1)
    recovered = recovered_df.drop(['Province/State','Lat','Long'],axis=1)
    deaths = deaths_df.drop(['Province/State','Lat','Long'],axis=1)
        
    # Model Genesis
    start = time.perf_counter()
    for countryname in top7:
        conf = confirmed[confirmed['Country/Region'] == countryname].drop('Country/Region',axis=1).T.reset_index()
        recov = recovered[recovered['Country/Region'] == countryname].drop('Country/Region',axis=1).T.reset_index()
        death = deaths[deaths['Country/Region'] == countryname].drop('Country/Region',axis=1).T.reset_index()
        conf.columns = ['ds','y']
        recov.columns = ['ds','y']
        death.columns = ['ds','y']
        conf['ds'] = pd.to_datetime(conf['ds'])
        recov['ds'] = pd.to_datetime(recov['ds'])
        death['ds'] = pd.to_datetime(death['ds'])
        
        # model-fitting
        conf_m = Prophet(interval_width=0.90)
        recov_m = Prophet(interval_width=0.90)
        death_m = Prophet(interval_width=0.90)
        conf_m.fit(conf)
        recov_m.fit(recov)
        death_m.fit(death)
        
        # dumping       
        if not os.path.exists('Model-Confirmed'):
            os.makedirs('Model-Confirmed')
        if not os.path.exists('Model-Recovered'):
            os.makedirs('Model-Recovered')
        if not os.path.exists('Model-Deaths'):
            os.makedirs('Model-Deaths')  
        
        with open('./Model-Confirmed/{}.pkl'.format(countryname),'wb') as f:
                pickle.dump(conf_m,f)
        
        with open('./Model-Recovered/{}.pkl'.format(countryname),'wb') as f:
                pickle.dump(recov_m,f)
                
        with open('./Model-Deaths/{}.pkl'.format(countryname),'wb') as f:
                pickle.dump(death_m,f)
                
        print('Done!')
        print('Elapsed Time {}s'.format((time.perf_counter() - start)))
        

        

# Data Source

confirmed_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
recovered_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'
deaths_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'

# Reading Data

confirmed_df = pd.read_csv(confirmed_url)
recovered_df = pd.read_csv(recovered_url)
deaths_df = pd.read_csv(deaths_url)


# Generating Training and Dumping Prophet Models
Model_complete_Genesis(confirmed_df,recovered_df,deaths_df)



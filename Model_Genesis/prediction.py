#!/opt/anaconda3/bin/python

import pandas as pd
import numpy as np 
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
import datetime
import time 
import pickle 
# ----------------------------

confirmed_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
recovered_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv')
deaths_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')

country_top_7 = confirmed_df[['Country/Region','9/19/20']]
country_top_7 = country_top_7.sort_values(by='9/19/20',ascending=False)
country_top_7 = country_top_7.reset_index()
country_top_7.drop('index',axis=1,inplace=True)
top7 = list(country_top_7[:7]['Country/Region'])


dates = confirmed_df.drop(['Country/Region','Province/State','Lat','Long'], axis = 1).columns
days_since_1_22 = np.array([i for i in range(len(dates))]).reshape(-1, 1)

PRED_FOR_EACH_COUNTRY = []

start = time.perf_counter()

for COUNTRY in top7:
    country_conf_df = confirmed_df[confirmed_df['Country/Region'] == COUNTRY]
    cont_cf=country_conf_df.copy().reset_index()
 
    cont_cf=cont_cf.set_index('Country/Region')
    cont_cf=cont_cf.drop(['index', 'Province/State','Lat','Long'], axis = 1)

    confirmed = country_conf_df.iloc[:, 4:].T
    confirmed = confirmed.rename(columns={list(confirmed.columns)[0]: "ConfirmedCases"})
    confirmed.index = pd.to_datetime(confirmed.index)
    dates = confirmed.index
    days_since_1_22 = np.array([i for i in range(len(dates))]).reshape(-1, 1)
    

    confirmed_cases = np.array(confirmed['ConfirmedCases']).reshape(-1, 1)
    poly = PolynomialFeatures(degree=6)
    poly_X_train_confirmed = poly.fit_transform(days_since_1_22) 

    linear_model = LinearRegression(normalize=True, fit_intercept=False)
    linear_model.fit(poly_X_train_confirmed, confirmed_cases)

    with open('{}'.format(COUNTRY),'wb') as f:
        pickle.dump(linear_model,f)
        
        
print('\nDone\nELAPSED TIME {}sec'.format((time.perf_counter() - start)))
    
 
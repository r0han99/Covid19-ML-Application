#!/opt/anaconda3/bin/python

import pandas as pd
import numpy as np 
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import datetime
import time 
import pickle 
import os
# ----------------------------

def transform_input(days_since_1_22,number_of_days=30):
    future_forecast_dates = []
    poly = PolynomialFeatures(degree=6)
    if number_of_days!=30:
        number_of_days = int(input('Enter number of days from now to the future: '))
    forecast = np.array([i for i in range(len(days_since_1_22)+number_of_days)]).reshape(-1, 1)
    start = '1/22/2020'
    start_date = datetime.datetime.strptime(start, '%m/%d/%Y')
    future_forecast_dates = []
    for i in range(len(forecast)):
        future_forecast_dates.append((start_date + datetime.timedelta(days=i)).strftime('%m/%d/%Y'))
    poly_future_forecast = poly.fit_transform(forecast)
    return poly_future_forecast,number_of_days,future_forecast_dates[-number_of_days:]



def Model_Genesis():

    confirmed_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')

    country_top_7 = confirmed_df[['Country/Region','9/19/20']]
    country_top_7 = country_top_7.sort_values(by='9/19/20',ascending=False)
    country_top_7 = country_top_7.reset_index()
    country_top_7.drop('index',axis=1,inplace=True)
    top7 = list(country_top_7[:7]['Country/Region'])

    dates = confirmed_df.drop(['Country/Region','Province/State','Lat','Long'], axis = 1).columns
    days_since_1_22 = np.array([i for i in range(len(dates))]).reshape(-1, 1)


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


def Model_Evalutation(days_since_1_22,trans_df):
    top7 = ['India', 'US', 'Russia', 'Peru', 'Mexico', 'Brazil', 'Colombia']
    all_pred = []
    rmse = [] 
    print('COUNTRY     MEANVAL    RMSE')
    for country in top7:
        with open(country,'rb') as f:
            model = pickle.load(f)
            dates_n,_,_ = transform_input(days_since_1_22)
            preds = model.predict(dates_n)
            preds = preds[:-30]
            all_pred.append(preds)
            y_true = trans_df.loc[country,:].values.reshape(-1,1)
            rmse = np.sqrt(mean_squared_error(preds,y_true))
            meanval = trans_df.loc[country,:].mean()
            print('{} ~      {}      {}'.format(country, meanval,rmse))

    return all_pred


key = int(input('Enter what Action to perform\n1. Model Genesis,\n2. Model Evualuation,\n3. Sample Test Prediction\nEnter your choice: '))
confirmed_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
trans_df = confirmed_df.drop(['Province/State','Lat','Long'], axis = 1)
trans_df = confirmed_df.drop(['Province/State','Lat','Long'], axis = 1)
trans_df = trans_df.set_index('Country/Region')
dates = confirmed_df.drop(['Country/Region','Province/State','Lat','Long'], axis = 1).columns
days_since_1_22 = np.array([i for i in range(len(dates))]).reshape(-1, 1)




if key == 1:
    if not os.path.exists('./Models/'):
        os.makedirs('./Models')
        Model_Genesis()
    else:
        print('Predictive Models already exist')

elif key == 2:
    print('Model Evaluation\n')
    _ = Model_Evalutation(days_since_1_22, trans_df)

elif key == 3:
    with open('India','rb') as f:
        model = pickle.load(f)
        dates_n,forcast,dates_real = transform_input(days_since_1_22,10)
        preds = model.predict(dates_n)
    preds = zip(dates_real,np.round(preds.reshape(-1,1)[-forcast:]).astype('int64'))
    for x,y in preds:
        print(x,y)

else:
    print('Invalid Exiting')


   










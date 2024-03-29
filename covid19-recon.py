
# Application GUI dependencies 
import streamlit as st
from src.preconditional import app
from streamlit import caching

# Dataanalytics Dependencies 
import pandas as pd
import numpy as np 
from covid import Covid
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

# os dependecies
import re
from datetime import date
from datetime import datetime, timedelta
import sys
import time
import pickle
from pathlib import Path
import base64
# from fbprophet import Prophet
# sys.tracebacklimit = 1



covid = Covid()

# Johns Hopkins CSSE Data (Auto-Updated)
confirmed_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
recovered_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'
deaths_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
aggregate_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/web-data/data/cases_country.csv'

st.set_page_config(page_title="Covid19-Recon-App",page_icon="./assets/tablogo.png",layout="centered",initial_sidebar_state="auto",)


def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded


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

@st.cache(persist=True)
def Data_load(confirmed_url,deaths_url,recovered_url,aggregate_url):
    confirmed_df = pd.read_csv(confirmed_url)
    recovered_df = pd.read_csv(recovered_url)
    deaths_df = pd.read_csv(deaths_url)
    aggregate_df = pd.read_csv(aggregate_url)

    confirmed_df = confirmed_df.replace(np.nan,'unregistered',regex=True)
    recovered_df = recovered_df.replace(np.nan,'unregistered',regex=True)
    deaths_df = deaths_df.replace(np.nan,'unregistered',regex=True)

    return confirmed_df, deaths_df, recovered_df, aggregate_df


@st.cache(persist=True)
def choro_aggregate(agg_df):
    attrs = ['Confirmed','Deaths','Recovered','Active']
    choropleth = []
    for attr in attrs:
        choropleth.append(agg_df[['Country_Region', 'Lat','Long_','{}'.format(attr),'UID','ISO3']])

    return choropleth


def choroplethChart(data,attr,config):
    total = data[attr].sum()
    
    palette = config['palette']
    border = config['border']
    title = config['title']
    
    fig = go.Figure(data=go.Choropleth(
        locations = data['ISO3'],
        z = data[attr],
        text = data['Country_Region'],
        colorscale = palette,
        autocolorscale=False,
        reversescale=True,
        marker_line_color=border,
        marker_line_width=1,
      
    ))

    fig.update_layout(
        title_text='{}, WorldWide {:,}'.format(attr,total),
        title_font_family='poppins',
        title_x=0.5,
        title_font_color=title,
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='equirectangular'
        ),
        annotations = [dict(
            x=0.55,
            y=0.1,
            xref='paper',
            yref='paper',
            text='',
            showarrow = False,
        )]
    )
    fig.update_geos(lataxis_showgrid=True, lonaxis_showgrid=True)
    fig.update_layout(height=300, margin={"r":0,"t":0,"l":0,"b":0})

    return fig
    

@st.cache(persist=True)
def preprocessing0(confirmed_df, recovered_df, deaths_df):
    confirmed_summary = confirmed_df.drop(['Lat','Long','Province/State','Country/Region'],axis=1).sum()
    # confirmed_summary = confirmed_summary.sum()
    summary = pd.DataFrame(confirmed_summary)
    summary['recovered'] = recovered_df.drop(['Lat','Long','Province/State','Country/Region'],axis=1).sum()
    summary['deaths'] = deaths_df.drop(['Lat','Long','Province/State','Country/Region'],axis=1).sum()
    summary.columns = ['Confirmed', 'Recovered', 'Deaths']
    summary['Active'] = summary['Confirmed'] - summary['Recovered'] - summary['Deaths']
    summary['Months'] = pd.to_datetime(summary.index)
    summary['Month_Year'] = pd.to_datetime(summary['Months']).dt.strftime('%Y-%m-%d')
    summary['Months'] = summary['Months'].dt.month
    

    return summary


def TimeSeriesPlot(summary,theme,region='Global'):

    # Months = summary.index
    Months = summary['Month_Year']

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=Months,
                    y=summary.Confirmed,
                    name='Confirmed',
                    marker_color='blueviolet'
                    ))
    fig.add_trace(go.Bar(x=Months,
                    y=summary.Recovered,
                    name='Recovered',
                    marker_color='royalblue'
                    
                    ))
    fig.add_trace(go.Scatter(x=Months,
                    y=summary.Deaths,
                    name='Deaths',
                    marker_color='gold',    
                
                    ))
    fig.add_trace(go.Scatter(x=Months,
                    y=summary.Active,
                    name='Active',
                    marker_color='crimson',
                    line_width = 2
                    ))

    fig.update_traces( marker_line_color='black',marker_line_width=0.1)
                  

    fig.update_layout(
        title='Time Series Plot of {}'.format(region),
        xaxis_tickfont_size=14,
        template = theme,
        yaxis=dict(
            title='Covid19 Reported Number of Cases',
            titlefont_size=16,
            tickfont_size=14,
        ),
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        barmode='group',
        bargap=0.2, 

    )
    
    return fig

   

@st.cache(persist=True)
def preprocessing1(CountryName,confirmed_df,recovered_df,deaths_df):
    month = { 1:'Jan', 2:'Feb', 3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sept',10:'Oct',
         11:'Nov',12:'Dec'}
    
    if len(CountryName) == 1 :
        country_summary = confirmed_df[confirmed_df['Country/Region'] == CountryName[0]].drop(['Province/State','Country/Region','Lat','Long'],axis=1).T
        country_summary['Recovered'] = recovered_df[recovered_df['Country/Region'] == CountryName[0]].drop(['Province/State','Country/Region','Lat','Long'],axis=1).T
        country_summary['Deaths'] = deaths_df[deaths_df['Country/Region'] == CountryName[0]].drop(['Province/State','Country/Region','Lat','Long'],axis=1).T
        country_summary.columns = ['Confirmed','Recovered','Deaths']
        country_summary['Active'] = country_summary['Confirmed'] - country_summary['Recovered'] - country_summary['Deaths']
        country_summary.index = pd.to_datetime(country_summary.index)
        country_summary['Months'] = country_summary.index
        country_summary['Month_Year'] = pd.to_datetime(country_summary['Months']).dt.strftime('%Y-%m-%d')

        country_summary['Months_num'] = country_summary['Months'].dt.month
        country_summary['Months'] = country_summary['Months'].dt.month
        country_summary['Months'] = pd.to_datetime(country_summary['Months'])
        country_summary['Months'] = country_summary['Months_num'].map(month)
        return country_summary
    
        
    

@st.cache(persist=True)
def province_check_confirmed(CountryName,confirmed_df):

    if len(confirmed_df[confirmed_df['Country/Region'] == CountryName]) > 1:
        transformed_confirmed = pd.DataFrame(confirmed_df[confirmed_df['Country/Region'] ==CountryName].sum()).T
        transformed_confirmed.iat[0,1] = CountryName
        return transformed_confirmed 

    else:
        return confirmed_df

@st.cache(persist=True)
def province_check_recovered(CountryName,recovered_df):

    if len(recovered_df[recovered_df['Country/Region'] == CountryName]) > 1:
        transformed_recovered = pd.DataFrame(recovered_df[recovered_df['Country/Region'] ==CountryName].sum()).T
        transformed_recovered.iat[0,1] = CountryName
        return transformed_recovered

    else:
        return recovered_df

@st.cache(persist=True)
def province_check_deaths(CountryName,deaths_df):

    if len(deaths_df[deaths_df['Country/Region'] == CountryName]) > 1:
        transformed_deaths = pd.DataFrame(deaths_df[deaths_df['Country/Region'] ==CountryName].sum()).T
        transformed_deaths.iat[0,1] = CountryName
        return transformed_deaths

    else:
        return deaths_df

@st.cache(persist=True)
def RAISE_in_Cases(confirmed_df,CountryName='India'):
    raise_cal = confirmed_df.copy(deep=True)
    raise_cal = raise_cal.drop(['Province/State','Lat','Long'],axis=1)
    raise_cal = raise_cal.drop(np.array(raise_cal.columns)[1:-2],axis=1)
    raise_cal = raise_cal.set_index('Country/Region')
    raise_cal['RAISE'] = np.abs(raise_cal[np.array(raise_cal.columns)[-2:][1]]- raise_cal[np.array(raise_cal.columns)[-2:][0]] )
    net_increase = raise_cal['RAISE'].sum()
    # try, catch
    if len(raise_cal.loc[CountryName,:]) > 3:
        country_raise = dict(raise_cal.loc[CountryName,:].sum())['RAISE']
    
    else:
        country_raise = dict(raise_cal.loc[CountryName,:])['RAISE']
    
    
    return net_increase,raise_cal.columns[:2],country_raise



def Make_contrast_TS_plots(figobj,country_summary,df_list,choice):


    for i,COUNTRY in enumerate(choice,0):

        fig.add_trace(
        go.Scatter(name=COUNTRY, x=country_summary.index, y=df_list[i]['Confirmed']),
        row=1, col=1
        
        )

        fig.add_trace(
            go.Scatter(name=COUNTRY, x=country_summary.index, y=df_list[i]['Recovered']),
            row=1, col=2
            
        )

        fig.add_trace(
            go.Scatter(name=COUNTRY, x=country_summary.index, y=df_list[i]['Deaths']),
            row=1, col=3
            
        )


        fig.add_trace(
            go.Scatter(name=COUNTRY, x=country_summary.index, y=df_list[i]['Active']),
            row=1, col=4
            
        )

    return fig

def Make_contrast_Box_plots(figobj,df_list,choice):
    
    for i,COUNTRY in enumerate(choice,0):
    
        fig.add_trace(
        go.Bar(name=COUNTRY, x=['Confirmed'], y=[df_list[i]['Confirmed'].max()]),
        row=1, col=1
        
        )

        fig.add_trace(
            go.Bar(name=COUNTRY, x=['Recovered'], y=[df_list[i]['Recovered'].max()]),
            row=1, col=2
            
        )

        fig.add_trace(
            go.Bar(name=COUNTRY, x=['Deaths'], y=[df_list[i]['Deaths'].max()]),
            row=1, col=3
            
        )


        fig.add_trace(
            go.Bar(name=COUNTRY, x=['Active'], y=[df_list[i]['Active'].max()]),
            row=1, col=4
            
        )


    return fig



@st.cache(persist=True)
def infectionrate_timeline(confirmed_df,recovered_df,deaths_df):
    month = { 1:'Jan', 2:'Feb', 3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sept',10:'Oct',
         11:'Nov',12:'Dec'}
    confirmed_df = confirmed_df.drop(['Province/State','Lat','Long'],axis=1)
    recovered_df = recovered_df.drop(['Province/State','Lat','Long'],axis=1)
    deaths_df = deaths_df.drop(['Province/State','Lat','Long'],axis=1)
    
    recov_cont = recovered_df['Country/Region'].to_list()
    deaths_cont = deaths_df['Country/Region'].to_list()
    confir_cont = confirmed_df['Country/Region'].to_list()
    
    confirmed_df = confirmed_df.drop('Country/Region',axis=1)
    recovered_df = recovered_df.drop('Country/Region',axis=1)
    deaths_df = deaths_df.drop('Country/Region',axis=1)
    
    df_list = [confirmed_df,recovered_df,deaths_df]
    countryNlist = [confir_cont,recov_cont,deaths_cont]

    transdf_list = []
    for df,countrylist in zip(df_list,countryNlist):
        temp = np.abs(df.diff(axis=1).T)
        temp = temp.drop('1/22/20')
        temp.columns = countrylist
        temp.index = pd.to_datetime(temp.index)
        temp['Months'] = temp.index
        temp['Months_num'] = temp['Months'].dt.month
        temp['Months'] = temp['Months'].dt.month
        temp['Months'] = pd.to_datetime(temp['Months'])
        temp['Months'] = temp['Months_num'].map(month)
        transdf_list.append(temp)
        
    return transdf_list
        
@st.cache(persist=True)
def hikedfslice(y_list,typename):
    
    transformed_y = []
    if typename == 'global':
        for y in y_list:
            y = y.drop(['Months','Months_num'],axis=1)
            transformed_y.append(y.sum(axis=1))
            
        return transformed_y

    else:

        for y in y_list:
            y = y.drop(['Months','Months_num'],axis=1)
            transformed_y.append(y)
        
        return transformed_y

def prophet_subplots(pred_conf,pred_recov,pred_ded):
    fig = make_subplots(rows=1, cols=3)

    # -------------------------------------------
    #   Confirmed
    # -------------------------------------------
    fig.add_trace(go.Scatter(x=pred_conf['ds'],
                    y=pred_conf['yhat'][:-daysinfuture],
                    name='Confirmed',
                    mode='lines',
                    legendgroup="group0",
                    marker_color='magenta',
                    fill='tozeroy',
                    
                ),row=1, col=1)

    fig.add_trace(go.Scatter(x=pred_conf['ds'][-daysinfuture:],
                    y=pred_conf['yhat'][-daysinfuture:],
                    name='Predicted',
                    legendgroup="group0",
                    marker_color='royalblue',
                            mode='lines',
                            fill='tozeroy',
                        
                    ),row=1, col=1)

    fig.add_trace(go.Scatter(x=pred_conf['ds'][-daysinfuture:],
                    y=pred_conf['yhat_upper'][-daysinfuture:],
                    name='Upper-Threshold',
                    legendgroup="group0",
                    mode='lines',
                    marker_color='crimson',
                        

                    ),row=1, col=1)
    fig.add_trace(go.Scatter(x=pred_conf['ds'],
                    y=pred_conf['yhat_lower'],
                    name='Lower-Threshold',
                    legendgroup="group0",
                    marker_color='black',
                        

                    ),row=1, col=1)
    # -------------------------------------------
    #   Recovered
    # -------------------------------------------

    fig.add_trace(go.Scatter(x=pred_recov['ds'],
                    y=pred_recov['yhat'][:-daysinfuture],
                    name='Recovered',
                    mode='lines',
                    legendgroup="group1",
                    marker_color='magenta',
                    fill='tozeroy',
                        
                ),row=1, col=2)

    fig.add_trace(go.Scatter(x=pred_recov['ds'][-daysinfuture:],
                    y=pred_recov['yhat'][-daysinfuture:],
                    name='Predicted',
                    marker_color='royalblue',
                            mode='lines',
                            legendgroup="group1",
                            fill='tozeroy',
                        
                    ),row=1, col=2)

    fig.add_trace(go.Scatter(x=pred_recov['ds'][-daysinfuture:],
                    y=pred_recov['yhat_upper'][-daysinfuture:],
                    name='Upper-Threshold',
                    legendgroup="group1",
                    mode='lines',
                    marker_color='crimson',
                        
                    ),row=1, col=2)

    fig.add_trace(go.Scatter(x=pred_recov['ds'],
                    y=pred_recov['yhat_lower'],
                    name='Lower-Threshold',
                    legendgroup="group1",
                    marker_color='black',
                        
                    ),row=1, col=2)

    # -------------------------------------------
    #   Dead
    # -------------------------------------------
    fig.add_trace(go.Scatter(x=pred_ded['ds'],
                    y=pred_ded['yhat'][:-daysinfuture],
                    name='Deaths',
                    mode='lines',
                    legendgroup="group2",
                    marker_color='magenta',
                    fill='tozeroy',
                        
                ),row=1, col=3)

    fig.add_trace(go.Scatter(x=pred_ded['ds'][-daysinfuture:],
                    y=pred_ded['yhat'][-daysinfuture:],
                    name='Predicted',
                    marker_color='royalblue',
                            mode='lines',
                            legendgroup="group2",
                            fill='tozeroy',
                        
                    ),row=1, col=3)

    fig.add_trace(go.Scatter(x=pred_ded['ds'][-daysinfuture:],
                    y=pred_ded['yhat_upper'][-daysinfuture:],
                    name='Upper-Threshold',
                    legendgroup="group2",
                    mode='lines',
                    marker_color='crimson',
                        
                    ),row=1, col=3)

    fig.add_trace(go.Scatter(x=pred_ded['ds'],
                    y=pred_ded['yhat_lower'],
                    name='Lower-Threshold',
                    legendgroup="group2",
                    marker_color='black',
                        
                    ),row=1, col=3)

    # -------------------------------------------

    fig.update_xaxes(title_text="Confirmed", row=1, col=1)
    fig.update_xaxes(title_text="Recovered", row=1, col=2)
    fig.update_xaxes(title_text="Deaths", row=1, col=3)

    
            
        
    return fig




@st.cache(persist=True)
def prophet_prediction_engine(daysinfuture,Model_select,trans_conf):

    # Model Selection
    with open('./models/Model-Confirmed/{}.pkl'.format(Model_select), 'rb') as f:
        model_conf = pickle.load(f)

    with open('./models/Model-Recovered/{}.pkl'.format(Model_select), 'rb') as f:
        model_rec = pickle.load(f)

    with open('./model-Deaths/{}.pkl'.format(Model_select), 'rb') as f:
        model_ded = pickle.load(f)



    # Genertor, Future dates in ds
    start = '1/22/2020'
    start_date = datetime.strptime(start, '%m/%d/%Y')
    future_forcast_dates = []
    for i in range(len(trans_conf)+daysinfuture):
        future_forcast_dates.append((start_date + timedelta(days=i)).strftime('%Y-%m-%d'))
    future = pd.DataFrame(pd.Series(future_forcast_dates[:],name='ds'))
    
    # future_conf = model_conf.make_future_dataframe(periods=daysinfuture)
    # future_recov = model_rec.make_future_dataframe(periods=daysinfuture)
    # future_ded = model_ded.make_future_dataframe(periods=daysinfuture)


    # predictions
    modelslist = [model_conf,model_rec,model_ded]
    # futuredateslist = [future_conf,future_recov,future_ded]
    records = []
    for model in  modelslist:

        pred = model.predict(future)
        records.append(pred)
    

    return records[0],records[1],records[2]






    
        

   



# THE FIRST PIE CHART DEPICTING THE GLOBAL STATUS OF ALL NUMERICALS 
# st.title('The COVID19 Reconnaissance & Forecasting Web Application')
# st.markdown('_A Statistical look through the data, from the **Inception of this unprecedented event** to a **Brief look into the Uncertain Future.**_')

COVID19 = "<p style='text-align: center ; background-color:crimson; text-shadow: 2px 2px #ff0000; font-size: 60px;'><b>COVID19</b></p>"

st.markdown("<h1 style='text-align:center;'><p style='font-size:60px; text-align:center; font-family:helvetica; font-weight:bold;'>The</p> {} Reconnaissance & Forecasting Web Application</h1>".format(COVID19),unsafe_allow_html=True)
st.markdown("<h6 style='text-align: center ;'>A Statistical look through the data, from the<strong style='font-weight: bold;'> Inception of this unprecedented event</strong> to a <strong style='font-weight: bold;'>Brief look into the Uncertain Future.<strong style='font-weight: bold;'></h6>", unsafe_allow_html=True)

st.markdown('')
st.sidebar.title('The  Shelf of Control')
st.sidebar.markdown('***')

# MULTIPLE DASHBOARDS
dropdown = st.sidebar.beta_expander('Dashboard',expanded=True)
apps = dropdown.radio('controlflow',['Statistical Analysis', 'Prognosis'])


st.sidebar.markdown('***')


if apps == 'Statistical Analysis':
    # CLEARING CACHE
    # caching.clear_cache()

    st.markdown('***')
    st.markdown('''<h2 style='font-family:poppins; text-align:center; font-weight:bold;'>Real-Time Statistical Analysis & Prophet</h2>''',unsafe_allow_html=True)
    st.markdown('***')

    st.markdown('''<h2 style='font-family:poppins; text-align:center;'>Global</h2>''',unsafe_allow_html=True)
    st.markdown('***')

    total_numericals = covidAPI_data_total()
    confirmed_df, deaths_df, recovered_df, agg_df = Data_load(confirmed_url,deaths_url,recovered_url,aggregate_url)
    plot_template = st.sidebar.selectbox('Default Plot Theme',['Light☀️','Dark🌑'],key='VizThemeTemplate')
    
    # Choropleth 
    choropleth = choro_aggregate(agg_df)
    choro_conf, choro_death, choro_recov, choro_active = choropleth
    # chart cofigurations
    r_col = {'palette':'Tealgrn','border':'black','title':'teal'}
    c_col = {'palette':'OrRd','border':'black','title':'black'}
    a_col = {'palette':'PuBu','border':'teal','title':'dodgerblue'}
    d_col = {'palette':'RdGy','border':'firebrick','title':'crimson'}


    # Universal Plot Theme
    if plot_template == 'Dark🌑':
        theme = 'plotly_dark'
    else:
        theme = 'plotly_white'


    st.sidebar.markdown('***') # section break

    if st.sidebar.checkbox('World Status',True):
        
    

        slot = st.empty()
        
        cols = st.beta_columns(4)
        
        attr = st.select_slider('Slide',['Active','Recovered','Confirmed','Deaths'], key='choropleth')
        
        if attr == 'Active':
            fig = choroplethChart(choro_active,'Active',config=a_col)
            slot.plotly_chart(fig,use_container_width=True)
        elif attr == 'Confirmed':
            fig = choroplethChart(choro_conf,'Confirmed',config=c_col)
            slot.plotly_chart(fig,use_container_width=True)
        elif attr == 'Recovered':
            fig = choroplethChart(choro_recov,'Recovered',config=r_col)
            slot.plotly_chart(fig,use_container_width=True)
        elif attr == 'Deaths':
            fig = choroplethChart(choro_death,'Deaths',config=d_col)
            slot.plotly_chart(fig,use_container_width=True)






        st.markdown('***')

         
        

        
        


        st.sidebar.header('Global Statistics📈')
        st.sidebar.markdown(' ') # section break

        # Global Status
        table='''

            **Confirmed** -  ```{:,}```\n
            **Recovered** -  ```{:,}```\n
            **Deaths**$~~~~~$ - ```{:,}```\n
            **Active**$~~~~~$ - ```{:,}```\n
        '''.format(total_numericals['Total Confirmmed'],total_numericals['Total Active'],total_numericals['Total Deaths'],total_numericals['Total Recovered'])

        st.sidebar.write(table)


        # st.sidebar.markdown('***')
        Global_Chart_radio = st.sidebar.selectbox('Visualization type', ['Pie chart', 'Time Series'], key='3')
        if st.sidebar.checkbox('Usage',False):
            
            st.sidebar.markdown('_You use the provided widgets on the right-side top-corner to better usage of this plot. You are able to do stuff like zooming into the plot and You can also click on the `legends` of the plot to switch them off individually, I Suggest you to use the `Toggle Spike Lines` option for better Data point tracing._')

    

        if Global_Chart_radio == 'Time Series':
            temp = []
            
            summary = preprocessing0(confirmed_df, recovered_df, deaths_df)
            

            # Slider_month = st.sidebar.slider('Control the Time (Months)',1,int(summary['Months'].max()),key='iixx1')
            
            # for i in range(1,Slider_month+1):
            #     temp.append(summary[summary['Months'] == i])
            
            # final = pd.concat(temp)
            fig = TimeSeriesPlot(summary,theme)
            st.plotly_chart(fig)
            
            

        
        else:
            labels = list(total_numericals.keys())
            values = list(total_numericals.values())
            st.markdown('**Covid19 Situation, decomposed into Percentiles (Global).**')
            colors = ['lime', 'royalblue', 'crimson', 'blueviolet']
            fig = go.Figure(data=[go.Pie(labels=labels,values=values,pull=[0, 0.2, 0, 0], hole=.3)])
            fig.update_traces(hoverinfo='label+percent+value', textfont_size=20,
                            marker=dict(colors=colors, line=dict(color='#000000', width=2.5)))

            st.plotly_chart(fig)


        # Time Series Hike plot 

        if st.checkbox('Frequency of Reported Cases Global',True):

            y = infectionrate_timeline(confirmed_df,recovered_df,deaths_df)
            y = hikedfslice(y,'global')

            Months = y[0].index 

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=Months,
                            y=y[0],
                            name='Confirmed',
                            marker_color='red'
                            
                            ))
            fig.add_trace(go.Bar(x=Months,
                            y=y[1],
                            name='Recovered',
                            marker_color='dodgerblue'
                            ))
            fig.add_trace(go.Scatter(x=Months,
                            y=y[2],
                            name='Deaths',
                            marker_color='blueviolet',    
                        
                            ))

            fig.update_layout(
                title='Monthwise, Daily Hike in Cases reported Globally',
                xaxis_tickfont_size=14,
                template = theme,
                yaxis=dict(
                    title='Covid19 Reported Number of Cases',
                    titlefont_size=16,
                    tickfont_size=14,
                ),
                legend=dict(
                    x=0,
                    y=1.0,
                    bgcolor='rgba(255, 255, 255, 0)',
                    bordercolor='rgba(255, 255, 255, 0)'
                ),
                barmode='group',
                bargap=0.2, 

            )
            
            st.plotly_chart(fig)

        net_increase,last2dates,_ = RAISE_in_Cases(confirmed_df)
        info0 = '''
                    The Net Hike in Cases Between _Last Two Days_ 
                    **{}** `&` **{}** is : **{:,}**
        '''.format(last2dates[0],last2dates[1],net_increase)
        st.info(info0)




        if st.checkbox('Note!',False):
            st.markdown('_Numericals shown in the plot might not be Comparatively accurate with the prominent sources like [**worldometers**](https://www.worldometers.info/coronavirus/) but will be close enough to get an intuition. Also the last date (present day), might not be the day you are using this Application, Since this data is heavyly relied on [**Johns Hopkins Github**](https://github.com/CSSEGISandData/COVID-19) Repository, its auto-update schema is delayed accordingly with the time zones. One thing you can try, in order to update the data is to press `C` on your keyboard and select `clear cache`, then `Reload` the page. Now all the **Data-Fetch** Operations are performed keeping the data upto date with the Johns Hopkins Data._')
            


        


    st.markdown('***')
    st.markdown('''<h2 style='font-family:poppins; text-align:center;'>Country-Wise</h2>''',unsafe_allow_html=True)
    st.markdown('***')
    # country list fetch 
    st.markdown('***Country Name Input***')

    country_list = covidAPI_country_list()

    if st.checkbox('All Country List',False):
        st.write('Copy a Country Name from the provided list.')
        st.write(country_list)
        st.markdown("_why country name is important? the following figure shows a **brief** workflow of this Application, which is driven by an intial **Country Name Input**._")
        st.image('./assets/WorkFlow.png',width=750,caption='control flow')
        st.markdown('_Note ~ _ "The Prediction Model, only trained on the data collected for the **Top 7 critically hit countries** (shown further in the application)."')



    # Country Input 
    CountryName = st.text_input('Enter the Country Name (Default : India) ','India')
    # /Country Input

    if not CountryName == 'US':
        if CountryName == '':
            raise Exception('Null Value!')


        elif re.search(r"\"",CountryName):
            CountryName = re.sub(r"\"","",CountryName)
            country_dict = covidAPI_data(CountryName)

        elif CountryName not in country_list:

            raise Exception('Invalid Country Name (Check spellings),The input format should be a capitalized Name,\nSelect from the Country List provided if your are recurrently facing the same difficulty.')


        else:

            country_dict = covidAPI_data(CountryName)
    else:

        st.markdown('_US Data synopsis is temporarily deprecated by the CovidAPI due to inconsistency in record maintenance_')

    # st.sidebar.markdown('***')
    # st.sidebar.markdown('The ***`Control-Switches`***, will be activated only when you input a country name.')
    # st.sidebar.markdown('***')

    st.sidebar.markdown('***')
    st.sidebar.subheader('Control the Mechanics⚙️')
    st.sidebar.markdown('***')

    present_date = date.today().strftime("%m/%d/%Y")

    st.sidebar.markdown("Selected Country is : ***{}***".format(CountryName))
    st.sidebar.markdown('***')

    if not CountryName == 'US':
        st.sidebar.subheader('Calculated Fatality and Recovery Rate Percentiles of : {}'.format(CountryName))

        st.markdown("***")

        # Mortality Rate Calc
        st.markdown("***Mortality Rate and Recovery Rate, Percentiles***")

        
        summation_deaths = country_dict.get('deaths')
        summation_Confirmed = country_dict.get('confirmed')
        summation_recovered = country_dict.get('recovered')
        mortality_rate = summation_deaths/summation_Confirmed
        recovery_rate = summation_recovered/summation_Confirmed
        # a Check box to See how mortality is calculated
        st.markdown('**{}**, Fatality Rate as of Date (**{}**)  : **{:.2f}%**'.format(CountryName,present_date,mortality_rate*100))
        st.markdown('**{}**, Recovery Rate as of Date (**{}**) : **{:.2f}%**'.format(CountryName,present_date,recovery_rate*100))

        if st.sidebar.checkbox('Info',True):
            st.sidebar.error('_**Mortality Rate**_ is the proportion of People who **Died** from the Disease to the Total Number of People Infected.')
            st.sidebar.success('_**Recovery Rate**_ is the proportion of People who **Recovered** from the Diesease to the Total Number of People Infected.')
                                
        st.markdown('***')

        st.sidebar.markdown('***')

        st.sidebar.subheader('Synopsis of {}'.format(CountryName))

        CHART_TYPE0 = st.sidebar.selectbox('Visualization type',['Pie Chart','Bar Chart'], key='ix')


        st.markdown('***Field for Country Synopsis Plots ``&`` Time Series Plot***')

        if st.checkbox('Show Country Synopsis Chart','True',key='2903'):
            st.markdown('A **'+CHART_TYPE0+'** _Visualization._')

            if CHART_TYPE0 == 'Pie Chart':

                labels = list(country_dict.keys())
                values = list(country_dict.values())

                colors = ['dodgerblue', 'crimson', 'lime', 'magenta']
                fig = go.Figure(data=[go.Pie(labels=labels,title='Covid19 Situation decomposed into Percentiles ({})'.format(CountryName),titleposition='top left',values=values,pull=[0, 0.2,0, 0],hole=0.3)])
                fig.update_traces(hoverinfo='label+percent+value', textfont_size=20,
                                marker=dict(colors=colors, line=dict(color='#000000', width=2.5)))
                st.plotly_chart(fig)


            elif CHART_TYPE0 == 'Bar Chart':
                x = list(country_dict.keys())
                y = list(country_dict.values())

                colors = ['lightslategray'] * 5
                colors[2] = 'crimson'

                
                fig = go.Figure(data=[go.Bar(x=x, y=y,
                            )])

                fig.update_traces(marker_color=colors, marker_line_color='rgb(0,0,0)',
                                marker_line_width=1.5, opacity=0.9)
                fig.update_layout(template=theme,title_text='Covid19 Situation decomposed into Bars ({})'.format(CountryName))
                st.plotly_chart(fig)


    else:
        st.markdown('***')
        


    if st.checkbox('Frequency of Reported Cases in {}'.format(CountryName),True,key='frequency country plot'):
        
            y = infectionrate_timeline(confirmed_df,recovered_df,deaths_df)
            y = hikedfslice(y,'not-global')
            trans_df = []
            for i,df in enumerate(y,0):
                if pd.DataFrame(df[CountryName]).shape[1] > 1:
                    df = df[CountryName].sum(axis=1)
                    trans_df.append(df)
                else:
                    df = df[CountryName]
                    trans_df.append(df)


            Months = trans_df[0].index 

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=Months,
                            y=trans_df[0],
                            name='Confirmed',
                            marker_color='red'
                            ))
            fig.add_trace(go.Bar(x=Months,
                            y=trans_df[1],
                            name='Recovered',
                            marker_color='dodgerblue'
                            ))
            fig.add_trace(go.Scatter(x=Months,
                            y=trans_df[2],
                            name='Deaths',
                            marker_color='blueviolet',    
                        
                            ))

            fig.update_layout(
                title='Monthwise, Daily Hike in Cases reported in {}'.format(CountryName),
                xaxis_tickfont_size=14,
                template = theme,
                yaxis=dict(
                    title='Covid19 Reported Number of Cases',
                    titlefont_size=16,
                    tickfont_size=14,
                ),
                legend=dict(
                    x=0,
                    y=1.0,
                    bgcolor='rgba(255, 255, 255, 0)',
                    bordercolor='rgba(255, 255, 255, 0)'
                ),
                barmode='group',
                bargap=0.2, 

            )
            
            st.plotly_chart(fig)


    net_increase,last2dates, country_raise = RAISE_in_Cases(confirmed_df,CountryName)
    st.info('The Net Hike in Cases Between _Last Two Days_ in **{}** `&` **{}** in {} is : **{:,}**'.format(last2dates[0],last2dates[1],CountryName,country_raise))
    if st.checkbox('If Zero',(country_raise==0)):
        st.markdown('If this Value is ever `zero`, that means there are same number of cases reported in the last two dates, So, there is no Net Increase in Cases. However, I feel the Value `Zero` is very unlikely, So I believe it to be either **Artificiality** in the Dataset or The Data is **Not Updated** yet.')





    st.sidebar.markdown('***')

    # confirmed_df,recovered_df,deaths_df,_ = Data_load(confirmed_url,deaths_url,recovered_url,aggregate_url)
    trans_conf = province_check_confirmed(CountryName, confirmed_df)
    trans_recov = province_check_recovered(CountryName, recovered_df)
    trans_deaths = province_check_deaths(CountryName, deaths_df)

    country_summary = preprocessing1([CountryName],trans_conf,trans_recov,trans_deaths)


    st.sidebar.subheader("Time Series Plot of {}".format(CountryName))
    if st.checkbox('Show Time Series Chart',True):

        
        # st.write(country_summary)
        

        # Slider_month = st.sidebar.select_slider('Control the Time (Months)',list(country_summary['Month_Year']),key='iixx123')
        
        # Slider_month = country_summary['Month_Year']
        
        # st.write('Slider Month {}'.format(Slider_month))
        # temp0 = []

        # for i in range(1,Slider_month+1):
        #     temp0.append(country_summary[country_summary['Month_Year'] == i])

        # country_concat = pd.concat(temp0)
        fig0 = TimeSeriesPlot(country_summary,theme,region=CountryName)

        st.markdown('**A Time Series** _Visualization._')

        st.plotly_chart(fig0)

        
            


        
        
            



    if st.sidebar.checkbox('intriguing?',False):
        st.sidebar.info('_I felt, the following list of countries had some **Intriguing patterns** in Time Series Plot, While the application was in the testing Phase.Why Intriguing you might ask, from the plot you can clearly see the contrast between people of different regions, reacting to the same contagion.Up Next in the Subplots Section you are enabled to choose any other 3 countries to contrast with the initial one._')
        # st.sidebar.markdown
        intriguing_countries = ['Ecuador','Brazil','US','China','Canada','Spain']
        st.sidebar.code(intriguing_countries)

    st.sidebar.markdown('***')


    st.markdown('***')

    st.markdown('**Field for Contrasting Subplots of the Selected Countries**')

    st.sidebar.subheader('Subplots to Magnify the Intricate Contrasting Details')

    if st.sidebar.checkbox('How does this work?',False):
        subplot_text = '''
        
        The Initial **Country Name** you choose will be the essential object of this application pipeline. For the following subplots, the country you have initially choosen will act a _Pivot_ for the other countries (3 Max) you choose to look
        for the contrasting details, Making it 4 countries on the whole to notice prominent differences in the Timeline.
        
        '''

        st.sidebar.info(subplot_text)


    # side bar text input, right side with the country names 

    typeofsubplot = st.sidebar.selectbox('Select Type of Subplot',['Time Series','Box Plot of Summations'],key='94839285')



    if typeofsubplot == 'Time Series':
        fig = make_subplots(rows=1, cols=4)

        fig.add_trace(
            go.Scatter(name=CountryName, x=country_summary.index, y=country_summary['Confirmed']),
            row=1, col=1
            
        )

        fig.add_trace(
            go.Scatter(name=CountryName, x=country_summary.index, y=country_summary['Recovered']),
            row=1, col=2
            
        )

        fig.add_trace(
            go.Scatter(name=CountryName, x=country_summary.index, y=country_summary['Deaths']),
            row=1, col=3
            
        )


        fig.add_trace(
            go.Scatter(name=CountryName, x=country_summary.index, y=country_summary['Active']),
            row=1, col=4
            
        )



        fig.update_xaxes(title_text="Confirmed", row=1, col=1)
        fig.update_xaxes(title_text="Recovered", row=1, col=2)
        fig.update_xaxes(title_text="Deaths", row=1, col=3)
        fig.update_xaxes(title_text="Active", row=1, col=4)


        fig.update_layout(height=500, width=750,template=theme,title_text="Time Series Plot to Measure the Contrasting Details Between the Countries", showlegend=False)
        
        

        all_countries = list(confirmed_df['Country/Region'].unique())

        
        choice = st.sidebar.multiselect('Type/Pick 3 Countries', all_countries,default=['Ecuador', 'Italy', 'United Kingdom'],key='2141256')
        
        if st.sidebar.checkbox('Note!',False,key='9495859'):
            st.sidebar.markdown('This Widget allows a user to select **more than 3** attributes, but considering the **Consequences of higher computation**, I explicitly limited it to be **only 3**, even if one chooses more than 3 options.')

        try:
            if not len(choice)==0 and CountryName not in choice:
                df_list = []
                for CountryName in choice[:3]:
                    trans_conf = province_check_confirmed(CountryName, confirmed_df)
                    trans_recov = province_check_recovered(CountryName, recovered_df)
                    trans_deaths = province_check_deaths(CountryName, deaths_df)
                    temp = preprocessing1([CountryName],trans_conf,trans_recov,trans_deaths)
                    df_list.append(temp)

                # returned obj 
                fig = Make_contrast_TS_plots(fig,country_summary,df_list,choice[:3]) 

                if st.checkbox('Show Subplots',True,key='3938472'):
                    st.plotly_chart(fig)

            else:
                st.error('Please Select 3 Countries & Make sure that you do not select the Same Country Name that you intitially did. If It still throws same the Error refresh the page, it might be a cache problem.')

        except KeyError:
            st.error("Please Select 3 Countries or Refresh the Page if the Exception still persists. or Selected Countries Data Might not be consisted to fit into the application's pipeline ")


    elif typeofsubplot == 'Box Plot of Summations':
        st.markdown('**Box Plot of Summations of Selected Countries**')

        # st.write(country_summary['Confirmed'].max())

        all_countries = list(confirmed_df['Country/Region'].unique())
        

        fig = make_subplots(rows=1, cols=4)

        fig.add_trace(
            go.Bar(name=CountryName, x=['Confirmed'], y=[country_summary['Confirmed'].max()]),
            row=1, col=1
            
        )

        fig.add_trace(
            go.Bar(name=CountryName, x=['Recovered'], y=[country_summary['Recovered'].max()]),
            row=1, col=2
            
        )

        fig.add_trace(
            go.Bar(name=CountryName, x=['Deaths'], y=[country_summary['Deaths'].max()]),
            row=1, col=3
            
        )


        fig.add_trace(
            go.Bar(name=CountryName, x=['Active'], y=[country_summary['Active'].max()]),
            row=1, col=4
            
        )



        fig.update_xaxes(title_text="Confirmed", row=1, col=1)
        fig.update_xaxes(title_text="Recovered", row=1, col=2)
        fig.update_xaxes(title_text="Deaths", row=1, col=3)
        fig.update_xaxes(title_text="Active", row=1, col=4)


        fig.update_layout(height=500, width=750,template=theme,title_text="Box Plot Summary of the Countries Selected", showlegend=False)
        
        choice = st.sidebar.multiselect('Type/Pick 3 Countries', all_countries,default=['Ecuador', 'Brazil', 'US'],key='214123536')

        try:

            if not len(choice)==0 and CountryName not in choice:
                df_list = []
                for CountryName in choice[:3]:
                    trans_conf = province_check_confirmed(CountryName, confirmed_df)
                    trans_recov = province_check_recovered(CountryName, recovered_df)
                    trans_deaths = province_check_deaths(CountryName, deaths_df)
                    temp = preprocessing1([CountryName],trans_conf,trans_recov,trans_deaths)
                    df_list.append(temp)

                # returned obj 
                fig = Make_contrast_Box_plots(fig,df_list,choice[:3]) 

                if st.checkbox('Show Subplots',True,key='3938472'):
                    st.plotly_chart(fig)

            else:
                st.error('Please Select 3 Countries & Make sure that you do not select the Same Country Name that you intitially did. If It still throws the same Error refresh the page, it might be a cache problem.')

        except KeyError:
            st.error('Please Select 3 Countries or Refresh the Page if the Exception still persists.')

    st.markdown('***')
    st.sidebar.markdown('***')



    st.markdown('''<h2 style='font-family:poppins; text-align:center;'>Forecasting the Time-Series Data-Trend Using Prophet</h2>''',unsafe_allow_html=True)
    st.markdown('***')

    st.sidebar.subheader('Predicting the Future - _Prophet_')
    st.subheader("")

    # if st.checkbox('Knowledge',False):
    #     Knowledge = '''
    #     There are 7 Models in Total, which are the `Top-7 Most Critically Hit Countries` (According to the Data) because of _Covid19_. The **Machine Learning** Models are Generated with Help of a Script By iterating it over 7 Countries which are programatically selected and fitting the **Prophet Model** to each Country.
    #     _Prophet_ is an efficient Machine Learning Algorithm within choices when it comes to predicting a Vector of values learning from a **Time Series Data**. It's robust to Outliers, which is mostly observed in this Data as well. For a Detailed Elucidation, I'm also wrote a blog which explains everything employed and observed in this application during
    #     the making, A `Redirection` to the Blog is Added Under the Appendix Section.
        
    #     '''
    #     st.markdown(Knowledge)


    # Model_select = st.sidebar.selectbox('Select a Country for Machine Learning Model Implementation ( Default : India )',['India','US', 'Brazil', 'Russia', 'Argentina', 'Colombia', 'Spain','France'],key='Prophet-Models')
    # daysinfuture = st.sidebar.number_input('Enter Number of Periods(days) in the Future',10,100)


    # Model Changelog 


    expchangelog = st.sidebar.beta_expander(label='Model Changelog')

    expchangelog.markdown('Following is the elucidation of the **Timeline of Changes**, Updated with the **Trained Models** ( countries ) after a significant change observed in the Trend of Reported Cases. Each Generation (```Gen```) linked with a successive list of Countries which were apparently the most effected.')
    expchangelog.markdown('**ChangeLog**')
    expchangelog.markdown('**Gen-I**: ```Models``` - **Epoch** : ```17/10/2020```')
    expchangelog.code('India, US, Brazil, Russia, Argentina, Coloumbia, Spain')
    expchangelog.markdown('**Gen-II**: ```Models``` - **Epoch** : ```5/11/2020```')
    expchangelog.code('US, India, Brazil, Russia, France, Spain, Argentina')




    if expchangelog.checkbox('Note',False):
        expchangelog.markdown('_Note_, Each Changelog corresponds to a Change in the Top7 Critically Hit Countries Based on Which the Models were Generated.')


    # / Model Changelog





    # #prophet-prediction-engine

    # alldates = confirmed_df.drop(['Province/State','Country/Region','Lat','Long'],axis=1).columns


    # pred_conf,pred_recov,pred_ded = prophet_prediction_engine(daysinfuture,Model_select,alldates)

    # # current
    # current_date = trans_conf[trans_conf['Country/Region'] == Model_select].iloc[:,-1:].columns[0]
    # current_conf = trans_conf[trans_conf['Country/Region'] == Model_select].iloc[:,-1:].values[0][0]
    # current_recov = trans_recov[trans_recov['Country/Region'] == Model_select].iloc[:,-1:].values[0][0]
    # current_death = trans_deaths[trans_deaths['Country/Region'] == Model_select].iloc[:,-1:].values[0][0]


    # st.subheader("Prophet-Predictions for **{}**".format(Model_select))
    # st.markdown("**Last Reported Status (``According to Data``) - **{} :-".format(datetime.strptime(current_date, '%m/%d/%y').strftime('%d, %B')))
    # st.markdown('```{:,} Confirmed```, ```{:,} Recovered```, ```{:,} Deaths```'.format(current_conf,current_recov,current_death))
    # st.markdown('***')

    # futuredates = pred_conf['ds'][-daysinfuture:]

    # yhat_conf = pred_conf['yhat'][-daysinfuture:].astype('int64')
    # yhat_recov = pred_recov['yhat'][-daysinfuture:].astype('int64')
    # yhat_ded = pred_ded['yhat'][-daysinfuture:].astype('int64')
    # if daysinfuture <= 20:
    #     attr = st.beta_columns(4)
    #     attr[0].markdown('**Future**')
    #     attr[1].markdown('**Confirmed**')
    #     attr[2].markdown('**Recovered**')
    #     attr[3].markdown('**Deaths**')
    #     for w,x,y,z in zip(futuredates,yhat_conf,yhat_recov,yhat_ded):
    #         cols = st.beta_columns(4)
    #         cols[0].write('```{}```'.format(w.strftime('%d, %B')))
    #         cols[1].write('```{:,}```'.format(x))
    #         cols[2].write('```{:,}```'.format(y))
    #         cols[3].write('```{:,}```'.format(z))

    # else:
    #     st.markdown('This Section Can Hold Only ```20``` Calculated Prediction Records, Please View the **Interactive-Visualisation** to cross-validated your Date-choice. ')
        

    # st.markdown('***')

    # # Plotly Subplot-fucntion call
    # figobj = prophet_subplots(pred_conf,pred_recov,pred_ded)
    # figobj.update_layout(height=500, width=750,template=theme, title_text="Prophet-Predictions in Blue - {}".format(Model_select))



    # if st.checkbox('Visual-Representation',True):
    #     st.plotly_chart(figobj)



    # if st.checkbox('Info',False):

    #     vizinfo = '''

    #     Above is the Visual Representation of the General-Statistical Trend of each attribute ( confirmed, recovered, deaths ) along with the Future Trend forecasted by Prophet.
    #     The predictions made by Prophet are based off of a **Confidence Percentange** (interval-width) which was initially parameterized during the model creation, the choosen percentile was _90%_ which means there's a scope 
    #     of 10% error in the Predictions. The Generated DataFrame Consists the Trends, yhat(predictions), yhat-lower, yhat-upper and many other attributes. Where yhat-lower (Lower-Threshold) and yhat-upper (Upper-Threshold) are
    #     the possibilities of the predicted value getting to lowest and highest point, respectively. 
        
    #     '''
    #     st.markdown(vizinfo)

    st.markdown('* Machine Learning Model (_Prophet_) Section of the Code is temporarily commented out based on the recent observations of inaccurate predictions.')
    st.markdown("* Initial Hypothesis for the Model's inaccurate predictions is believed to be the drastically changing patterns in the Country's data reflecting the reality. ")
    st.markdown("* The Prophet Model _isn't generalising well enough_ for the data which is now in a downward trend, Initially it was a rapid upward projection on the TimeSeries on which the Model is trained.")


    st.sidebar.markdown('***')
    st.markdown('***')

    




    st.subheader('$~~~~~~~~~~~~~~~~~~$`Developed` _and_ `Deployed` _by_ **```𝚛𝟶𝚑𝚊𝚗```**')
    st.write("<p style='text-align: center;'><strong>V1.0.3- The Prophet Version</strong></p>",unsafe_allow_html=True)


    st.markdown('***')

    expander_appendix = st.sidebar.beta_expander(label='Appendix')
    if expander_appendix.checkbox('Display',False):
        if plot_template == 'Dark🌑':
            st.image('./assets/BlogCoverB.jpg',width=700)
        else:
            st.image('./assets/BlogCoverL.jpg',width=700)
        st.markdown("Here's my blog about this project elucidating everthing. I validate this project as \n**_A Complex Analysis yet for a Layman_** \n ~ [``click-me``](https://medium.com/swlh/covid-19-data-analysis-from-the-inception-to-predicting-the-uncertain-future-through-machine-ef4c3f0371bc) If you like to read.")






    st.sidebar.markdown('***')


    expander0 = st.sidebar.beta_expander(label='GitHub')
    expander0.markdown('''[<img src='data:image/png;base64,{}' class='img-fluid' width=32 height=32>](https://github.com/r0han99/Covid19-PredictiveAnalysis) <small>Source-Code | Oct 2020</small>'''.format(img_to_bytes("./assets/GitHub.png")), unsafe_allow_html=True)
    expander0.markdown('''[<img src='data:image/png;base64,{}' class='img-fluid' width=32 height=32>](https://github.com/r0han99/) <small>Other Works</small>'''.format(img_to_bytes("./assets/cognitive-intel.png")), unsafe_allow_html=True)


    st.sidebar.markdown('***')




else:
    app()

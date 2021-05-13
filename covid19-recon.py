
# Application GUI dependencies 
import streamlit as st
from streamlit import caching

# Multiple App Access
from src.preconditional import precondition
from src.country import countryViz
from src.world import world_data
from src.vaccine import vaccineStats
from src.about import about


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
vaccinestats_url = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv'
vaccineloc_url = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/locations.csv'

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
def Data_load(confirmed_url,deaths_url,recovered_url,aggregate_url, vaccinestats_url, vaccineloc_url):
    confirmed_df = pd.read_csv(confirmed_url)
    recovered_df = pd.read_csv(recovered_url)
    deaths_df = pd.read_csv(deaths_url)
    aggregate_df = pd.read_csv(aggregate_url)
    vaccine_df = pd.read_csv(vaccinestats_url)
    vaccloc_df = pd.read_csv(vaccineloc_url)

    confirmed_df = confirmed_df.replace(np.nan,'unregistered',regex=True)
    recovered_df = recovered_df.replace(np.nan,'unregistered',regex=True)
    deaths_df = deaths_df.replace(np.nan,'unregistered',regex=True)

    return confirmed_df, deaths_df, recovered_df, aggregate_df, vaccine_df, vaccloc_df


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


def TimeSeriesPlot(summary):

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
        xaxis_tickfont_size=14,
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
        try:
            country_summary = confirmed_df[confirmed_df['Country/Region'] == CountryName[0]].drop(['Province/State','Country/Region','Lat','Long'],axis=1).T
            country_summary['Recovered'] = recovered_df[recovered_df['Country/Region'] == CountryName[0]].drop(['Province/State','Country/Region','Lat','Long'],axis=1).T
            country_summary['Deaths'] = deaths_df[deaths_df['Country/Region'] == CountryName[0]].drop(['Province/State','Country/Region','Lat','Long'],axis=1).T
        except KeyError:
            country_summary = confirmed_df[confirmed_df['Country/Region'] == CountryName[0]].drop(['Province/State','Country/Region'],axis=1).T
            country_summary['Recovered'] = recovered_df[recovered_df['Country/Region'] == CountryName[0]].drop(['Province/State','Country/Region'],axis=1).T
            country_summary['Deaths'] = deaths_df[deaths_df['Country/Region'] == CountryName[0]].drop(['Province/State','Country/Region'],axis=1).T
            
    
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

def mr_rate_timeline(country_summary, CountryName):

    x = country_summary['Deaths']/country_summary['Confirmed']*100
    r = country_summary['Recovered']/country_summary['Confirmed']*100


    mr_chart = go.Figure()
    mr_chart.add_trace(go.Scatter(x=x.index, y=x,
                        mode='lines',
                        name='Mortality',line=dict(color='red', width=2.5,
                                ) ))
    mr_chart.add_trace(go.Scatter(x=r.index, y=r,
                        mode='lines',
                        name='Recovery Rate',line=dict(color='gold', width=2.5,)))
    mr_chart.update_layout(
                    xaxis_title='Timeline',
                    yaxis_title='Rate%')


    return mr_chart



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






def footer():
    

    st.markdown('***')
    st.subheader('$~~~~~~~~~~~~~~~~~~$`Developed` _and_ `Deployed` _by_ **```𝚛𝟶𝚑𝚊𝚗```**')
    # st.write("<p style='text-align: center;'><strong>V1.0.3- The Prophet Version</strong></p>",unsafe_allow_html=True)



    expander_appendix = st.sidebar.beta_expander(label='Blog Post')
    if expander_appendix.checkbox('Display',False):
        st.markdown('***')
        st.image('./assets/BlogCoverB.jpg',width=700)
        st.markdown("Here's my blog about this project elucidating everthing. I affirm this project as \n**_A Complex Analysis yet for a Layman_** \n ~ [``click-me``](https://medium.com/swlh/covid-19-data-analysis-from-the-inception-to-predicting-the-uncertain-future-through-machine-ef4c3f0371bc) If you like to read.")


    expander0 = st.sidebar.beta_expander(label='GitHub')
    expander0.markdown('''[<img src='data:image/png;base64,{}' class='img-fluid' width=32 height=32>](https://github.com/r0han99/Covid19-PredictiveAnalysis) <span style='color:white; font-size:18px; font-style:italic;'>Source-Code | Oct 2020</span>'''.format(img_to_bytes("./assets/GitHub.png")), unsafe_allow_html=True)
    expander0.markdown('''[<img src='data:image/png;base64,{}' class='img-fluid' width=32 height=32>](https://github.com/r0han99/) <span style='color:white; font-size:18px; font-style:italic;' >Other Works</span>'''.format(img_to_bytes("./assets/cognitive-intel.png")), unsafe_allow_html=True)


    st.sidebar.markdown('***')

    
        

   



# THE FIRST PIE CHART DEPICTING THE GLOBAL STATUS OF ALL NUMERICALS 
# st.title('The COVID19 Reconnaissance & Forecasting Web Application')
# st.markdown('_A Statistical look through the data, from the **Inception of this unprecedented event** to a **Brief look into the Uncertain Future.**_')


st.markdown("<h1 style='text-align:center;'><p style='font-size:55px; text-align:center; font-family:Montserrat; font-weight:normal;'>The <span style='color:red;'>COVID19</span> Web Application<img src='data:image/png;base64,{}' class='img-fluid' width=62 height=62></h1>".format(img_to_bytes('./assets/world.png')),unsafe_allow_html=True)
# st.markdown("<h6 style='text-align: center ;'>A Statistical look through the data, from the<strong style='font-weight: bold;'> Inception of this unprecedented event</strong> to a <strong style='font-weight: bold;'>Brief look into the Uncertain Future.<strong style='font-weight: bold;'></h6>", unsafe_allow_html=True)

st.markdown('')
st.sidebar.title('The Shelf of Control')
st.sidebar.markdown('***')

datevalidity = st.sidebar.empty()

st.sidebar.markdown('***')

# Data Fetch
total_numericals = covidAPI_data_total()
confirmed_df, deaths_df, recovered_df, agg_df, vaccine_df, vaccloc_df = Data_load(confirmed_url,deaths_url,recovered_url,aggregate_url,vaccinestats_url, vaccineloc_url)
    

last_date = confirmed_df.columns[-1]
present_date = date.today().strftime("%m/%d/%Y")
try: 
    day_diff = int(last_date.split('/')[1]) - int(present_date.split('/')[1])
    
    if abs(day_diff) >= 5:      
        prompt = '''_Data Seems to be cached & Old ⚠️, ```Press C, Clear Cache then Reload the Page``` to fetch recent records of Data._'''  
        warn = datevalidity.beta_expander('Old Data ⚠️')
        warn.markdown(prompt)
    else:
        prompt = '''_Data stored in the cache is fairly recent, ```Press C, Clear Cache then Reload the Page``` to fetch recent records of Data._'''
        warn = datevalidity.beta_expander('Fairly Recent Data in cache ✅')
        warn.markdown(prompt)
        
except:
    day_diff = '~'



# MULTIPLE DASHBOARDS
dropdown = st.sidebar.beta_expander('Dashboard',expanded=True)


category = dropdown.selectbox('Category', ['Statistics', 'Machine Learning', 'About'], key='categories')
if category == 'Statistics':
    apps = dropdown.radio('Statistics',['Country-Wise', 'World', 'Vaccinations'], key='Statistics')

elif category == 'Machine Learning':
    apps = dropdown.radio('Machine Learning',['Precondition Based Prognosis'], key='Machine Learning')

else: 
    apps = 'about'
    about()

st.sidebar.markdown('***')


if apps == 'World':
    
    
    # Choropleth 
    choropleth = choro_aggregate(agg_df)
    choro_conf, choro_death, choro_recov, choro_active = choropleth
    choro_conf, choro_death, choro_recov, choro_active = choropleth
    # chart cofigurations
    r_col = {'palette':'Tealgrn','border':'black','title':'teal'}
    c_col = {'palette':'OrRd','border':'black','title':'black'}
    a_col = {'palette':'PuBu','border':'teal','title':'dodgerblue'}
    d_col = {'palette':'RdGy','border':'firebrick','title':'crimson'}
    # Post rendered, Charts are stored in dict
    choropleth = {'Active' : choroplethChart(choro_active,'Active',config=a_col), 
                  'Deaths' : choroplethChart(choro_death,'Deaths',config=d_col),
                  'Confirmed': choroplethChart(choro_conf,'Confirmed',config=c_col),
                  'Recovered':  choroplethChart(choro_recov,'Recovered',config=r_col)}



    # Plot Dict Creation
    choroplot_dict = {'Active': choroplethChart(choro_active,'Active',config=a_col), 'Recovered': choroplethChart(choro_conf,'Confirmed',config=c_col), 'Recovered' : choroplethChart(choro_recov,'Recovered',config=r_col), 'Deaths': choroplethChart(choro_death,'Deaths',config=d_col) }

    # Data Creation
    summary = preprocessing0(confirmed_df, recovered_df, deaths_df)

    

    # Global Pie
    colors = ['lime', 'royalblue', 'crimson', 'blueviolet']
    labels = list(total_numericals.keys())
    values = list(total_numericals.values())
    world_pie = go.Figure(data=[go.Pie(labels=labels,values=values,pull=[0, 0.2, 0, 0], hole=.3)])
    world_pie.update_traces(hoverinfo='label+percent+value', textfont_size=20,
                    marker=dict(colors=colors, line=dict(color='#000000', width=2.5)))

    
    # Frequency of Global Cases 
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
        xaxis_tickfont_size=14,
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
    
    net_increase,last2dates,_ = RAISE_in_Cases(confirmed_df)
    info0 = '''
                The Net Hike in Cases Between _Last Two Days_ 
                **{}** `&` **{}** is : **{:,}**
    '''.format(last2dates[0],last2dates[1],net_increase)
   

    worldTime_dict = {'Time Series':TimeSeriesPlot(summary) ,'World-Pie': world_pie , 'Frequency': (fig,info0) }


    # Redirecting the recorded values to the actual app to render
    world_data(choropleth, total_numericals, worldTime_dict)




        

elif apps == 'Country-Wise':


    st.markdown('***')
    st.markdown('''<h3 style='font-family:poppins; text-align:center;'>Country-Wise Visualisation</h3>''',unsafe_allow_html=True)
    

    
    # country list fetch 
    st.markdown('***')
    st.markdown('***Country Name Input***')

    country_list = covidAPI_country_list()

    # SEND country_list

    if st.checkbox('All Country List',False):
        st.write('Copy a Country Name from the provided list.')
        st.write(country_list)
        st.markdown('***')
        # st.markdown("_why country name is important? the following figure shows a **brief** workflow of this Application, which is driven by an intial **Country Name Input**._")
        # st.image('./assets/WorkFlow.png',width=750,caption='control flow')
        


    # Country Input 
    CountryName = st.text_input('Enter the Country Name (Default : India) ','India')
    # /Country Input


     # Data Manipulation 
    trans_conf = province_check_confirmed(CountryName, confirmed_df)
    trans_recov = province_check_recovered(CountryName, recovered_df)
    trans_deaths = province_check_deaths(CountryName, deaths_df)

    country_summary = preprocessing1([CountryName],trans_conf,trans_recov,trans_deaths)



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

        st.markdown('_United States Data visualisation is temporarily deprecated by the CovidAPI due to inconsistency in record maintenance_')

 


    present_date = date.today().strftime("%m/%d/%Y")

    
 
    
    # MORTALITY AND FATALITY 
    if not CountryName == 'US':
        
        summation_deaths = country_dict.get('deaths')
        summation_Confirmed = country_dict.get('confirmed')
        summation_recovered = country_dict.get('recovered')
        mortality_rate = summation_deaths/summation_Confirmed
        recovery_rate = summation_recovered/summation_Confirmed

        mrchart = mr_rate_timeline(country_summary, CountryName)


        MR = {'Date': present_date, 'Mortality': mortality_rate, 'Recovery': recovery_rate, 'MRchart':mrchart}



    


        # QUANTIFIED SUMMARY
        # pie Chart
        labels = list(country_dict.keys())
        values = list(country_dict.values())
        colors = ['dodgerblue', 'crimson', 'lime', 'magenta']
        pie_chart = go.Figure(data=[go.Pie(labels=labels,titleposition='top left',values=values,pull=[0, 0.2,0, 0],hole=0.3)])
        pie_chart.update_traces(hoverinfo='label+percent+value', textfont_size=20,
                        marker=dict(colors=colors, line=dict(color='#000000', width=2.5)))
        
        # Box Chart 
        x = list(country_dict.keys())
        y = list(country_dict.values())

        colors = ['lightslategray'] * 5
        colors[2] = 'crimson'

        
        box_chart = go.Figure(data=[go.Bar(x=x, y=y,
                    )])

        box_chart.update_traces(marker_color=colors, marker_line_color='rgb(0,0,0)',
                        marker_line_width=1.5, opacity=0.9)
        
        
        quantsum = {'Piechart':pie_chart, 'Barchart': box_chart}

    
    

    # FREQUENCY OF INFECTION REPORTS 
    y = infectionrate_timeline(confirmed_df, recovered_df,deaths_df)
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
        
        xaxis_tickfont_size=14,
        yaxis=dict(
            title='Reported Number of Cases',
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
    

    net_increase,last2dates, country_raise = RAISE_in_Cases(confirmed_df,CountryName)
    freq = {'FreqChart': fig, 'info' : (net_increase,last2dates, country_raise)}
    
    
    
    timeline = TimeSeriesPlot(country_summary)




    
    if CountryName == 'US':
        MR = None
        quantsum = None
        countryViz(CountryName, MR, quantsum, freq, timeline)
    else:
        countryViz(CountryName, MR, quantsum, freq, timeline)

    
    
elif apps == 'Vaccinations':

    # Vaccine Data
    vaccine = {'Vaccine_df': vaccine_df, 'Vaccine_loc': vaccloc_df}
    vaccineStats(vaccine)
        

elif apps == 'Precondition Based Prognosis':
    precondition()




footer()
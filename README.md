# Covid19 Machine Learning ``&`` Data Analytics Application [![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/r0han99/covid19-ml-application/master/covid19-recon.py/+/)

<img width="999" alt="Banner" src="https://user-images.githubusercontent.com/45916202/118280917-481ae080-b4ea-11eb-9cf5-0a9e0cc85aac.png">





This repository is the stronghold for this _Application_ which have tons of Visualisations
and Information about everything covid-19 related

## Timeline of Number of Cases Daily Reported - _India_

<img width="1404" alt="Freq" src="https://user-images.githubusercontent.com/45916202/118281161-903a0300-b4ea-11eb-803d-6656c034c501.png">


## Vaccine Administration - _India_

<img width="1417" alt="Vaccs" src="https://user-images.githubusercontent.com/45916202/118281416-ce372700-b4ea-11eb-8f18-29cb4b901dae.png">




## Blog Post - Abstract

_One might consider Nuclear Warfare and a climatic catastrophe as the biggest failure that humanity could ever experience. However, People Failed to Acknowledge that any Novel infectious disease's emergence can wipe out a significant portion of human existence within no time as they did in the past. Despite the intense studies on the patterns of these epidemic outbreaks, when, where, and how these are triggered is out of comprehension. Severe respiratory disease was reported in Wuhan, Hubei province, China. As of 25 January 2020, at least 1,975 cases had been reported since the first patient was hospitalized on 12 December 2019. After the phylogenetic analysis of the complete viral genome, it was found to be closely related to SARS-like virus which is related to the family Coronaviridae and initially named it as SARS-CoV-2 then later bolted down to the name Covid19. This outbreak highlights the ongoing ability of viral spill-over from animals to cause severe disease in humans._

[(Continuation ...)](https://medium.com/swlh/covid-19-data-analysis-from-the-inception-to-predicting-the-uncertain-future-through-machine-ef4c3f0371bc)


## Development Log ⚙️
- **[29/9/2020]**
  Intially Application was Deployed on Heroku. Reported a few Observations, Application had high-latency in rendering Visualisations and also Did not use the Performance Abilities of streamlit's Cache system which was intentionally used, aiming at low reponse time in serving results. Found out the Standard ``dynos`` Setting is alloted for a standard deployments which is not sufficient for a Heavy Application. Deployment was based off of this repository ( GitHub Connection and Integration ).
  
- **[30/9/2020]**
    Streamlit is used to create flawless Front-End Aesthetics and to hold all the front-end Integrated Data Visualisations and Machine Learning Implementation. The app is Deployed on Streamlit Share, because of an *Invitation to test*, offered by a Streamlit's community major, A cloud platform which is now in closed BETA.
    
- **[7/12/2020]** 
  Deployment expired, Initially to generate requirements.txt programtically, I used _Pigar Tool_ which specifically tagged the versions used at that point of time. as of now, some of the modules are updated. so, removing the version tags for each module-name in the requirements.txt and rebooting the deployment installed the newest versions of the modules used in this application. problem resolved, deployment is active.
  
  Note, Deployment on Heroku is taken-down as in it's `Under-maintenance` but it still shows up Under Environments Section of this repository please ignore that. The Only Actively Maintained Deployment is the later. 


## Version TimeLine( ```Changelog``` )

- **[30/9/2020] ~ V 1.0.1** _The Polynomial version_ 
    - Global statistics, Time Series visualisation & pie-chart of percentiles ,
    - Frequency of Cases Reported Globally, Time Series Plot,
    - Country Mortality and Recovery Rates,
    - Country-wise Time Series Visualisation and Bar chart of Summations,
    - Country-wise Frequency of Cases Reported, Time Series Plot,
    - Constrasting Subplots for the Selected Countries,
    - Polynomial Regression to Predict the Confirmed Cases of any of the Selected 7 Countries ( top7 critically hit countries ). 

- **[17/10/2020] ~ V 1.0.2** _The Prophet Version_
    - Everything From V 1.0.1, Except
    - Polynomial Regression Models are Swapped with Facebook's Prophet Model,
    - Predicts all the Three Attributes (Confirmed, Recovered, Deaths),
    - Conjunctive Time Series Visualisation of Both General Statistical Trend of the Selected Country along with the Trend of Predictions on the Same Graph,
    - Added Global Statistical Summaries (numerical) on the Sidebar at the top,
    - All the Numerical's are well formatted in an International System.

- **[5/11/2020] ~ V 1.0.2** _Retrain Cycle I, Gen-II_
  - Retrained the models to incorporate the significant changes in the trend of reported cases for better predictions
  - Added a ChangeLog of the Model Retrain Cycles for better comprehension. 
  
- **[11/1/2021] ~ V 1.0.2** _Bug Elimination_ 

  - Remodeled TimeSeriesPlots, incorporating 2021's data and removed the Month slider
  - US data acess from CovidAPI is deprecated temporarily
  - Changed Artwork
  - Removed Recovered Plot from the Frequency plots on observing the inconsistencies within the data
  - TimeSeries subplot's now shows 3 new countries as default
  
- **[23/3/2021] ~ V1.0.3** *Segregated Dashboard*

    - Front-End Updates

        - Section based Titles are mentioned
        - Plot colors are changed
        - Streamlit's system based theme configuration  
    - Changed paths to incorporate the changes in the repo 

* **[25/3/2021]** ~ **V1.0.3** *Choropleth*

    * Utilized Aggregate data to visualise a Choropleth Map
    * Banner is now replaced by Choropleth Map

* **[12/5/2021]** ~ *De-Clutter + Re-Organisation*

  * Changed Title into a Simpler one
  * Redesigned Front-End
  * Segregated Different Sections to many apps
  * Country Flag Assets
  * Dropped prophet & Constrasting Plots
  
* **[13/5/2021]** ~ *Vaccine Administration Radio-Page*

  * Fixed bugs
  * Mortality and Recovery Rate Timeline Chart
  * All About Vaccinations   
  * Vaccines and Manufacturers    
  * Countrywise, percentage of Vaccines Administered ( Fully Vaccinated , One-Shot ( Partially ) Vaccinated )
  * Cache Status Checking functionality

* **[14/5/2021]** ~ *Re-Organisation Complete*

   * Vaccine Page re-Organisation
      * Vaccinations of the world
          * Information about all the Vaccines available
      * Vaccine Administration
          * Percentage description of Vaccine Administration in Countries
    * Fixed some front-end issues
    * Default theme setup with config.toml

***





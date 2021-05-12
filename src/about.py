import streamlit as st



def about():
    st.markdown('***')
    st.markdown('''<h3 style='font-family:poppins; text-align:center;'>About</h3>''',unsafe_allow_html=True)

    st.image('./assets/covid.png')

    Abstract = '''

    One might consider Nuclear Warfare and a climatic catastrophe as the biggest failure that humanity could ever experience. However, People Failed to Acknowledge that any Novel infectious disease's emergence can wipe out a significant portion of human existence within no time as they did in the past. Despite the intense studies on the patterns of these epidemic outbreaks, when, where, and how these are triggered is out of comprehension. Severe respiratory disease was reported in Wuhan, Hubei province, China. As of 25 January 2020, at least 1,975 cases had been reported since the first patient was hospitalized on 12 December 2019. After the phylogenetic analysis of the complete viral genome, it was found to be closely related to SARS-like virus which is related to the family Coronaviridae and initially named it as SARS-CoV-2 then later bolted down to the name Covid19. This outbreak highlights the ongoing ability of viral spill-over from animals to cause severe disease in humans.

    '''

    st.markdown('{}'.format(Abstract))
import streamlit as st
from streamlit_folium import folium_static
import json
import folium
import requests
import pandas as pd
from pandas.io.json import json_normalize
import plotly
import plotly.express as px


def main():

    st.markdown("<h1 style='text-align: center; color: #ff634d;'><strong>COVID</strong>-19 ANALYSIS</h1>", unsafe_allow_html=True)
    st.markdown("![COVID-19 Picture](https://d2jx2rerrg6sh3.cloudfront.net/image-handler/ts/20200420091641/ri/674/picture/2020/4/%40shutterstock_1647268288.jpg)")
    st.markdown("Welcome to our COVID-19 data visualization web app. The purpose of this project is to have a look at the  state of COVID-19 using visualizations from different geographical perspectives. The plots have been created by using data visualization tools such as Plotly and Folium.")
    st.markdown("*1. Global COVID-19 Situation*: We will display a folium map that shows the total cases, total deaths, total confirmed cases . In addition to that, we will display various pie charts and bar charts to understand better how the disease has spread across the globe.")
    st.sidebar.markdown("<h1 style='text-align: center; color: #aaccee;'><strong><u> DASHBOARD</u></strong></h1>", unsafe_allow_html=True)

    st.sidebar.image('https://media.giphy.com/media/dVuyBgq2z5gVBkFtDc/giphy.gif')


    url='https://api.covid19api.com/summary'
    r=requests.get(url,verify=False)
    json=r.json()


    df=pd.DataFrame(json['Countries'])

    covid1=df.drop(columns=['CountryCode','Slug','Date','Premium'],axis=1)
    covid1['ActiveCases'] = covid1['TotalConfirmed']-covid1['TotalRecovered']+covid1['TotalDeaths']
    dfn=covid1.drop(['NewConfirmed','NewDeaths','NewRecovered'],axis=1)
    dfn = dfn.groupby(['Country'])[['TotalConfirmed','TotalDeaths']].sum().sort_values(by='TotalConfirmed',ascending=False)


    dfc = covid1.groupby(['Country'])[['TotalConfirmed','TotalDeaths','TotalRecovered','ActiveCases']].max().sort_values(by='TotalConfirmed',ascending=False).reset_index()


    m = folium.Map(tiles='Stamen Terrain',min_zoom=2)
    url='https://raw.githubusercontent.com/python-visualization/folium/master/examples/data'
    country_shapes = f'{url}/world-countries.json'
    folium.Choropleth(
    geo_data=country_shapes ,
    min_zoom=2,
    name='Covid-19',
    data=covid1,
    columns=['Country','TotalConfirmed'],
    key_on='feature.properties.name',
    fill_color='YlOrRd',
    legend_name='Total Confirmed Cases',
    ).add_to(m)


    m4 = folium.Map(tiles='Stamen Terrain',min_zoom=1.5)
    url='https://raw.githubusercontent.com/python-visualization/folium/master/examples/data'
    country_shapes = f'{url}/world-countries.json'
    folium.Choropleth(
    geo_data=country_shapes,
    min_zoom=2,
    name='Covid-19',
    data=covid1,
    columns=['Country','ActiveCases'],
    key_on='feature.properties.name',
    fill_color='YlOrBr',
    nan_fill_color='black',
    legend_name='Active Cases',
    ).add_to(m4)


    m2 = folium.Map(tiles='Stamen Terrain',min_zoom=1.5)
    url='https://raw.githubusercontent.com/python-visualization/folium/master/examples/data'
    country_shapes = f'{url}/world-countries.json'
    folium.Choropleth(
    geo_data=country_shapes,
    min_zoom=2,
    name='Covid-19',
    data=covid1,
    columns=['Country','TotalDeaths'],
    key_on='feature.properties.name',
    fill_color='YlOrBr',
    nan_fill_color='black',
    legend_name='TotalDeaths',
    ).add_to(m2)

    covid1.update(covid1['TotalConfirmed'].map('Total Confirmed:{}'.format))
    covid1.update(covid1['ActiveCases'].map('Active Cases:{}'.format))
    covid1.update(covid1['TotalDeaths'].map('Total Deaths:{}'.format))

    coordinates = pd.read_csv('https://raw.githubusercontent.com/VinitaSilaparasetty/covid-map/master/country-coordinates-world.csv')
    covid_final = pd.merge(covid1,coordinates,on='Country')

    def plot(p):
        folium.CircleMarker(location=[p.latitude,p.longitude],radius=5,weight=2,popup=[p.Country,p.TotalConfirmed],fill_color='#000000').add_to(m)
    covid_final.apply(plot,axis=1)
    m.fit_bounds(m.get_bounds())

    def plot(p):
        folium.CircleMarker(location=[p.latitude,p.longitude],radius=5,weight=2,popup=[p.Country,p.ActiveCases],fill_color='red').add_to(m4)
    covid_final.apply(plot,axis=1)
    m4.fit_bounds(m4.get_bounds())

    def plot(p):
        folium.CircleMarker(location=[p.latitude,p.longitude],radius=5,weight=2,popup=[p.Country,p.TotalDeaths],fill_color='orange').add_to(m2)
    covid_final.apply(plot,axis=1)
    m2.fit_bounds(m2.get_bounds())


    confirmed_tot = int(dfc['TotalConfirmed'].sum())
    deaths_tot = int(dfc['TotalDeaths'].sum())
    st.sidebar.write("### LIVE")
    st.sidebar.write("## GLOBAL CASES-",confirmed_tot)
    st.sidebar.write("## GLOBAL DEATHS-",deaths_tot)


    st.sidebar.subheader(' MAP ANALYSIS')

    select = st.sidebar.selectbox('Choose Map Type for visualization of',['Confirmed Cases','Active Cases','Deaths'],key='1')


    if select == "Confirmed Cases":
           folium_static(m)

    elif select == "Active Cases":

           folium_static(m4)

    else:

           folium_static(m2)


    st.sidebar.subheader(' BAR CHART ANALYSIS')

    select = st.sidebar.selectbox('Choose Bar Chart for visualization of ',['Confirmed Cases','Active Cases','Deaths'],key='2')


    if select == "Confirmed Cases":
           fig = px.bar(dfc.head(10), y='TotalConfirmed',x='Country',color='Country',height=400)
           fig.update_layout(title=' Total Confirmed Cases of 10 most Affected Countries',xaxis_title='Country',yaxis_title='Total Confirmed Case')
           st.plotly_chart(fig)


    elif select == "Active Cases":

           fig = px.bar(dfc.head(10), y='ActiveCases',x='Country',color='Country',height=400)
           fig.update_layout(title='Active Cases of 10 most Affected Countries',xaxis_title='Country',yaxis_title='Total Recovered')
           st.plotly_chart(fig)


    else:
          fig = px.bar(dfc.head(10), y='TotalDeaths',x='Country',color='Country',height=400)
          fig.update_layout(title=' Total Deaths of 10 most Affected Countries',xaxis_title='Country',yaxis_title='Total Deaths')
          st.plotly_chart(fig)


    st.sidebar.subheader('PIE CHART ANALYSIS')

    select = st.sidebar.selectbox('Choose pie  Chart for visualization of',['Confirmed Cases','Active Cases','Deaths'],key='2')

    if select=="Active Cases":
          fig = px.pie(dfc.head(10), values='ActiveCases',names='Country',title='Active Cases of 10 Most Affected Countries')
          st.plotly_chart(fig)

    elif select=="Confirmed Cases":
          fig = px.pie(dfc.head(10), values='TotalConfirmed',names='Country',title='Total Confirmed cases of 10 Most Affected Countries')
          st.plotly_chart(fig)
    else:
          fig = px.pie(dfc.head(10), values='TotalDeaths',names='Country',title='Total Death cases of 10 Most Affected Countries')
          st.plotly_chart(fig)



    if st.sidebar.checkbox("Show Covid Data",False):
        st.subheader(" Data used for ANALYSIS ")
        st.write(covid1)


if __name__ == '__main__':
    main()


st.markdown("MADE BY SRUTHI ")

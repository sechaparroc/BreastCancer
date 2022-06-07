import time
import dash
import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objs as go
from dash import Input, Output, dcc, html
import pandas as pd
import json
import plotly.express as px
import plotly.io as pio
import os
from pathlib import Path

from . import cancer_data_exploration as eda
from app import app

def geoplotfigure(var = 'Causa', types = []):
    if var == None or var not in eda.cancer_columns:
        var = 'Causa'

    #apply filter
    cancer_department_data = eda.cancer_data
    if len(types) > 0:
        cancer_department_data = eda.cancer_data[eda.cancer_data[var].isin(types)]
    cancer_department_data = cancer_department_data.groupby(['COD_DPTO', 'Departamento'])['Numero_Registros'].sum().reset_index()    
    cancer_department_data = eda.addPopulationInformation(cancer_department_data)
    cancer_department_data['Tasa_muerte'] = cancer_department_data['Numero_Registros'] / cancer_department_data['Poblacion'] * 10000

    fig = px.choropleth_mapbox(cancer_department_data,           #Data
            locations='COD_DPTO',                     #Column containing the identifiers used in the GeoJSON file 
            color='Tasa_muerte',                 #Column giving the color intensity of the region
            geojson=eda.geojson,                          #The GeoJSON file
            featureidkey='properties.DPTO',
            zoom=3.5,                                   #Zoom
            mapbox_style="carto-positron",            #Mapbox style, for different maps you need a Mapbox account and a token
            center={"lat": 4, "lon": -72},            #Center
            color_continuous_scale="Viridis",         #Color Scheme
            opacity=0.5,                              #Opacity of the map
            )

    return fig



def geoplottab():
    # Read the geojson File containing the areas of interest coordinates
    cancer_department_data = eda.cancer_data.groupby(['COD_DPTO', 'Departamento'])['Numero_Registros'].sum().reset_index()    
    cancer_department_data = eda.addPopulationInformation(cancer_department_data)
    cancer_department_data['Tasa_muerte'] = cancer_department_data['Numero_Registros'] / cancer_department_data['Poblacion'] * 10000

    fig = px.choropleth_mapbox(cancer_department_data,           #Data
            locations='COD_DPTO',                     #Column containing the identifiers used in the GeoJSON file 
            color='Tasa_muerte',                 #Column giving the color intensity of the region
            geojson=eda.geojson,                          #The GeoJSON file
            featureidkey='properties.DPTO',
            zoom=3.5,                                   #Zoom
            mapbox_style="carto-positron",            #Mapbox style, for different maps you need a Mapbox account and a token
            center={"lat": 4, "lon": -72},            #Center
            color_continuous_scale="Viridis",         #Color Scheme
            opacity=0.5,                              #Opacity of the map
            )

    controls = dbc.Card(
        [
            html.Div(
                [
                    dbc.Label("variable"),
                    dcc.Dropdown(
                        id="geoplot-var",
                        options=[
                            {"label": col[:15], "value": col} for col in eda.cancer_columns
                        ],
                        value = 'Causa',
                        className = "dash-bootstrap"
                        
                    ),
                ]
            ),
            html.Div(
                [
                    dbc.Label("Categories"),
                    dcc.Dropdown(
                        id="geoplot-var-types",
                        options=[
                            {"label": col[:15], "value": col} for col in eda.cancer_categories
                        ],
                        value = [],
                        multi=True,
                        className = "dash-bootstrap"
                        
                    ),
                ]
            ),
        ],
        body=True,
    )    

    layout = [
        html.H1("Number of deaths Geoplot"),
        html.Hr(),
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(controls, md=3),
                        dbc.Col(
                            [dbc.Row(
                                dbc.Col(
                                    dcc.Graph(figure=fig,id ='geo-plot')
                                )
                            ), 
                            dbc.Row(
                                dbc.Col(
                                    html.Div("Here we can provide some insigths of the data"),
                                    align='center',
                                ),
                                justify="center", align="center" 
                            )],   
                            md=9
                        ),
                    ],
                    justify="center", align="center",
                ),
            ], fluid=True,
        )
    ] 

    return layout


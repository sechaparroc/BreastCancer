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

def barplotfigure(first_var = 'Causa', first_types = [], second_var = 'Sexo', second_types = []):
    if first_var == None or first_var not in eda.cancer_columns:
        first_var = 'Causa'
    if second_var == None or second_var not in eda.cancer_columns:
        second_var = 'Sexo'        

    labels = {"Numero_Registros" : "Número de muertes", "Causa" : "Tipo de cancer"}
    title = "Numero de muertes por tipo de Cancer"

    cancer_deaths = None
    if first_var == second_var:
        cancer_deaths = eda.cancer_data.groupby([first_var])['Numero_Registros'].sum().reset_index()
    else : 
        cancer_deaths = eda.cancer_data.groupby([first_var, second_var])['Numero_Registros'].sum().reset_index()

    if len(first_types) > 0:
        cancer_deaths = cancer_deaths[cancer_deaths[first_var].isin(first_types)]
    if len(second_types) > 0:
        cancer_deaths = cancer_deaths[cancer_deaths[second_var].isin(second_types)]

    if first_var == second_var:
        cancer_deaths = cancer_deaths.sort_values('Numero_Registros', ascending = True)
        fig = px.bar(cancer_deaths, y=first_var, x='Numero_Registros', barmode = 'group', labels = labels, title = title, height = 600) 
    else :    
        cancer_deaths = cancer_deaths.sort_values(first_var, ascending = True)
        fig = px.bar(cancer_deaths, y=first_var, x='Numero_Registros', color = second_var, barmode = 'group', labels = labels, title = title, height = 600) 
    return fig

def barplottab():
    labels = {"Numero_Registros" : "Número de muertes", "Causa" : "Tipo de cancer"}
    title = "Numero de muertes por tipo de Cancer"

    cancer_deaths = eda.cancer_data.groupby(['Causa'])['Numero_Registros'].sum().reset_index()
    cancer_deaths = cancer_deaths.sort_values('Numero_Registros', ascending = True)

    fig = px.bar(cancer_deaths, y='Causa', x='Numero_Registros', barmode = 'group', labels = labels, title = title, height = 600) 

    controls = dbc.Card(
        [
            html.Div(
                [
                    dbc.Label("First variable"),
                    dcc.Dropdown(
                        id="barplot-var-1",
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
                        id="barplot-var-1-types",
                        options=[
                            {"label": col[:15], "value": col} for col in eda.cancer_categories
                        ],
                        value = [],
                        multi=True,
                        className = "dash-bootstrap"
                        
                    ),
                ]
            ),
            html.Div(
                [
                    dbc.Label("Second variable"),
                    dcc.Dropdown(
                        id="barplot-var-2",
                        options=[
                            {"label": col[:15], "value": col} for col in eda.cancer_columns
                        ],
                        value = "Sexo",
                        className = "dash-bootstrap"
                        
                    ),
                ]
            ),
            html.Div(
                [
                    dbc.Label("Categories"),
                    dcc.Dropdown(
                        id="barplot-var-2-types",
                        options=[
                            {"label": col[:15], "value": col} for col in eda.sex_categories
                        ],
                        value=[],
                        multi=True,
                        className="dash-bootstrap"
                    ),
                ]
            ),
        ],
        body=True,
    )    

    layout = [
        html.H1("Number of deaths Barplots"),
        html.Hr(),
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(controls, md=3),
                        dbc.Col(
                            [dbc.Row(
                                dbc.Col(
                                    dcc.Graph(figure=fig,id ='bar-plot')
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


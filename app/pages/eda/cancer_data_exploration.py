import time
import dash
import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objs as go
from dash import Input, Output, dcc, html, callback

import pandas as pd
import json
import plotly.express as px
import plotly.io as pio

import os
from pathlib import Path

#from . import geo_plots
from components.bars.deaths_barplot import BarPlot

dash.register_page(__name__, path="/data-exploration")

#Define global actions - TODO: Check potential pitfalls with global vars!
#See - https://dash.plotly.com/sharing-data-between-callbacks#why-global-variables-will-break-your-app

def loadMainData():
    path = Path(os.path.dirname(os.path.realpath(__file__)))
    path = path.parent.parent.absolute()

    path = os.path.join(path, 'assets', 'csv', 'muertes2020.csv')
    data = pd.read_csv( path, sep=',', encoding='ISO-8859-1',
                       dtype= {
                           'COD_DPTO' : str,
                           'COD_MUNIC' : str
                        }) .drop(columns='Unnamed: 0')
    
    #Rename cancer categories
    cancer_cats = [cat for cat in data['Causa'].unique()
                   if 'tumor' in cat.lower() and 'maligno' in cat.lower()]

    cancer_labels_map = {
    'Tumor maligno de la mama de la mujer' : 'Seno',
    'Tumor maligno de la próstata': 'Próstata', 
    'Tumor maligno del estómago ' : 'Estómago',
    'Tumor maligno de la tráquea, los bronquios y el pulmón ' : 'Traquea, Bronquios, Pulmón',
    'Tumor maligno del colon, de la unión rectosigmoidea, recto y ano' : 'Colon, Recto, Ano',
    'Tumor maligno del cuello del útero ' : 'Cuello del útero',
    'Todos los demás tumores malignos del tejido linfático, de los órganos hematopoyéticos y de tejidos afines ' : 'T. Linfático, O. hematopoyéticos, T. Afines',
    'Tumor maligno del ovario ' : 'Ovario', 
    'Tumor maligno del páncreas ' : 'Páncreas',
    'Tumor maligno del hígado ' : 'Hígado',
    'Tumor maligno de sitios no especificados' : 'Sitios no especificados',
    'Tumor maligno del encéfalo, del ojo y de otras partes del sistema nervioso central ': 'Encéfalo, Ojo, S. Nervioso Central',
    'Tumor maligno de la vesícula biliar y de las vías biliares ' : 'Vesícula biliar',
    'Tumor maligno de otras partes del útero' : 'Otras parter útero',
    'Todos los demás tumores malignos de otras localizaciones ' : 'Otras localizaciones',
    'Tumor maligno del esófago' : 'Esófago',
    'Tumores malignos del labio, de la cavidad bucal y de la faringe ': 'Labio, Cavidad Bucal, Faringe',
    'Melanoma y otros tumores malignos de la piel' : 'Melanoma, Piel',
    'Todos los demás tumores malignos de los órganos urinarios' : 'O. Urinarios',
    'Tumor maligno de la vejiga urinaria ': 'Vejiga urinaria',
    'Tumor maligno del tiroides y de otras glandulas endocrinas ' : 'Tiroides, Glandulas Endocrinas',
    'Tumor maligno de la laringe ' : 'Laringe',
    'Todos los demás tumores malignos de los órganos digestivos y del peritoneo ' : 'O. Digestivos y Peritoneo',
    'Tumores malignos de sitios mal definidos y secundarios ' : 'Sitios mal definidos, Secundarios',
    'Tumor maligno de los huesos y de los cartilagos articulares': 'Huesos, Cartilagos articulares',
    'Todos los demás tumores malignos de los órganos respiratorios e intratorácicos, excepto tráquea, bronquios y pulmón ' : 'Otros Respiratorios'
    }

    mask = data['Causa'].isin(cancer_cats)
    
    data.loc[mask, 'Causa'] = data.loc[mask, 'Causa'].map(cancer_labels_map) 

    #filtered data
    cancer_data = data[data['Causa'].isin([cancer_labels_map[cat] for cat in cancer_cats])]
    return data, cancer_data 

def loadPopulationData():
    path = Path(os.path.dirname(os.path.realpath(__file__)))
    path = path.parent.parent.absolute()
    path = os.path.join(path, 'assets', 'csv', 'anexo-proyecciones-poblacion-Nacional2018_2070.csv')

    population = pd.read_csv( path, sep=',', encoding='ISO-8859-1', thousands=',',
                       dtype= {
                           'DP' : str,
                           'DPMP' : str
                        }) 
    population_department = population[(population['ÁREA GEOGRÁFICA'] == 'Total') & (population['AÑO'] == 2020)][['DP', 'DPNOM', 'Total Hombres', 'Total Mujeres', 'Total']]
    return population_department

def loadGeojson():
    path = Path(os.path.dirname(os.path.realpath(__file__)))
    path = path.parent.parent.absolute()
    geo_path = os.path.join(path, 'assets', 'geo', 'colombia.geo.json')
    # Read the geojson File containing the areas of interest coordinates
    with open(geo_path) as geo:
        geojson = json.loads(geo.read())
    return geojson

def addPopulationInformation(data):
    data = data.merge(loadPopulationData(), 
                                    left_on = ['COD_DPTO'], 
                                    right_on = ['DP'])
    data = data.drop(columns=['DP', 'DPNOM'])
    data = data.reset_index(drop = True) 
    data = data.rename(columns = {'Total' : 'Poblacion', 
                                  'Total Hombres' : 'Poblacion Hombres', 
                                  'Total Mujeres' : 'Poblacion Mujeres'
                                 })
    return data    

def obtainCategories(data, category):
    #just keep the first 15 
    categories = data[category].unique()
    categories.sort()
    return categories

data, cancer_data = loadMainData()
geojson = loadGeojson()
cancer_categories = obtainCategories(cancer_data, 'Causa')
sex_categories = obtainCategories(cancer_data, 'Sexo')
cancer_columns = ['Causa', 'Sexo', 'Edad', 'Educacion', 'Etnia', 'Area_Residencia', 'Seguridad_social',
 'Numero_Registros', 'Departamento', 'Municipio']


#tabs

# Define instance of the components to use
barplot_component : BarPlot = BarPlot(cancer_data, 'cancer_bars')
barplot_component2 : BarPlot = BarPlot(cancer_data, 'cancer_bars')


#bar_content = bar_plots.barplottab()
#geo_content = geo_plots.geoplottab()

layout = dbc.Container(
    [
        html.H1("Cancer data exploration"),
        html.Hr(),
        dbc.Tabs(
            [
                dbc.Tab(barplot_component.display(), label="Bar plot", tab_id="bar"),
                dbc.Tab(barplot_component2.display(), label="Geo plot", tab_id="geo"),
            ],
            id="tabs",
            active_tab="bar",
        ),
    ]
)


# BAR PLOT CALLBACKS

@callback(
    Output(barplot_component.first_variable_categories_id(), "value"),
    Output(barplot_component.first_variable_categories_id(), "options"),
    Input(barplot_component.first_variable_id(), "value")
)
def update_barplot_var_1_types(variable):
    variable = "Causa" if variable not in cancer_columns else variable
    options=[
        {"label": col[:15], "value": col} for col in obtainCategories(cancer_data, variable)
    ]
    return [], options

# @callback(
#     Output("barplot-var-2-types", "value"),
#     Output("barplot-var-2-types", "options"),
#     Input("barplot-var-2", "value")
# )
# def update_barplot_var_2_types(variable):
#     variable = "Sexo" if variable not in cancer_columns else variable
#     options=[
#         {"label": col[:15], "value": col} for col in obtainCategories(cancer_data, variable)
#     ]
#     return [], options
# 


@callback(
    Output(barplot_component.figure_id(), "figure"),
    Input(barplot_component.first_variable_id(), "value"),
    Input(barplot_component.first_variable_categories_id(), "value"),
    Input(barplot_component.second_variable_id(), "value"),
    Input(barplot_component.second_variable_categories_id(), "value")
)
def render_barplot_content(var1, var1_types, var2, var2_types):
    #update filters
    barplot_component.first_variable = var1
    barplot_component.second_variable = var2
    barplot_component.first_variable_categories = var1_types
    barplot_component.second_variable_categories = var2_types
    return barplot_component.update_figure()


# GEO PLOT CALLBACKS

# @callback(
#     Output("geoplot-var-types", "value"),
#     Output("geoplot-var-types", "options"),
#     Input("geoplot-var", "value")
# )
# def update_barplot_var_1_types(variable):
#     variable = "Causa" if variable not in cancer_columns else variable
#     options=[
#         {"label": col[:15], "value": col} for col in obtainCategories(cancer_data, variable)
#     ]
#     return [], options
# 
# @callback(
#     Output("geo-plot", "figure"),
#     Input("geoplot-var", "value"),
#     Input("geoplot-var-types", "value"),
# )
# def render_geoplot_content(var, var_types):
#     return geo_plots.geoplotfigure(var, var_types)
# 

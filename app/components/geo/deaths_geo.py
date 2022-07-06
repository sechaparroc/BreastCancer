import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objs as go
from dash import dcc, html
import pandas as pd
import plotly.express as px
import numpy as np

class GeoPlot:
    """Represent cancer deaths information using a map with Colombian Departments"""        
    def __init__(self, 
        data: pd.DataFrame, 
        population_data: pd.DataFrame,
        geojson,
        id: str,
        filter_by_column : list = {'Causa' : [], 'Sexo': [], 'Edad': [], 'Educacion': [], 'Etnia': [], 'Area_Residencia': [], 'Seguridad_social': []},
        ):
        self.id = id
        self.data = data
        self.population_data = population_data
        self.geojson = geojson
        self.filter_by_column = filter_by_column

    # Define id names
    def variable_id(self, column):
        return self.id + "_" + column

    def figure_id(self):
        return self.id + "_figure"

    def columns(self):
        return list(self.filter_by_column.keys())


    def obtainCategories(self, category):
        #drop nan values
        categories = self.data[category].dropna().unique()
        categories.sort()
        return categories



    def addPopulationInformation(self, data):
        data = data.merge(self.population_data, 
                                        left_on = ['COD_DPTO'], 
                                        right_on = ['DP'])
        data = data.drop(columns=['DP', 'DPNOM'])
        data = data.reset_index(drop = True) 
        data = data.rename(columns = {'Total' : 'Poblacion', 
                                    'Total Hombres' : 'Poblacion Hombres', 
                                    'Total Mujeres' : 'Poblacion Mujeres'
                                    })
        return data    


    def filter_column(self, data, column,categories = []):
        filtered_data = data
        #apply filter
        if len(categories) > 0:
            filtered_data = filtered_data[filtered_data[column].isin(categories)]
        return filtered_data

    def apply_filter(self):
        filtered_data = self.data
        exist_femenino = False
        exist_masculino = False
        for column, categories in self.filter_by_column.items():
            filtered_data = self.filter_column(filtered_data, column, categories)
            if 'Femenino' in categories: exist_femenino = True
            if 'Masculino' in categories: exist_masculino = True

        pop_to_use = 'Poblacion'
        if not exist_masculino and not exist_femenino:
            pop_to_use = 'Poblacion'
        elif exist_masculino and not exist_femenino:
            pop_to_use = 'Poblacion Hombres'
        elif not exist_masculino and exist_femenino:
            pop_to_use = 'Poblacion Mujeres'
        elif exist_masculino and exist_femenino:
            pop_to_use = 'Poblacion'

        department_data = filtered_data.groupby(['COD_DPTO', 'Departamento'])['Numero_Registros'].sum().reset_index()    
        department_data = self.addPopulationInformation(department_data)
        department_data['Tasa_muerte'] = np.round(department_data['Numero_Registros'] / department_data[pop_to_use] * 10000, 4)
        return department_data


    def update_figure(self):
        """
            Filter the data given the First and Second Variables.
            Generate the Barplot given this information.
        """
        #apply filter
        deparment_data = self.apply_filter()
        fig = px.choropleth_mapbox(deparment_data,        
                locations='COD_DPTO',                      
                color='Tasa_muerte',                      
                geojson=self.geojson,                     
                featureidkey='properties.DPTO',
                zoom=3.5,                                 
                mapbox_style="carto-positron",            
                center={"lat": 4, "lon": -72},            
                color_continuous_scale="jet",         
                opacity=0.5,
                custom_data = ["Departamento", "Numero_Registros", "Poblacion"]                               
                )

        fig.update_traces(
            hovertemplate="<br>".join([
                "Departamento=%{customdata[0]}",
                "Tasa muerte=%{z}",
                "Total muertes=%{customdata[1]}",
                "Total poblacion=%{customdata[2]}",
            ])
        )

        
        return fig


    def display(self):
        """Render this component
        """
        fig = self.update_figure()

        controls = []

        for column in self.filter_by_column:
            controls.append(
                html.Div(
                    [
                        dbc.Label(column),
                        dcc.Dropdown(
                            id=self.variable_id(column),
                            options=[
                                {"label": col[:15], "value": col} for col in self.obtainCategories(column)
                            ],
                            value = [],
                            multi=True,
                            className = "dash-bootstrap"
                            
                        ),
                    ]
                )
            )


        layout = [
            html.H1("Number of deaths Geoplot"),
            html.Hr(),
            dbc.Container(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Card(
                                    controls,
                                    body=True,
                                ), 
                                md=3
                            ),
                            dbc.Col(
                                [dbc.Row(
                                    dbc.Col(
                                        dcc.Graph(figure=fig,id =self.figure_id())
                                    )
                                ), 
                                ],   
                                md=9
                            ),
                        ],
                        justify="center", align="center",
                    ),
                ], fluid=True,
            )
        ] 

        return layout



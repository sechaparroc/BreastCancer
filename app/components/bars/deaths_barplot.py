import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objs as go
from dash import dcc, html
import pandas as pd
import plotly.express as px


class BarPlot:
    """Represent cancer deaths information using Barplots"""        
    def __init__(self, 
        data: pd.DataFrame, 
        id: str,
        first_variable: str = "Causa",
        second_variable: str = 'Sexo',
        register_column: str = "Numero_Registros",
        labels: dict = {"Numero_Registros" : "Número de muertes", "Causa" : "Tipo de cancer"},
        title: str = "Numero de muertes por tipo de Cancer",
        allowed_columns : list = ['Causa', 'Sexo', 'Edad', 'Educacion', 'Etnia', 'Area_Residencia', 'Seguridad_social',]
        ):
        """Constructs a Barplot to visualize cancer deaths data
        Args:
            data (pd.DataFrame): Death data information
            id (str): id name
            first_variable (str, optional): First variable to use. Defaults to "Causa".
            second_variable (str, optional): Second variable to use. Defaults to 'Sexo'.
            labels (str, optional): Rename labels
            title (str, optional): Rename the title of this component.
        """
        self.id = id
        self.data = data
        self.first_variable = first_variable
        self.second_variable = second_variable
        self.register_column = register_column
        self.labels = labels
        self.title =  title
        self.allowed_columns = allowed_columns
        self.first_variable_categories = []
        self.second_variable_categories = []

    # Define id names
    def first_variable_id(self):
        return self.id + "_first"

    def first_variable_categories_id(self):
        return self.id + "_first_categories"

    def second_variable_id(self):
        return self.id + "_second"

    def second_variable_categories_id(self):
        return self.id + "_second_categories"

    def figure_id(self):
        return self.id + "_figure"

    def obtainCategories(self, category):
        #just keep the first 15 
        categories = self.data[category].dropna().unique()
        categories.sort()
        return categories


    def update_figure(self):
        """
            Filter the data given the First and Second Variables.
            Generate the Barplot given this information.
        """
        if self.first_variable == None or self.first_variable not in self.allowed_columns:
            self.first_variable = self.allowed_columns[0]
        if self.second_variable == None or self.second_variable not in self.allowed_columns:
            self.second_variable = self.allowed_columns[1]

        deaths = None
        if self.first_variable == self.second_variable:
            deaths = self.data.groupby([self.first_variable])[self.register_column].sum().reset_index()
        else : 
            deaths = self.data.groupby([self.first_variable, self.second_variable])[self.register_column].sum().reset_index()

        if len(self.first_variable_categories) > 0:
            deaths = deaths[deaths[self.first_variable].isin(self.first_variable_categories)]
        if len(self.second_variable_categories) > 0:
            deaths = deaths[deaths[self.second_variable].isin(self.second_variable_categories)]

        if self.first_variable == self.second_variable:
            deaths = deaths.sort_values(self.register_column, ascending = True)
            fig = px.bar(deaths, y=self.first_variable, x=self.register_column, barmode = 'group',
                labels = self.labels, height = 600, text_auto=True, template="simple_white",
                color_discrete_sequence=px.colors.qualitative.Vivid,) 
        else :    
            deaths = deaths.sort_values(self.first_variable, ascending = True)
            fig = px.bar(deaths, y=self.first_variable, x=self.register_column, color = self.second_variable, 
                barmode = 'group', labels = self.labels, height = 600, text_auto=True, template="simple_white",
                color_discrete_sequence=px.colors.qualitative.Vivid,) 

        return fig


    def display(self):
        """Render this component
        """
        fig = self.update_figure()
        self.first_variable_categories = self.obtainCategories(self.first_variable)
        self.second_variable_categories = self.obtainCategories(self.second_variable)

        controls = dbc.Card(
            [
                html.Div(
                    [
                        dbc.Label("First variable"),
                        dcc.Dropdown(
                            id=self.first_variable_id(),
                            options=[
                                {"label": col[:15], "value": col} for col in self.allowed_columns
                            ],
                            value = self.first_variable,
                            className = "dash-bootstrap"
                            
                        ),
                    ]
                ),
                html.Div(
                    [
                        dbc.Label("Categories"),
                        dcc.Dropdown(
                            id=self.first_variable_categories_id(),
                            options=[
                                {"label": col[:15], "value": col} for col in self.first_variable_categories
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
                            id=self.second_variable_id(),
                            options=[
                                {"label": col[:15], "value": col} for col in self.allowed_columns
                            ],
                            value = self.second_variable,
                            className = "dash-bootstrap"
                            
                        ),
                    ]
                ),
                html.Div(
                    [
                        dbc.Label("Categories"),
                        dcc.Dropdown(
                            id=self.second_variable_categories_id(),
                            options=[
                                {"label": col[:15], "value": col} for col in self.second_variable_categories
                            ],
                            value=[],
                            multi=True,
                            className="dash-bootstrap"
                        ),
                    ]
                ),
            ],
            body=True,
            id = self.id
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
                                        dcc.Graph(figure=fig,id = self.figure_id())
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
    
    def update_categories(self, variable):
        variable = self.allowed_columns[0] if variable not in self.allowed_columns else variable
        options=[
            {"label": col[:15], "value": col} for col in self.obtainCategories(self.data, variable)
        ]
        return [], options

    def update_first_variable_categories(self):
        self.update_categories(self.first_variable)

    def update_second_variable_categories(self):
        self.update_categories(self.second_variable)






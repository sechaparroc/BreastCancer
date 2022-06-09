import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

# Import the main app
from app import app
# Import here the Pages to add
from pages import about_us, contact_us, home
from pages.eda import cancer_data_exploration
from pages.predict import breast_cancer_prediction 

server = app.server

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="/", active="exact")),
        dbc.NavItem(dbc.NavLink("Data Exploration", href="/data-exploration", active="exact")),
        dbc.NavItem(dbc.NavLink("Prediction", href="/prediction", active="exact")),
        dbc.NavItem(dbc.NavLink("About us", href="/about-us", active="exact")),
        dbc.NavItem(dbc.NavLink("Contact us", href="/contact-us", active="exact")),
    ],
    brand="Breast Cancer",
    brand_href="#",
    color="primary",
    dark=True,
)


content = html.Div(id="page-content")
layout = html.Div([dcc.Location(id="url"), navbar, content])

# Set app layout
app.layout = layout

# assemble all layouts 
app.validation_layout = html.Div(
    children = [
        layout, 
        home.layout,
        cancer_data_exploration.layout,
        breast_cancer_prediction.layout,
        about_us.layout,
        contact_us.layout,
    ]
)


# Update content
@app.callback(
    Output(
        component_id='page-content',
        component_property='children',
        ),
    [Input(
        component_id='url',
        component_property='pathname',
        )]
)
def display_page(pathname):
    if pathname == '/':
        return home.layout
    elif pathname == '/data-exploration':
        return cancer_data_exploration.layout
    elif pathname == '/prediction':
        return breast_cancer_prediction.layout
    elif pathname == '/about-us':
        return about_us.layout
    elif pathname == '/contact-us':
        return contact_us.layout
    else:
        return '404'

import dash
from dash import html , dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/about-us")

layout = html.Div(
    dbc.Container(
        [
            html.H1("About us", className="display-3"),
            html.P(
                "Here goes main information...",
                className="lead",
            ),
            html.Hr(className="my-2"),
            html.P(
                "Here goes main information...",
            ),
            html.P(
                dbc.Button("Learn more", color="primary"), className="lead"
            ),
        ],
        fluid=True,
        className="py-3",
    ),
    className="p-3 rounded-3",
)
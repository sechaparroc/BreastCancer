import dash_bootstrap_components as dbc
from dash import html

layout = html.Div(
    dbc.Container(
        [
            html.H1("Contact us", className="display-3"),
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
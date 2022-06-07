import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, State, Output, dcc, html
import plotly.express as px
import dash
from skimage import data
import json
from skimage import io
import plotly.graph_objects as go
import os
from pathlib import Path



from app import app

#global references
figures = dict()
path = Path(os.path.dirname(os.path.realpath(__file__)))
path = path.parent.parent.absolute()
path = os.path.join(path, 'assets', 'imgs', '14155.png')

img = io.imread(path)

def generate_canvas(id, name):

    fig = px.imshow(img)
    fig.update_layout(dragmode="drawrect", 
                      #newshape=dict(opacity=0.45, fillcolor="#94e3b6"),
                      )
    config = {
        "modeBarButtonsToAdd": [
            "drawline",
            "drawopenpath",
            "drawclosedpath",
            "drawcircle",
            "drawrect",
            "eraseshape",
        ]
    }
    
    figures[id] = fig
    
    return [
            html.H5(name, style={ "textAlign": "center"}),
            dcc.Graph(id=id, 
                     className="w-100", 
                     figure=fig, 
                     config=config,
                     style={ "width": "100%"})]

def generate_controls():
    return dbc.Card(
        [
            html.Div(
                [
                    dbc.Label("Choose Image"),
                    dcc.Dropdown(
                        id="x-variable",
                        options=[
                            {"label": col, "value": col} for col in ['a','b','c']
                        ],
                        value="sepal length (cm)",
                        className="dash-bootstrap"
                    ),
                ]
            ),
            html.Div(
                [
                    dbc.Label("Choose model"),
                    dcc.Dropdown(
                        id="y-variable",
                        options=[
                            {"label": col, "value": col} for col in ['a','b','c']
                        ],
                        value="sepal width (cm)",
                        className="dash-bootstrap"
                    ),
                ]
            ),
            html.Div(
                [
                    dbc.Button("Run selected model", color="primary", className="me-1", id ="run-button")
                ],
                style = { 'padding-top' : 20, 'padding-left' : 5}
            ),            
        ],
        body=True,
    )    

def imageRecognitionPage():
    return dbc.Col(
            [
                html.H1("Breast cancer image recognition"),
                html.Hr(),
                dbc.Row(
                    [
                        dbc.Col(generate_controls(), md=2),
                        dbc.Col(generate_canvas("main-canvas", "Main"), md=6),
                        dbc.Col(generate_canvas("selected", "Selected"), md=4),
                    ],

                align="center",
                ),
                dbc.Row(
                    [
                        dbc.Col("", md=2),
                        dbc.Col(generate_canvas("predicted-canvas", "Predicted"), md=10),
                        #dbc.Col(generate_canvas("selected", "Selected"), md=4),
                        html.Pre(id="annotations-data"),
                    ],

                align="center",
                ),
            ]
        )


layout = html.Div(
    [
        imageRecognitionPage()
    ],
    style={"height": "100vh"},
)

@app.callback(
    Output("annotations-data", "children"),
    Output("main-canvas", "figure"),
    Output("selected", "figure"),
    Output("predicted-canvas", "figure"),
    Input("main-canvas", "relayoutData"),
    State("main-canvas", "figure"),
    prevent_initial_call=True,
)
def on_new_annotation(relayout_data, figure):
    if "shapes" in relayout_data:
        last = relayout_data["shapes"][-1]
        relayout_data["shapes"] = [last]
        
        """
        No documentation to do this efficiently
        #fig = go.Figure(figure)
        fig = figures['main-canvas']
        #define how to update properly
        
        fig['layout'] = relayout_data
        fig.update_layout(dragmode="drawrect", 
                          newshape=dict(opacity=0.5, fillcolor="#E222AD"),
                          )
        """
        fig = go.Figure(figure)
        fig.update_shapes(last)        
        
        # Update the figure of the other panel to just show ROI
        # shape coordinates are floats, we need to convert to ints for slicing
        x0, y0 = int(last["x0"]), int(last["y0"])
        x1, y1 = int(last["x1"]), int(last["y1"])
        roi_img = img[y0:y1, x0:x1]
        
        return json.dumps(relayout_data, indent=2), fig, px.imshow(roi_img), px.imshow(roi_img)
    else:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update

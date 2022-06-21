import dash
import dash_bootstrap_components as dbc
from dash import Input, State, Output, dcc, html, callback
import dash
from skimage import io
import os
from pathlib import Path
import numpy as np

from components.image.visualizer import Visualizer
from components.predict.model import Model


dash.register_page(__name__, path="/cancer-prediction")


#global references
path = Path(os.path.dirname(os.path.realpath(__file__)))
path = path.parent.parent.absolute()
models_path = os.path.join(path, 'assets', 'models')
images_path = os.path.join(path, 'assets', 'imgs')

img = io.imread(os.path.join(images_path, '16.png'))
blank_image = 165.0 * np.ones(img.shape).astype('float32')

selector_component : Visualizer = Visualizer(img, 'Image', 'main-canvas')
prediction_component : Visualizer = Visualizer( blank_image, 'Prediction', 'prediction-canvas', False)

# Load prediction models
classical_model = Model("classical", os.path.join(models_path, 'classical_model.h5'), "conv2d_2")


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

layout = html.Div(
    [
        dbc.Col(
            [
                html.H1("Breast cancer image recognition"),
                html.Hr(),
                dbc.Row(
                    [
                        dbc.Col(generate_controls(), md=2),
                        dbc.Col(selector_component.display(), md=5),
                        dbc.Col(prediction_component.display(), md=5),
                    ],
                align="center",
                ),
            ]
        )
    ],
    style={"height": "100vh"},
)

#Callbacks

@callback(
    Output(selector_component.figure_id(), "figure"),
    Output(prediction_component.figure_id(), "figure"),
    Input(selector_component.figure_id(), "relayoutData"),
    prevent_initial_call=True,
)
def on_roi_selection(relayout_data):
    if "shapes" in relayout_data:
        updated_main_fig = selector_component.update_figure(relayout_data)
        roi = selector_component.get_roi(relayout_data)
        # apply prediction
        if roi is not None:
            #roi = classical_model.tint_image(roi)
            roi , _ = classical_model.tint_with_gradcam(roi)
        else:
            roi = blank_image
        updated_pred_fig = prediction_component.update_image(roi) 
        return updated_main_fig, updated_pred_fig
    else:
        return dash.no_update, dash.no_update




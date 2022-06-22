import dash
import dash_bootstrap_components as dbc
from dash import Input, State, Output, dcc, html, callback, ctx
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

# Place here the images
sample_images = [io.imread(os.path.join(images_path, f"sample_{i}.png")) for i in range(0,5)]
blank_image = 165.0 * np.ones((500,500,3)).astype('float32')

# Place here the models
models = dict()
models["Classical"] = Model("classical", os.path.join(models_path, 'classical_model.h5'), "conv2d_2")
models["With regularization"] = Model("classical", os.path.join(models_path, 'classical_model.h5'), "conv2d_2")

# Define prediction modes 
prediction_modes = ['Tint patches', 'Grad-Cam Heatmap', 'Grad-Cam Tint']

selector_component : Visualizer = Visualizer(sample_images[0], 'Image', 'main-canvas')
prediction_component : Visualizer = Visualizer( blank_image, 'Prediction', 'prediction-canvas', False)


def generate_controls():
    return dbc.Card(
        [
            dcc.Store(id='local-data', data = {'model' : 'Classical', 'image' : 0}),
            html.Div(
                [
                    dbc.Label("Choose Image"),
                    dcc.Dropdown(
                        id="image-select",
                        options=[
                            {"label": f"Image {key}", "value": key} for key in range(0,len(sample_images))
                        ],
                        value=0,
                        className="dash-bootstrap"
                    ),
                ]
            ),
            html.Div(
                [
                    dbc.Label("Choose model"),
                    dcc.Dropdown(
                        id="model-select",
                        options=[
                            {"label": key, "value": key} for key in models
                        ],
                        value="Classical",
                        className="dash-bootstrap"
                    ),
                ]
            ),
            html.Div(
                [
                    dbc.Label("Choose prediction mode"),
                    dcc.Dropdown(
                        id="prediction-mode",
                        options=[
                            {"label": key, "value": key} for key in prediction_modes
                        ],
                        value=prediction_modes[0],
                        className="dash-bootstrap"
                    ),
                ]
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

# Update main figure either if a Rect is drawn or if a new image is selected
def update_main_figure_on_rect_draw(relayout_data):
    if "shapes" in relayout_data:
        updated_main_fig = selector_component.update_figure(relayout_data)
        return updated_main_fig
    else:
        return dash.no_update

def update_main_figure_on_choose_img(local_data):
    updated_main_fig = selector_component.update_image(sample_images[local_data['image']])
    return updated_main_fig

@callback(
    Output(selector_component.figure_id(), "figure"),
    Input(selector_component.figure_id(), "relayoutData"),
    Input('local-data', 'data'),
    prevent_initial_call=True,
)
def update_main_figure(relayout_data, local_data):
    triggered_id = ctx.triggered_id
    if(triggered_id == selector_component.figure_id()):
        return update_main_figure_on_rect_draw(relayout_data)
    elif(triggered_id == "local-data"):
        return update_main_figure_on_choose_img(local_data)
    return dash.no_update




@callback(
    Output(prediction_component.figure_id(), "figure"),
    Input(selector_component.figure_id(), "relayoutData"),
    State('local-data', 'data'),
    State('prediction-mode', 'value'),
    prevent_initial_call=True,
)
def update_roi_figure_on_selection(relayout_data, local_data, prediction_mode):
    if "shapes" in relayout_data:
        roi = selector_component.get_roi(relayout_data)
        # apply prediction
        # modes: 'Tint patches', 'Grad-Cam Heatmap', 'Grad-Cam Tint'
        if roi is not None:
            if prediction_mode == 'Tint patches':
                roi = models[local_data['model']].tint_image(roi)
            elif prediction_mode == 'Grad-Cam Heatmap':
                _ , roi = models[local_data['model']].tint_with_gradcam(roi)
            elif prediction_mode == 'Grad-Cam Tint':
                roi , _ = models[local_data['model']].tint_with_gradcam(roi)
                
        else:
            roi = blank_image
        updated_pred_fig = prediction_component.update_image(roi) 
        return updated_pred_fig
    else:
        return dash.no_update

@callback(
    Output('local-data', 'data'),
    Input("image-select", "value"),
    Input("model-select", "value"),
    State('local-data', 'data'),
    prevent_initial_call=True,
)
def on_selection(image, model, data):
    if data is None:
        data = dict()
    data['model'] = model 
    data['image'] = image 
    return data


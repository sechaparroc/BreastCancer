from io import BytesIO as bt
import dash
import dash_bootstrap_components as dbc
from dash import Input, State, Output, dcc, html, callback, ctx
import dash
import sys
import skimage
from skimage import io as skio
import io
import requests
from PIL import Image
import pickle
import codecs
from collections import deque
import os
from pathlib import Path
import numpy as np

from components.image.visualizer import Visualizer

dash.register_page(__name__, path="/cancer-prediction")


#global references
BREAST_CANCER_API = "http://127.0.0.1:8050"

path = Path(os.path.dirname(os.path.realpath(__file__)))
path = path.parent.parent.absolute()
images_path = os.path.join(path, 'assets', 'imgs')

# Place here the test images -- Loaded from a S3 Bucket
sample_images = []
for i in range(0,5):
    r = requests.get(url=f'{BREAST_CANCER_API}/image_sample', params={ "num" : str(i)})
    sample_images.append(skio.imread(io.BytesIO(r.content)))


blank_image = 165.0 * np.ones((500,500,3)).astype('float32')

# Place here the models
models = ["classical", "with_regularization"]

# Define prediction modes 
prediction_modes = ['Tint patches', 'Grad-Cam']


selector_component : Visualizer = Visualizer(sample_images[0], 'Image', 'main-canvas')
prediction_component : Visualizer = Visualizer( blank_image, 'Prediction', 'prediction-canvas', False)

def generate_controls():
    return dbc.Card(
        [
            dcc.Store(id='image-data', data = { 'data' : sample_images[0]}),
            dcc.Store(id='local-data', data = {'model' : 'classical', 'image' : 0, 'show-annotations' : False,
            }),
            html.Div(
                [
                    dbc.Label("Filter by"),
                    dcc.Dropdown(
                        id="filter-by",
                        options=[
                            {"label": f"{key}", "value": key} for key in ['Patient Id', 'Proportion', 'Samples']
                        ],
                        value='Samples',
                        className="dash-bootstrap"
                    ),
                ]
            ),
            html.Div(id="patient-id-div", children =
                [
                    dbc.Label("Patient Id"),
                    dcc.Dropdown(
                        id="patient-id",
                        options=[
                        ],
                        value=None,
                        className="dash-bootstrap"
                    ),
                ]
            ),
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
                        value="classical",
                        className="dash-bootstrap"
                    ),
                ]
            ),
            html.Div(
                [
                    dbc.Label("Prediction mode"),
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
            html.Div(
                [
                    dbc.Checklist(
                        options=[
                            {"label": "Show annotations", "value": "show-annotations"},
                        ],
                        value=[],
                        id="switches-input",
                        switch=True,
                    ),
                ],
                style={"margin-left": "15px", "margin-top": "15px"}
            )

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
def update_main_figure_on_rect_draw(relayout_data, figure):
    if "shapes" in relayout_data:
        updated_main_fig = selector_component.update_figure(relayout_data, figure)
        return updated_main_fig
    else:
        return dash.no_update

def update_main_figure_on_choose_img(local_data):
    # load image dinamically

    r = requests.get(url=f'{BREAST_CANCER_API}/image', params={
        "path" : local_data['image']
    })
    img = skio.imread(io.BytesIO(r.content))
    updated_main_fig = selector_component.update_image(img)
    return updated_main_fig, img

@callback(
    Output(selector_component.figure_id(), "figure"),
    Output('image-data', 'data'),
    Input(selector_component.figure_id(), "relayoutData"),
    Input('local-data', 'data'),
    State(selector_component.figure_id(), "figure"),
    prevent_initial_call=True,
)
def update_main_figure(relayout_data, local_data, figure):
    triggered_id = ctx.triggered_id
    if(triggered_id == selector_component.figure_id()):
        return update_main_figure_on_rect_draw(relayout_data, figure), dash.no_update
    elif(triggered_id == "local-data"):
        updated_main_fig, img = update_main_figure_on_choose_img(local_data)
        image_data = {'data' : img}
        return updated_main_fig, image_data
    return dash.no_update, dash.no_update




@callback(
    Output(prediction_component.figure_id(), "figure"),
    Input(selector_component.figure_id(), "relayoutData"),
    State('local-data', 'data'),
    State('image-data', 'data'),
    State('prediction-mode', 'value'),
    prevent_initial_call=True,
)
def update_roi_figure_on_selection(relayout_data, local_data, image_data, prediction_mode):
    if "shapes" in relayout_data:
        annotations = []
        arr = np.array(image_data['data']).astype('uint8')

        roi = selector_component.get_roi(relayout_data, arr)
        # apply prediction
        # modes: 'Tint patches', 'Grad-Cam Heatmap', 'Grad-Cam'
        if roi is not None:
            if prediction_mode == 'Tint patches':
                #use API to Tint the patchs
                im = Image.fromarray(roi)
                # save image to an in-memory bytes buffer
                with io.BytesIO() as buf:
                    im.save(buf, format='PNG')
                    im_bytes = buf.getvalue()
                response = requests.post(url=f'{BREAST_CANCER_API}/tint_patches', params={
                    "model_name" : local_data['model']
                }, files= {'roiImg' : im_bytes})

                response_json = response.json() 
                annotations = response_json["annotations"]
                roi = pickle.loads(codecs.decode(response_json["roi"].encode('latin1'), "base64"))

            elif prediction_mode == 'Grad-Cam':
                #use API to Tint the patchs
                im = Image.fromarray(roi)
                # save image to an in-memory bytes buffer
                with io.BytesIO() as buf:
                    im.save(buf, format='PNG')
                    im_bytes = buf.getvalue()
                response = requests.post(url=f'{BREAST_CANCER_API}/tint_gradcam', params={
                    "model_name" : local_data['model']
                }, files= {'roiImg' : im_bytes})

                response_json = response.json() 
                annotations = response_json["annotations"]
                roi = pickle.loads(codecs.decode(response_json["roi"].encode('latin1'), "base64"))
        else:
            roi = blank_image
        updated_pred_fig = prediction_component.update_image(roi) 

        if local_data['show-annotations']:
            for annotation in annotations:
                updated_pred_fig.add_annotation(
                    x=annotation['x'], y=annotation['y'],
                    text=annotation['text'],
                        xref="x",
                        yref="y",
                        showarrow=True,
                        font=dict(
                            family="Courier New, monospace",
                            size=16,
                            color="#ffffff"
                            ),
                        align="center",
                        arrowhead=2,
                        arrowsize=1,
                        arrowwidth=2,
                        arrowcolor="#000000",
                        ax=20,
                        ay=-30,
                        bordercolor="#ffffff",
                        borderwidth=2,
                        borderpad=4,
                        bgcolor="#000000",
                        opacity=0.8
                    )

        return updated_pred_fig
    else:
        return dash.no_update

@callback(
    Output('local-data', 'data'),
    Input("image-select", "value"),
    Input("model-select", "value"),
    Input("switches-input", "value"),
    State('local-data', 'data'),
    prevent_initial_call=True,
)
def on_selection(image, model, switches, data):
    if data is None:
        data = dict()
    data['model'] = model 
    data['image'] = image 
    data['show-annotations'] = 'show-annotations' in switches
    return data

@callback(
   Output(component_id='patient-id-div', component_property='style'),
   Output(component_id='patient-id', component_property='options'),
   [Input(component_id='filter-by', component_property='value')])
def show_hide_dropdowns(value):
    if value == 'Patient Id':
        #get all available patients
        response = requests.get(url=f'{BREAST_CANCER_API}/patient_ids')
        return {'display': 'block'}, [{"label": i, "value": i} for i in response.json()]
    else:
        return {'display': 'none'}, dash.no_update


@callback(
   Output(component_id='patient-id', component_property='value'),
   [Input(component_id='patient-id', component_property='options')],
   prevent_initial_call=True,
   )
def show_hide_dropdowns(options):
    if options is None or len(options) == 0:
        return None
    return options[0]['value']

@callback(
   Output(component_id='image-select', component_property='value'),
   [Input(component_id='image-select', component_property='options')],
   prevent_initial_call=True,
   )
def show_hide_dropdowns(options):
    if options is None or len(options) == 0:
        return None
    return options[0]['value']


@callback(
   Output(component_id='image-select', component_property='options'),
   [Input(component_id='patient-id', component_property='value')],
   prevent_initial_call=True,
   )
def show_patient_images(value):
    #get all available patients
    response = requests.get(url=f'{BREAST_CANCER_API}/obtain_patient_images', params={ "patient_id" : value, "dims" : 500})
    list_response = response.json()
    list_response = list_response[3:] + list_response[0:3]
    options = [{"label": i, "value": path} for i, path in enumerate(list_response)]
    return options


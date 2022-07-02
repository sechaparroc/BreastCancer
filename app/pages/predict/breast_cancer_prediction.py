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

def request_image_sample(num):
    r = requests.get(url=f'{BREAST_CANCER_API}/image_sample', params={ "num" : str(num)})
    return skio.imread(io.BytesIO(r.content))

def request_image(path):
    r = requests.get(url=f'{BREAST_CANCER_API}/image', params={
        "path" : path
    })
    return skio.imread(io.BytesIO(r.content))

#global references
BREAST_CANCER_API = "http://127.0.0.1:8050"

path = Path(os.path.dirname(os.path.realpath(__file__)))
path = path.parent.parent.absolute()
images_path = os.path.join(path, 'assets', 'imgs')

# Place here the test images -- Loaded from a S3 Bucket
blank_image = 165.0 * np.ones((500,500,3)).astype('float32')

# Place here the models
models = ["classical", "with_regularization"]

# Define prediction modes 
prediction_modes = ['Tint patches', 'Grad-Cam']


# initial local data configuration
storage_data = {'model' : 'classical', 'image' : 0, 'show-annotations' : False}
storage_mode = {'mode' : 'Samples'}


selector_component : Visualizer = Visualizer( request_image_sample(0), 'Image', 'main-canvas')
prediction_component : Visualizer = Visualizer( blank_image, 'Prediction', 'prediction-canvas', False)

def patient_controls():
    return [
            html.Div(
                [
                    dbc.Label("Patient Id"),
                    dcc.Dropdown(
                        id="patient-id",
                        options=[],
                        value=None,
                        className="dash-bootstrap"
                    ),
                ]
            ),
            html.Div(
                [
                    dbc.Label("Choose Image"),
                    dcc.Dropdown(
                        id="patient-image-select",
                        options=[],
                        value=0,
                        className="dash-bootstrap"
                    ),
                ]
            ),
        ]

def proportion_controls():
    return [
            html.Div(
                [
                    dbc.Label("Cancer Proportion"),
                    dbc.Input(id='proportion-number', type="number", min=0, max=1, step=0.1, value=0.5),                    
                ]
            ),
            html.Div(
                [
                    dbc.Label("Patient Id"),
                    dcc.Dropdown(
                        id="proportion-id",
                        options=[],
                        value=None,
                        className="dash-bootstrap"
                    ),
                ]
            ),
            html.Div(
                [
                    dbc.Label("Choose Image"),
                    dcc.Dropdown(
                        id="proportion-image-select",
                        options=[],
                        value=0,
                        className="dash-bootstrap"
                    ),
                ]
            ),
        ]


def sample_controls():
    return [
            html.Div(children =
                [
                    dbc.Label("Choose Image"),
                    dcc.Dropdown(
                        id="sample-image-select",
                        options=[],
                        value=0,
                        className="dash-bootstrap"
                    ),
                ]
            ),
        ]



def generate_controls():
    return dbc.Card(
        [
            dcc.Store(id='image-data', data = dict()),
            dcc.Store(id='local-data', data = storage_data),
            dcc.Store(id='local-image-path', data = dict()),
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
            html.Div( id = "patient-controls", children = patient_controls(), style = {'display': 'none'}),
            html.Div( id = "sample-controls", children = sample_controls()),
            html.Div( id = "proportion-controls", children = proportion_controls(), style = {'display': 'none'}),
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
                html.Span([
                    html.H1("Breast cancer image recognition", style = {'display': 'inline-block'}),
                    html.Span(dcc.Loading( id="loading-id", type = "circle", 
                        children = [   
                            html.Span(id="loading-main-image", style = {'display': 'inline-block'}),
                            html.Span(id="loading-prediction-image", style = {'display': 'inline-block'}),
                        ], style = {'display': 'inline-block'}
                    ), style = {'display': 'inline-block', 'padding-left': 50}),
                    ], 
                ),
                html.Hr(),
                dbc.Row(
                    [
                        dbc.Col(generate_controls(), md=2),
                        dbc.Col(selector_component.display(), md=5),
                        dbc.Col(prediction_component.display(), md=5),
                    ],
                align="center",
                ),
                dbc.Row(
                    [
                        dbc.Col([], md=2),
                        dbc.Col([], md=5),
                        dbc.Col([
                            html.H5(["Region covered with cancer: ", html.H5("-", id="proportion-label", style = {'display': 'inline-block'})]),
                        ], md=5, style={ "textAlign": "center", 'display': 'inline-block'}),
                    ]),


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
    img = request_image(local_data['image'])
    updated_main_fig = selector_component.update_image(img)
    return updated_main_fig, img

@callback(
    Output(selector_component.figure_id(), "figure"),
    Output('image-data', 'data'),
    Output('loading-main-image', "children"),
    Input(selector_component.figure_id(), "relayoutData"),
    Input('local-data', 'data'),
    State(selector_component.figure_id(), "figure"),
    prevent_initial_call=True,
)
def update_main_figure(relayout_data, local_data, figure):
    triggered_id = ctx.triggered_id
    if(triggered_id == selector_component.figure_id()):
        return update_main_figure_on_rect_draw(relayout_data, figure), dash.no_update, ""
    elif(triggered_id == "local-data"):
        if local_data['image'] is None:
            return dash.no_update, dash.no_update, dash.no_update
        updated_main_fig, img = update_main_figure_on_choose_img(local_data)
        image_data = {'data' : img}
        return updated_main_fig, image_data, ""
    return dash.no_update, dash.no_update, dash.no_update




@callback(
    Output(prediction_component.figure_id(), "figure"),
    Output('loading-prediction-image', "children"),
    Output('proportion-label', 'children'),
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

        total_patches = 0
        patches_with_cancer = 0
        for annotation in annotations:
            num = float(annotation['text'])
            if num > 0.5:
                patches_with_cancer += 1
            total_patches += 1 
        prop = round(patches_with_cancer / total_patches, 4) * 100

        return updated_pred_fig, "", f"{prop}%"
    else:
        return dash.no_update, dash.no_update, dash.no_update

@callback(
    Output('local-data', 'data'),
    Input('local-image-path', 'data'),
    Input("model-select", "value"),
    Input("switches-input", "value"),
    State('local-data', 'data'),
    prevent_initial_call=True,
)
def on_selection(image_path, model, switches, data):
    if data is None:
        data = dict()
    if image_path is None:
        return dash.no_update        
    data['model'] = model 
    data['image'] = image_path['path'] 
    data['show-annotations'] = 'show-annotations' in switches
    return data

@callback(
   Output(component_id='patient-controls', component_property='style'),
   Output(component_id='patient-id', component_property='options'),
   Output(component_id='sample-controls', component_property='style'),
   Output(component_id='sample-image-select', component_property='options'),
   Output(component_id='proportion-controls', component_property='style'),
   Output(component_id='proportion-number', component_property='value'),
   [Input(component_id='filter-by', component_property='value')],
   
   )
def upload_after_filter_by(value):
    if value == 'Patient Id':
        #get all available patients
        response = requests.get(url=f'{BREAST_CANCER_API}/patient_ids')
        options = [{"label": i, "value": i} for i in response.json()]
        return {'display': 'block'}, options, {'display': 'none'},dash.no_update, {'display': 'none'},dash.no_update
    elif value == 'Samples':
        response = requests.get(url=f'{BREAST_CANCER_API}/obtain_sample_images')
        list_response = response.json()
        options = [{"label": i, "value": path} for i, path in enumerate(list_response)]
        return {'display': 'none'}, dash.no_update, {'display': 'block'}, options, {'display': 'none'},dash.no_update 
    elif value == 'Proportion':
        return {'display': 'none'}, dash.no_update, {'display': 'none'}, dash.no_update, {'display': 'block'}, 0.5 


# Core functionality to fetch images when we filter by Patient ID
@callback(
   Output(component_id='patient-id', component_property='value'),
   [Input(component_id='patient-id', component_property='options')],
   prevent_initial_call=True,   
   )
def upload_patient_id(options):
    if options is None or len(options) == 0:
        return None
    return options[0]['value']

@callback(
   Output(component_id='patient-image-select', component_property='options'),
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


@callback(
   Output(component_id='patient-image-select', component_property='value'),
   [Input(component_id='patient-image-select', component_property='options')],
   prevent_initial_call=True,
   )
def upload_patient_image(options):
    if options is None or len(options) == 0:
        return None
    return options[0]['value']

# Core functionality to fetch images when we filter by Samples
@callback(
   Output(component_id='sample-image-select', component_property='value'),
   [Input(component_id='sample-image-select', component_property='options')],
   prevent_initial_call=True,
   )
def upload_sample_image(options):
    if options is None or len(options) == 0:
        return None
    return options[0]['value']

@callback(
    Output('local-image-path', 'data'),
    Input("patient-image-select", "value"),
    Input("sample-image-select", "value"),
    Input("proportion-image-select", "value"),
    State('local-image-path', 'data')
)
def on_path_selection(patient_image, sample_image, proportion_image, data):
    if data is None:
        data = dict()
    triggered_id = ctx.triggered_id
    if(triggered_id == 'patient-image-select'):
        data['path'] = patient_image 
        return data
    elif(triggered_id == 'sample-image-select'):
        data['path'] = sample_image 
        return data
    elif(triggered_id == 'proportion-image-select'):
        data['path'] = proportion_image 
        return data

# Core functionality to fetch images when we filter by Proportion
@callback(
   Output(component_id='proportion-id', component_property='options'),
   [Input(component_id='proportion-number', component_property='value')],
   prevent_initial_call=True,
   )
def update_proportion_value(value):
    #get all available patients
    response = requests.get(url=f'{BREAST_CANCER_API}/obtain_patient_by_cancer_proportion', params = {
         "cancer_proportion" : value
    })
    options = [{"label": i, "value": i} for i in response.json()]
    return options

@callback(
   Output(component_id='proportion-id', component_property='value'),
   [Input(component_id='proportion-id', component_property='options')],
   prevent_initial_call=True,
   )
def update_proportion_id(options):
    if options is None or len(options) == 0:
        return None
    return options[0]['value']

@callback(
   Output(component_id='proportion-image-select', component_property='options'),
   [Input(component_id='proportion-id', component_property='value')],
   prevent_initial_call=True,
   )
def show_proportion_images(value):
    #get all available patients
    response = requests.get(url=f'{BREAST_CANCER_API}/obtain_patient_images', params={ "patient_id" : value, "dims" : 500})
    list_response = response.json()
    list_response = list_response[3:] + list_response[0:3]
    options = [{"label": i, "value": path} for i, path in enumerate(list_response)]
    return options


@callback(
   Output(component_id='proportion-image-select', component_property='value'),
   [Input(component_id='proportion-image-select', component_property='options')],
   prevent_initial_call=True,
   )
def update_proportion_image(options):
    if options is None or len(options) == 0:
        return None
    return options[0]['value']






 #   prevent_initial_call=True,

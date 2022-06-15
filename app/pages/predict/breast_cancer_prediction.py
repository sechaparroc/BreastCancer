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

import tensorflow as tf
import cv2
import numpy as np
import math


from app import app
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"


#global references
figures = dict()
path = Path(os.path.dirname(os.path.realpath(__file__)))
path = path.parent.parent.absolute()
models_path = os.path.join(path, 'assets', 'models')
path = os.path.join(path, 'assets', 'imgs', '3.png')
classical_model = tf.keras.models.load_model(os.path.join(models_path, 'classical_model.h5'))

#TF Section
#see https://stackoverflow.com/questions/46020894/superimpose-heatmap-on-a-base-image-opencv-python
#given a large image tint with a red color the zones with cancer 
def tint_image(roi_img):
    roi_img = roi_img / 255.0 
    PW = 50
    PH = 50

    #make the input shape of the roi image a multiple of PW and PH
    width_mod = roi_img.shape[1] % PW
    lower_width = min(roi_img.shape[1] - width_mod, PW)
    upper_width = roi_img.shape[1] + PW - width_mod
    #desired_width =  lower_width if abs(roi_img.shape[1] - lower_width) <= abs(roi_img.shape[1] - upper_width) else upper_width
    desired_width = upper_width

    height_mod = roi_img.shape[0] % PH
    lower_height = min(roi_img.shape[0] - height_mod, PH)
    upper_height = roi_img.shape[0] + PH - height_mod
    #desired_height =  lower_height if abs(roi_img.shape[0] - lower_height) <= abs(roi_img.shape[0] - upper_height) else upper_height
    desired_height = upper_height


    print("des")
    print(desired_height)
    print(desired_width)
    print("--")

    border_left =  math.floor(abs(desired_width - roi_img.shape[1]) / 2)
    border_right = math.ceil(abs(desired_width - roi_img.shape[1]) / 2)
    border_top = math.floor(abs(desired_height - roi_img.shape[0]) / 2)
    border_bottom = math.ceil(abs(desired_height - roi_img.shape[0]) / 2)

    print(roi_img.shape)

    print("borders")
    print(border_left,border_right,border_bottom,border_top)

    input_image = cv2.copyMakeBorder(
        roi_img,
        top=border_top,
        bottom=border_bottom,
        left=border_left,
        right=border_right,
        borderType=cv2.BORDER_CONSTANT,
        value=[0, 0, 0]
    )

    print("Start")
    print(input_image.shape)

    mask = np.zeros((input_image.shape[0], input_image.shape[1], 1))
    print("Mask")
    print(mask.shape)
    for row in range(0,input_image.shape[0],PH):
        for col in range(0,input_image.shape[1],PW):
            print(col,row)
            patch = input_image[row:row+PH, col:col+PW, :]
            print(patch.shape)
            y_pred = classical_model.predict(patch.reshape((1,PH,PW,3)), verbose = 0)
            mask[row:row+PH, col:col+PW, 0] =  1 - 1 * y_pred[0][0]
    print("End")

    mask = 255 * mask 
    mask = mask.astype(np.uint8)
    print("Mean")
    print(np.mean(mask))
    mask = cv2.GaussianBlur(mask,(9,9), 7)

    heatmap_mask = cv2.applyColorMap(mask, cv2.COLORMAP_JET)


    return cv2.addWeighted(heatmap_mask, 0.3, (input_image * 255).astype(np.uint8), 0.7, 0) 
#END OF TF Section



img = io.imread(path)
pred_img = img


def generate_canvas(id, name):
    im = img
    if id == "predicted-canvas":
        im = pred_img

    fig = px.imshow(im)
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
                        dbc.Col(generate_canvas("predicted-canvas", "Predicted"), md=4),
                    ],

                align="center",
                ),
                dbc.Row(
                    [
                        dbc.Col("", md=2),
                        #dbc.Col(generate_canvas("predicted-canvas", "Predicted"), md=10),
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
    Output("predicted-canvas", "figure"),
    Input("main-canvas", "relayoutData"),
    State("main-canvas", "figure"),
    prevent_initial_call=True,
)
def on_new_annotation(relayout_data, figure):
    if "shapes" in relayout_data:
        last = relayout_data["shapes"][-1]
        relayout_data["shapes"] = [last]

        fig = go.Figure(figure)
        fig.update_shapes(last)        
        
        # Update the figure of the other panel to just show ROI
        # shape coordinates are floats, we need to convert to ints for slicing
        x0, y0 = int(last["x0"]), int(last["y0"])
        x1, y1 = int(last["x1"]), int(last["y1"])
        try:
            roi_img = img[y0:y1, x0:x1]
            pred_img = tint_image(roi_img)
            return json.dumps(relayout_data, indent=2), fig, px.imshow(pred_img)
        except:
            return dash.no_update, dash.no_update, dash.no_update    
    else:
        return dash.no_update, dash.no_update, dash.no_update

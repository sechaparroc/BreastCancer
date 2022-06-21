import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objs as go
from dash import dcc, html
import pandas as pd
import plotly.express as px
import numpy as np

class Visualizer():
    """
    Define a rectangular region and return the ROI of a given image
    """
    def __init__(self, 
        image, 
        title,
        id: str,
        interactive: bool = True
        ):
        self.id = id
        self.title = title
        self.interactive = interactive
        self.update_image(image)


    def figure_id(self):
        return self.id + "_figure"

    def update_image(self, image):
        # Generate the initial Figure
        self.image = image
        self.figure = px.imshow(self.image)
        self.figure.update_layout(dragmode="drawrect" if self.interactive else None, 
                        #newshape=dict(opacity=0.45, fillcolor="#94e3b6"),
                        margin=dict(l=5, r=5, b=5, t=5),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'                        
                    )

        self.figure.update_xaxes(showticklabels=False, showgrid=False,  zerolinecolor = 'rgba(0,0,0,0)')
        self.figure.update_yaxes(showticklabels=False, showgrid=False,  zerolinecolor = 'rgba(0,0,0,0)')        
        self.figure.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        })

        if self.interactive:
            self.config = {
                "modeBarButtonsToAdd": [
                    "drawrect",
                    "eraseshape",
                ]
            }
        else:
            self.config = dict()
        return self.figure


    def update_figure(self, relayout_data):
        if "shapes" in relayout_data:
            # keep only the last ROI
            last = relayout_data["shapes"][-1]
            relayout_data["shapes"] = [last]
            self.figure = go.Figure(self.figure)
            self.figure.update_shapes(last)     
            return self.figure
        else:
            return self.figure

    def get_roi(self, relayout_data):
        if not self.interactive:
            return None

        if "shapes" in relayout_data:
            # keep only the last ROI
            last = relayout_data["shapes"][-1]
            relayout_data["shapes"] = [last]
            
            # Return the ROI
            # Shape coordinates are floats, we need to convert to ints for slicing
            x0, y0 = int(last["x0"]), int(last["y0"])
            x1, y1 = int(last["x1"]), int(last["y1"])
            x0, x1 = min(x0,x1), max(x0,x1)
            y0, y1 = min(y0,y1), max(y0,y1)

            try:
                roi_img = self.image[y0:y1, x0:x1]
                return roi_img
            except:
                return None
        else:
            return None

    #DEFINE LAYOUT
    #Helper functions
    def display(self):
        """Render this component
        """
        return [
                html.H5(self.title, style={ "textAlign": "center"}),
                dcc.Graph(id=self.figure_id(),
                        className="w-100", 
                        figure=self.figure, 
                        config=self.config,
                        style={ "width": "100%"})]

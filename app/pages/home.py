from turtle import st
import dash
from dash import html , dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/")

layout = html.Div(
    dbc.Container(
        [
            dbc.Carousel(
            items=[
                {"key": "1", "src": "/assets/imgs/slide01.png"},
            ],
            ride="carousel",
            ),
            html.Hr(className="my-2"), 
            dbc.Card(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.CardImg(
                                            src="/assets/imgs/card01.jpg",
                                            className="img-fluid rounded-start",
                                        ),
                                        className="col-md-4",
                                    ),
                                    dbc.Col(
                                        dbc.CardBody(
                                            [
                                                html.H1("Our Mission"),
                                                dcc.Markdown(
                                                    """Our main goal is to create and app in which you can upload and explore radiological images and highlight
                                                    those regions in which there are IDC indices.
                                                    The application is a versatile, practical and fast way for a health professional to make a reliable diagnosis
                                                    regarding the presence of cancer in a sample. This approach has advantages over other proposals
                                                    found in literature, such as:""", style={"textAlign": "left", "fontSize": 25, "color":"darkcyan"}),
                                                dcc.Markdown(  
                                                    """
                                                    * Not being just an image classification model but an embedded model in an application that the final
                                                    user can better interact with
                                                    * This classification model is more reliable and robust compared to other models previously mentioned
                                                    * It gives a fast and reliable diagnostic that may help to reduce time and errors.We want to make
                                                    diagnostics more accessible and simple in order to make it easier for certain populations to have
                                                    access to an accurate diagnosis
                                                    * The model can work as a pedagogical tool to train health professionals who are related to this field.
                                                    * It is intended as a support tool for health professionals
                                                    """,
                                                    style={"textAlign": "left", "fontSize": 25, "color":"darkcyan"}
                                                ),
                                            ]
                                        ),
                                        className="col-md-8",
                                    ),
                                ],
                            )
                        ],
                    )
        ],
        fluid=True,
        className="py-3",
    ),
    className="p-3 rounded-3",
)
from io import BytesIO as bt
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras import models
import requests
import io
from starlette.responses import StreamingResponse

def get_pil_image(image):
    """
    Function to prepare data for the model prediction.
    Transforms the image bytes content into a np array
    
    @params image : UploadFile 
    @returns: image np array 
    """
    image_bytes=image.file.read()
    img_bytes_obj=Image.open(bt(image_bytes))
    return img_bytes_obj

def get_image_array(image):
    """
    Function to prepare data for the model prediction.
    Transforms the image bytes content into a np array
    
    @params image : UploadFile 
    @returns: image np array 
    """
    image_bytes=image.file.read()
    img_bytes_obj=Image.open(bt(image_bytes))
    return np.array(img_bytes_obj)

def load_data_from_url(image_url):
    """
    Function to load data from a given url.
    Transforms the image bytes content into a np array
    
    @params image_url : image from url
    @returns: image np array 
    """
    response = requests.get(image_url)
    img = Image.open(bt(response.content))
    return np.array(img)

def retrieve_img_data(img_array):
    """Given a numpy array return the image as a response
    @params image_url : image np array 
    @returns: encoded image
    """
    return StreamingResponse(io.BytesIO(img_array.tobytes()), media_type="image/png")


def prepare_cnn_response(prediction):
    """
    Function to prepare the CNN response based on the image class names
    
    @params prediction : np array with the prediction 
    @returns: Dict with the image predicition
    """
    print(prediction)

    return {"Image Prediction": prediction[0][0]}

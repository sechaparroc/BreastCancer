from io import BytesIO as bt
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras import models
import requests
import io
from starlette.responses import StreamingResponse
import boto3

def is_image_of_patient(patient_id:int, key:str):
    """Verify if the path of a given image corresponds to the patient ID 
    Args:
        patient_id (int) 
        key (str): aws S3 path

    Returns:
        bool
    """
    print(key.split("/")[-2], patient_id)
    return key.split("/")[-2] == patient_id

def obtain_patient_images(patient_id:int, tile_size:int=500):
    """Given a patient Id and the Tile size obtain the images related with the patient
    Args:
        patient_id (int)
        tile_size (int, optional): Dimension of the Squared images, either 500 or 1000. Defaults to 500.

    Returns:
        list: paths of the patient images
    """
    images = []
    s3 = boto3.resource('s3')
    my_bucket = s3.Bucket('breast-cancer-data')

    for object_summary in my_bucket.objects.filter(Prefix=f"Tiles/Tiles-{tile_size}/Tiles({tile_size}, {tile_size})/{patient_id}/"):
        images.append(object_summary.key)
    return images

def obtain_sample_images():
    """Given a patient Id and the Tile size obtain the images related with the patient
    Args:
        patient_id (int)
        tile_size (int, optional): Dimension of the Squared images, either 500 or 1000. Defaults to 500.

    Returns:
        list: paths of the patient images
    """
    images = []
    s3 = boto3.resource('s3')
    my_bucket = s3.Bucket('breast-cancer-data')

    for object_summary in my_bucket.objects.filter(Prefix=f"imgs/"):
        images.append(object_summary.key)
    return images


def obtain_patients_by_cancer_proportion(df, cancer_proportion:float, K:int = 5):
    """Given a proportion and the Tile size obtain the K patiens with the nearest proportion
    Args:
        cancer_proportion (float)
        tile_size (int, optional): Dimension of the Squared images, either 500 or 1000. Defaults to 500.

    Returns:
        list: patient ids 
    """
    filtered_patients = df.iloc[(df['cancer_proportion']-cancer_proportion).abs().argsort()[:K]].astype(int)
    return [int(x) for x in filtered_patients['id'].values]



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



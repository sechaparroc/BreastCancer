import os
import uvicorn
from fastapi import FastAPI,UploadFile
from fastapi import Response
from cnn.functions import *
from cnn.model import Model
import io
from starlette.responses import StreamingResponse
import pickle
import codecs

#Set this as false on Production if GPU is enabled
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

SAMPLE_PATH = "https://breast-cancer-data.s3.us-east-1.amazonaws.com/imgs/"
proxy=""
app_cnn = FastAPI(root_path=proxy)

# Place here the models
models = dict()
models["classical"] = Model("classical", os.path.join('.', 'data', 'models', 'classical_model.h5'), "conv2d_2")
models["with_regularization"] = Model("classical", os.path.join('.', 'data', 'models', 'classical_model.h5'), "conv2d_2")

@app_cnn.get('/status/')
async def get_api_status():
    """
    GET method for getting the status of the API
    @returns: JSON of the API status
    """
    return {'status': 'Up & running'}

@app_cnn.post('/predict/')
async def cnn_predict(model_name: str, image: UploadFile):
    """
    POST method for predicting if a given patch has cancer or not.
    @params model_name: model to use
    @params image: image UploadFile
    @returns: JSON of the image prediction 
    """
    prepared_data = get_image_array(image)
    prediction = models[model_name].predict(prepared_data[np.newaxis,...,np.newaxis])
    return prepare_cnn_response(prediction)

#See https://stackoverflow.com/questions/71595635/render-numpy-array-in-fastapi
@app_cnn.get("/image_sample", response_class=Response)
def get_image_sample(num):
    img_array = load_data_from_url(f"{SAMPLE_PATH}sample_{num}.png")
    im = Image.fromarray(img_array)
    # save image to an in-memory bytes buffer
    with io.BytesIO() as buf:
        im.save(buf, format='PNG')
        im_bytes = buf.getvalue()
    headers = {'Content-Disposition': 'inline; filename="test.png"'}
    return Response(im_bytes, headers=headers, media_type='image/png')

# https://stackoverflow.com/questions/6485790/numpy-array-to-base64-and-back-to-numpy-array-python
@app_cnn.post("/tint_patches")
def tint_patches(model_name : str, roiImg: UploadFile): 
    roi = get_image_array(roiImg)

    #transform roi into a numpy array
    roi, annotations = models[model_name].tint_image(roi)

    encoded_roi = codecs.encode(pickle.dumps(roi, protocol=pickle.HIGHEST_PROTOCOL), "base64").decode('latin1')
    #must return the annotations and the tinted roi
    # save image to an in-memory bytes buffer
    return {
        'roi' : encoded_roi,
        'annotations' : annotations
    }

@app_cnn.post("/tint_gradcam")
def tint_gradcam(model_name : str, roiImg: UploadFile): 
    roi = get_image_array(roiImg)
    #transform roi into a numpy array
    roi , _, annotations = models[model_name].tint_with_gradcam(roi)
    encoded_roi = codecs.encode(pickle.dumps(roi, protocol=pickle.HIGHEST_PROTOCOL), "base64").decode('latin1')
    # must return the annotations and the tinted roi
    # save image to an in-memory bytes buffer

    return {
        'roi' : encoded_roi,
        'annotations' : annotations
    }



if __name__ == "__main__":
    uvicorn.run(app_cnn, port=8000,host='0.0.0.0')

import pandas as pd
from skimage import data
from skimage import io
import plotly.graph_objects as go
import os
from pathlib import Path

import tensorflow as tf
from tensorflow import keras
import cv2
import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.cm as cm

#Set this as false on Production if GPU is enabled
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

class Model:
    """convinient methods to use a tf model and perform realtime predictions
    """
    def __init__(self, name, path, last_conv_layer, patch_dim = (50,50)):
        #load a model from the given path
        self.name = name
        self.model = tf.keras.models.load_model(path)
        self.patch_dim = patch_dim
        self.last_conv_layer = last_conv_layer

    #Useful image operations
    def get_img(self, path:str, size:tuple=None):
        return tf.keras.utils.load_img(path, target_size=size)

    def get_img_array(self, path : str, size : tuple):
        img = tf.keras.utils.load_img(path, target_size=size)
        array = tf.keras.utils.img_to_array(img) / 255.0
        array = np.expand_dims(array, axis=0)
        return array

    def get_array_from_img(self,img):
        array = tf.keras.utils.img_to_array(img) / 255.0
        array = np.expand_dims(array, axis=0)
        return array
    
    def predict_array(self, array, threshold = 0.5):
        y_pred = self.model.predict(array, verbose = 0)
        predicted_class = np.where(y_pred > threshold, 1,0)[0][0]
        return predicted_class

    def predict_img(self, img, threshold = 0.5):
        self.predict_array(self, self.get_array_from_img(img), threshold = 0.5)
    

    def add_padding(self, roi_img):
        PW = self.patch_dim[0]
        PH = self.patch_dim[1]
        #make the input shape of the roi image a multiple of PW and PH
        width_mod = roi_img.shape[1] % PW
        upper_width = roi_img.shape[1] + PW - width_mod
        desired_width = upper_width

        height_mod = roi_img.shape[0] % PH
        upper_height = roi_img.shape[0] + PH - height_mod
        desired_height = upper_height

        border_left =  math.floor(abs(desired_width - roi_img.shape[1]) / 2)
        border_right = math.ceil(abs(desired_width - roi_img.shape[1]) / 2)
        border_top = math.floor(abs(desired_height - roi_img.shape[0]) / 2)
        border_bottom = math.ceil(abs(desired_height - roi_img.shape[0]) / 2)

        valid_roi = cv2.copyMakeBorder(
            roi_img,
            top=border_top,
            bottom=border_bottom,
            left=border_left,
            right=border_right,
            borderType=cv2.BORDER_CONSTANT,
            value=[255, 255, 255]
        )


        return valid_roi





    #see https://stackoverflow.com/questions/46020894/superimpose-heatmap-on-a-base-image-opencv-python
    #given a large image tint with a red color the zones with cancer 
    def tint_image(self, image):
        image = self.add_padding(image)
        img_array = self.get_array_from_img(image)

        PH = self.patch_dim[0]
        PW = self.patch_dim[1]

        mask = np.zeros(img_array[0].shape).astype('float32')
        for row in range(0,img_array[0].shape[0],PH):
            for col in range(0,img_array[0].shape[1],PW):
                patch = img_array[:,row:row+PH, col:col+PW, :]
                # do not predict if patch shape is not valid
                if patch.shape[1] < PW or patch.shape[2] < PH:
                    continue
                y_prob = self.model.predict(patch, verbose = 0)
                mask[row:row+PH, col:col+PW, 0] =  1 * y_prob[0][0]

        mask = 255 * mask 
        mask = mask.astype(np.uint8)
        mask = cv2.GaussianBlur(mask,(9,9), 7)
        return cv2.addWeighted(mask, 0.3, (img_array[0] * 255).astype(np.uint8), 0.7, 0) 

    # use grad cam - code inspired by https://keras.io/examples/vision/grad_cam/
    def make_gradcam_heatmap(self, img_array, model, last_conv_layer_name, pred_index=None):
        grad_model = tf.keras.models.Model(
            [model.inputs], [model.get_layer(last_conv_layer_name).output, model.output]
        )
        with tf.GradientTape() as tape:
            last_conv_layer_output, preds = grad_model(img_array)
            
            if pred_index is None:
                pred_index = tf.argmax(preds[0])
            class_channel = preds[:, pred_index]

        grads = tape.gradient(class_channel, last_conv_layer_output)

        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

        last_conv_layer_output = last_conv_layer_output[0]
        heatmap = last_conv_layer_output @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)

        heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)
        return heatmap.numpy()

    def gradcam(self, img, heatmap, alpha=0.7):
        img = img * 255.0
        img = img.astype(np.float32)
        
        # Rescale heatmap to a range 0-255
        heatmap = np.uint8(255 * heatmap)
        # Use jet colormap to colorize heatmap
        jet = cm.get_cmap("jet") #jet
        # Use RGB values of the colormap
        jet_colors = jet(np.arange(256))[:, :3]
        jet_heatmap = jet_colors[heatmap]
        # Create an image with RGB colorized heatmap
        jet_heatmap = keras.preprocessing.image.array_to_img(jet_heatmap)
        jet_heatmap = jet_heatmap.resize((img.shape[1], img.shape[0]))
        jet_heatmap = keras.preprocessing.image.img_to_array(jet_heatmap)
        # Superimpose the heatmap on original image
        superimposed_img = cv2.addWeighted(img, 1-alpha, jet_heatmap, alpha, 0) #jet_heatmap * alpha + img
        
        return superimposed_img / 255.0, jet_heatmap / 255.0


                
    def tint_with_gradcam(self, image):
        image = self.add_padding(image)
        img_array = self.get_array_from_img(image)


        PH = self.patch_dim[0]
        PW = self.patch_dim[1]
        output_image = np.zeros(image.shape)
        heatmap_image = np.zeros(image.shape)

        for row in range(0,image.shape[0],PH):
            for col in range(0,image.shape[1],PW):
                patch = img_array[:,row:row+PH, col:col+PW, :]
                # do not predict if patch shape is not valid
                if patch.shape[1] < PW or patch.shape[2] < PH:
                    continue
                heatmap = self.make_gradcam_heatmap(patch, self.model, self.last_conv_layer, pred_index = 0)
                out, heat = self.gradcam(patch[0], heatmap, alpha=0.3)
                output_image[row:row+PH, col:col+PW, :] =  out
                heatmap_image[row:row+PH, col:col+PW, :] = heat
        return output_image, heatmap_image


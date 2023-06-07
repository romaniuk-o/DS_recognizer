import os
from pathlib import Path
from PIL import Image
from django.shortcuts import render, redirect

from django.http import JsonResponse
from .forms import AnalyzeForm
from django.conf import settings
import numpy as np


# Create your views here.
def main(request):
    return render(request, 'recognizer_app/index.html', {})

import tensorflow as tf
from tensorflow.keras.models import load_model


# Global variable to store the loaded model
loaded_model = None

def load_custom_model():
    global loaded_model
    if loaded_model is None:
        print('Loading the model ... ')
        model_path = 'recognizer_app/src/Xception_tuned.h5'
        loaded_model = load_model(model_path)

# Call the function to load the model
load_custom_model()

def classify(image=None):
    if not image:
        return None
    class_labels = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']
    img = image
    img = img.resize((32, 32))
    img = np.array(img)
    img = np.expand_dims(img, axis=0)  # Add a batch dimension
    predictions = loaded_model.predict(img)
    print(predictions)
    prediction_label = np.argmax(predictions)
    # prediction = tf.nn.softmax(prediction)
    return class_labels[prediction_label], predictions[0][prediction_label]
    # return 'bird'

def analyze_view(request):
    if request.method == 'POST':

        form = AnalyzeForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data['image']

            # Open the image using PIL
            img = Image.open(image)

            max_width = 299
            max_height = 299
            # Check if the image is larger than 32x32
            if img.width > max_width or img.height > max_height:
                # Calculate the new dimensions while maintaining aspect ratio
                aspect_ratio = img.width / img.height
                if img.width > img.height:
                    new_width = max_width
                    new_height = int(new_width / aspect_ratio)
                else:
                    new_height = max_height
                    new_width = int(new_height * aspect_ratio)

                # Rescale the image to the new dimensions
                img = img.resize((new_width, new_height), Image.LANCZOS)
            # print(img.width, img.height)
            # Save the image to the media directory
            image_path = os.path.join(settings.MEDIA_ROOT, image.name)
            img.save(image_path)

            # Generate the image URL to be used in the template
            image_url = os.path.join(settings.MEDIA_URL, image.name)

            image_class, confidence = classify(img)
            confidence = int(confidence*10000)/100.0
            print(image_class, confidence)

            return render(request, 'recognizer_app/index.html', {'image_url': image_url,
                                                                 'image_class': image_class,
                                                                 'confidence': confidence,
                                                                 })
    else:
        form = AnalyzeForm()

    return render(request, 'recognizer_app/index.html', {'form': form})



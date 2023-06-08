import os
from pathlib import Path
from PIL import Image
from django.shortcuts import render, redirect

from django.http import JsonResponse
from .forms import AnalyzeForm
from django.conf import settings
import numpy as np
from .models import Image as ImageModel
from django.core.exceptions import ObjectDoesNotExist

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
        # Get the last layer of the model
        last_layer = loaded_model.layers[-1]

        # Turn off the activation function of the last layer
        last_layer.activation = None
# Call the function to load the model
load_custom_model()


def classify(image=None):
    if not image:
        return None
    class_labels = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']

    img = image.convert('RGB')
    img = img.resize((32, 32))

    img = np.array(img)
    img = np.expand_dims(img, axis=0)  # Add a batch dimension
    clean_predictions = loaded_model.predict(img)
    sigmoid_predictions = 1 / (1 + np.exp(-clean_predictions))
    predictions = np.exp(clean_predictions) / np.sum(np.exp(clean_predictions))


    print(clean_predictions)
    print(predictions)
    print(sigmoid_predictions)
    prediction_label = np.argmax(predictions)
    # prediction = tf.nn.softmax(prediction)
    percentage = str(int(predictions[0][prediction_label] * 10000) / 100.0)
    return class_labels[prediction_label], percentage+"%"
    # return 'bird'


def analyze_view(request, image_id=-1):
    user_images = ImageModel.objects.filter(user=request.user).order_by('-last_viewed')
    image_url = None
    image_class = None
    confidence = None

    try:
        image = ImageModel.objects.get(id=image_id)
        image_url = image.image.url
        image_path = image.image.path
        # print(image_url)
        image_class, confidence = classify(Image.open(image_path))
    except ObjectDoesNotExist as err:
        pass
        # image_class, confidence = 'airplane', '99.99'
        # image_url = base_image_url

    if request.method == 'POST':
        form = AnalyzeForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data['image']

            # Open the image using PIL
            img = Image.open(image)

            max_width = 244
            max_height = 244
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

                img = img.resize((new_width, new_height), Image.LANCZOS)

            # Generate the image path to save the resized image
            image_path = os.path.join(settings.MEDIA_ROOT, image.name)
            img.save(image_path)

            new_image = ImageModel(user=request.user, image=image, title=image.name)
            new_image.save()

            # Generate the image URL to be used in the template
            image_url = os.path.join(settings.MEDIA_URL, image.name)

            image_class, confidence = classify(img)

            return render(request, 'recognizer_app/index.html', {'image_url': image_url,
                                                                 'image_class': image_class,
                                                                 'confidence': confidence,
                                                                 'images': user_images,
                                                                 })
    else:
        form = AnalyzeForm()

    return render(request, 'recognizer_app/index.html', {'image_url': image_url,
                                                         'image_class': image_class,
                                                         'confidence': confidence,
                                                         'images': user_images,
                                                         })


def analyze_view_by_id(request, image_id):
    # Retrieve the image object based on the image ID
    try:
        image = ImageModel.objects.get(id=image_id)
    except Exception:
        # Handle the case when any exception occurs
        return redirect('/analyze/')

    # Perform your analysis or any other operations based on the image
    # ...

    # Return the response or render a template with the analysis results
    # return render(request, 'analysis_results.html', {'image': image})
    return analyze_view(request, image_id=image_id)
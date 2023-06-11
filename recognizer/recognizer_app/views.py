import os
import io

from pathlib import Path
from PIL import Image
from django.shortcuts import render, redirect

from django.http import JsonResponse
from .forms import AnalyzeForm
from django.conf import settings
import numpy as np
from .models import Image as ImageModel
from django.core.exceptions import ObjectDoesNotExist
# import tensorflow as tf
# from tensorflow.keras.models import load_model
from django.contrib.auth import authenticate, login, logout
from .forms import SignUpForm
from django.contrib import messages
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden


# Create your views here.
def main(request):
    return render(request, 'recognizer_app/index.html', {})




# Global variable to store the loaded model
loaded_model = None

def load_custom_model():
    return 0
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
    return " uncomment view to  classify", " 0%"
    if not image:
        return None
    class_labels = ['Airplane', 'Automobile', 'Bird', 'Cat', 'Deer', 'Dog', 'Frog', 'Horse', 'Ship', 'Truck']

    img = image.convert('RGB')
    img = img.resize((32, 32))

    img = np.array(img)
    img = np.expand_dims(img, axis=0)  # Add a batch dimension
    clean_predictions = loaded_model.predict(img)
    sigmoid_predictions = 1 / (1 + np.exp(-clean_predictions))
    predictions = np.exp(clean_predictions) / np.sum(np.exp(clean_predictions))


    # print(clean_predictions)
    # print(predictions)
    # print(sigmoid_predictions)
    prediction_label = np.argmax(predictions)
    # prediction = tf.nn.softmax(prediction)
    percentage = str(int(predictions[0][prediction_label] * 10000) / 100.0)
    return class_labels[prediction_label], percentage+"%"
    # return 'bird'


@login_required  # Requires the user to be authenticated
def analyze_view(request, image_id=-1):

    if not request.user.is_authenticated:
        # Redirect or return an appropriate response for unauthorized users
        return HttpResponseForbidden()

    # try:
    #     image = ImageModel.objects.get(id=image_id)
    # except ImageModel.DoesNotExist:
    #     # Handle the case when the image doesn't exist
    #     return redirect('/analyze/')
    #
    # if image.user != request.user:
    #     # Return a forbidden response if the image doesn't belong to the user
    #     return HttpResponseForbidden()

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


    if request.method == 'POST':
        form = AnalyzeForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data['image']
            new_image = ImageModel(user=request.user, image=image, title=image.name)
            new_image.save()
            return redirect(f'/analyze/{new_image.id}/')
    else:
        form = AnalyzeForm()

    return render(request, 'recognizer_app/index.html', {'image_url': image_url,
                                                         'image_class': image_class,
                                                         'confidence': confidence,
                                                         'images': user_images,
                                                         })






@login_required  # Requires the user to be authenticated
def analyze_view_by_id(request, image_id):
    try:
        image = ImageModel.objects.get(id=image_id)
    except ImageModel.DoesNotExist:
        return redirect('/analyze/')
    if image.user != request.user:
        # return HttpResponseForbidden()
        return redirect('/analyze/')
    return analyze_view(request, image_id=image_id)


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/analyze/')  # replace 'home' with your desired landing page
        else:
            error_message = 'Invalid login credentials'
            return render(request, 'recognizer_app/login.html', {'error_message': error_message})
    else:
        return render(request, 'recognizer_app/login.html')
        # return render(request, 'login.html')


def signup_view(request):

    # uncomment this in final version
    # if request.user.is_authenticated:
    #     return redirect('/')

    if request.method == 'POST':
        error_message = []
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Your account has been created! You are now able to log in!')
            print("Form is valid")
            return redirect('/login/')
        else:
            print("Form is invalid")
            print(form.errors)  # Print form errors to the console
            # for field in form.errors:
            #     error_message[field] = form.errors[field].as_text()
    else:
        form = SignUpForm()
    return render(request, 'recognizer_app/signup.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    return redirect('main')
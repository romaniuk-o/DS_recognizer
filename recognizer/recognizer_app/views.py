import os
from pathlib import Path

from django.shortcuts import render, redirect


# Create your views here.
def main(request):
    return render(request, 'recognizer_app/index.html', {})







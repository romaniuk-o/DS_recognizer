from django.urls import path
from . import views
from .views import analyze_view

urlpatterns = [
    path('', views.main, name='main'),
    path('analyze/', analyze_view, name='analyze'),

]

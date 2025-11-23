
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('dispensar/', views.dispense, name='dispense'),
]


from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.inventory_list, name='inventory_list'),
    path('ingreso/', views.register_entry, name='register_entry'),
    path('revision/', views.review_received, name='review_received'),
    path('solicitudes/', views.requests_view, name='requests'),
]

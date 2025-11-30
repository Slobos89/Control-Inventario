from django.urls import path
from . import views

urlpatterns = [
    path('', views.inventory_list, name='inventory_list'),
    path('ingreso/', views.register_entry, name='register_entry'),
    path('solicitudes/', views.requests_view, name='requests'),
    path('importar/', views.import_inventory, name='import_inventory'),
]

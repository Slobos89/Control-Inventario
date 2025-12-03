from django.urls import path
from . import views

app_name = "inventario"   

urlpatterns = [
    path('', views.inventory_list, name='inventory_list'),
    path('ingreso/', views.register_entry, name='register_entry'),
    path('solicitudes/', views.solicitudes_listar, name='solicitudes_listar'),
    path('solicitudes/<int:pk>/', views.solicitud_detalle, name='solicitud_detalle'),
    path("solicitud/<int:pk>/aprobar/", views.solicitud_aprobar, name="solicitud_aprobar"),
    path("solicitud/<int:pk>/rechazar/", views.solicitud_rechazar, name="solicitud_rechazar"),
    path('importar/', views.import_inventory, name='import_inventory'),
    path('facturas/', views.facturas_list, name='facturas_list'),
    path('facturas/<int:pk>/', views.factura_detalle, name='factura_detalle'),
]

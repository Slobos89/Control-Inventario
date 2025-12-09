
from django.contrib import admin
from django.urls import path
from . import views

app_name = "farmacia"

urlpatterns = [
    path('', views.lista_medicamentos, name='medicamentos_lista'), 
    path('crear/', views.crear_medicamento, name='crear'),
    path('<int:pk>/', views.detalle_medicamento, name='detalle'),
    path('movimiento/nuevo/', views.movimiento_crear, name='movimiento_nuevo'),
    path("importar/", views.import_inventory_farmacia, name="import_inventory"),
    path("solicitudes/crear/", views.solicitud_crear, name="solicitud_crear"),
    path("solicitudes/mias/", views.solicitudes_mias, name="solicitudes_mias"),
    path("facturas/", views.facturas_farmacia_list, name="facturas_list"),
    path("facturas/<int:pk>/", views.factura_farmacia_detalle, name="factura_detalle"),
    path("facturas/nueva/", views.crear_factura_farmacia, name="crear_factura"),
    path('dispensar/', views.dispense, name='dispense'),
    path("dispensaciones/", views.dispensaciones_list, name="dispensaciones_list"),
    path("dispensacion/<int:id>/", views.dispensacion_detail, name="dispense_detail"),
]

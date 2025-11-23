
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('gestion/', views.manage_users, name='manage_users'),
    path('crear/', views.crear_usuario, name='crear_usuario'),
    # Si quieres habilitar registro público:
    path('registrar/', views.registrar_usuario, name='registrar_usuario'),
    path('estado/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
    path('editar/<int:user_id>/', views.editar_usuario, name='editar_usuario'),
]

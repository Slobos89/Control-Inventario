
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('jefe-bodega-dashboard/', views.jefe_bodega_dashboard, name='jefe_bodega_dashboard'),
    path('jefe-farmacia-dashboard/', views.jefe_farmacia_dashboard, name='jefe_farmacia_dashboard'),
    path('reportes/', views.reports, name='reports'),
    path('logout/', views.logout_view, name='logout'),
]

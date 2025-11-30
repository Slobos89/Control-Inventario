
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path("dashboard/", views.dashboard, name="dashboard"),
    path('reportes/', views.reports, name='reports'),
    path('logout/', views.logout_view, name='logout'),
]

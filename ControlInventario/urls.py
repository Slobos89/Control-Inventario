
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('core.urls')),
    path('admin/', admin.site.urls),
    path('inventario/', include('inventario.urls')),
    path('farmacia/', include('farmacia.urls')),
    path('usuarios/', include('usuarios.urls')),
]

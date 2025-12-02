
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('core.urls')),
    path('admin/', admin.site.urls),
    path("inventario/",include(("inventario.urls", "inventario"), namespace="inventario")),
    path("farmacia/", include(("farmacia.urls", "farmacia"), namespace="farmacia")),
    path('usuarios/', include('usuarios.urls')),
]

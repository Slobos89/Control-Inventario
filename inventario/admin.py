from django.contrib import admin
from .models import (
    Insumo, FacturaIngreso, ItemFactura,
    Movimiento, SolicitudReposicion, ItemSolicitud
)

admin.site.register(Insumo)
admin.site.register(FacturaIngreso)
admin.site.register(ItemFactura)
admin.site.register(Movimiento)
admin.site.register(SolicitudReposicion)
admin.site.register(ItemSolicitud)
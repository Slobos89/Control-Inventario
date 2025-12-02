from django.contrib import admin
from .models import (
    Insumo, FacturaIngreso, ItemFactura,
    Movimiento
)

admin.site.register(Insumo)
admin.site.register(FacturaIngreso)
admin.site.register(ItemFactura)
admin.site.register(Movimiento)

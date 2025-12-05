
from django.contrib import admin
from .models import *

@admin.register(Medicamento)
class MedicamentoAdmin(admin.ModelAdmin):
    list_display = ('codigo','nombre','stock','stock_critico','fecha_vencimiento')
    search_fields = ('codigo','nombre')

@admin.register(MovimientoFarmacia)
class MovimientoAdmin(admin.ModelAdmin):
    list_display = ('medicamento','tipo','cantidad','usuario','fecha')
    list_filter = ('tipo','fecha')

class ItemSolicitudInline(admin.TabularInline):
    model = ItemSolicitud
    extra = 0

@admin.register(SolicitudReposicion)
class SolicitudAdmin(admin.ModelAdmin):
    list_display = ("id", "area", "usuario", "estado", "fecha")
    list_filter = ("estado", "area")
    inlines = [ItemSolicitudInline]

class ItemFacturaFarmaciaInline(admin.TabularInline):
    model = ItemFacturaFarmacia
    extra = 0

@admin.register(FacturaFarmacia)
class FacturaFarmaciaAdmin(admin.ModelAdmin):
    list_display = ("id", "folio", "fecha_emision", "proveedor_nombre", "total_items", "usuario")
    search_fields = ("folio", "proveedor_nombre", "proveedor_rut")
    list_filter = ("fecha_emision",)
    inlines = [ItemFacturaFarmaciaInline]
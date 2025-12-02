
from django.contrib import admin
from .models import Medicamento, MovimientoFarmacia, SolicitudReposicion, ItemSolicitud

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
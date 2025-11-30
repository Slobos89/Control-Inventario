from django.contrib import admin


from django.contrib import admin
from .models import Medicamento, MovimientoFarmacia

@admin.register(Medicamento)
class MedicamentoAdmin(admin.ModelAdmin):
    list_display = ('codigo','nombre','stock','stock_critico','fecha_vencimiento')
    search_fields = ('codigo','nombre')

@admin.register(MovimientoFarmacia)
class MovimientoAdmin(admin.ModelAdmin):
    list_display = ('medicamento','tipo','cantidad','usuario','fecha')
    list_filter = ('tipo','fecha')
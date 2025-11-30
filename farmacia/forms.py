from django import forms
from .models import Medicamento, MovimientoFarmacia

class MedicamentoForm(forms.ModelForm):
    class Meta:
        model = Medicamento
        fields = ['codigo','nombre','descripcion','lote','fecha_vencimiento','stock','stock_critico']

class MovimientoFarmaciaForm(forms.ModelForm):
    class Meta:
        model = MovimientoFarmacia
        fields = ['medicamento','tipo','cantidad','observacion']

class UploadFileForm(forms.Form):
    archivo = forms.FileField()
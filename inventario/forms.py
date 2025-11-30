from django import forms
from .models import Insumo, FacturaIngreso, ItemFactura, SolicitudReposicion

class FacturaIngresoForm(forms.ModelForm):
    class Meta:
        model = FacturaIngreso
        fields = ["numero", "fecha", "proveedor"]


class ItemFacturaForm(forms.ModelForm):
    class Meta:
        model = ItemFactura
        fields = ["insumo", "cantidad", "lote", "vencimiento"]


class SolicitudForm(forms.ModelForm):
    class Meta:
        model = SolicitudReposicion
        fields = ["area"]

class UploadFileForm(forms.Form):
    archivo = forms.FileField(label="Archivo CSV o Excel")
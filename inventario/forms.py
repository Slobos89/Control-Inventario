from django import forms
from django.forms import formset_factory, inlineformset_factory
from .models import (
    FacturaIngreso,
    ItemFactura,
    Insumo
)

class FacturaIngresoForm(forms.ModelForm):
    class Meta:
        model = FacturaIngreso
        fields = ["numero", "fecha", "proveedor"]






class UploadFileForm(forms.Form):
    archivo = forms.FileField(label="Archivo CSV o Excel")


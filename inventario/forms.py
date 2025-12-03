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
        fields = [
            "folio",
            "fecha_emision",
            "proveedor_rut",
            "proveedor_nombre",
            "proveedor_giro",
            "archivo_pdf",
        ]

class ItemFacturaForm(forms.ModelForm):
    class Meta:
        model = ItemFactura
        fields = ["insumo","cantidad","lote","vencimiento"]

class UploadFileForm(forms.Form):
    archivo = forms.FileField(label="Archivo CSV o Excel")


from django import forms
from django.forms import inlineformset_factory
from .models import (
    Medicamento,
    MovimientoFarmacia,
    SolicitudReposicion,
    ItemSolicitud
)

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

class DispensacionForm(forms.Form):
    medicamento = forms.ModelChoiceField(
        queryset=Medicamento.objects.all(),
        label="Medicamento"
    )
    cantidad = forms.IntegerField(min_value=1, label="Cantidad a dispensar")
    observacion = forms.CharField(
        widget=forms.Textarea, 
        required=False,
        label="Observación"
    )



class ItemSolicitudForm(forms.ModelForm):
    class Meta:
        model = ItemSolicitud
        fields = ["insumo", "cantidad"]
        widgets = {
            "insumo": forms.Select(attrs={"class": "form-select"}),
            "cantidad": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
        }

class SolicitudReposicionForm(forms.ModelForm):
    class Meta:
        model = SolicitudReposicion
        fields = ["area"]  # usuario y fecha son automáticos
        widgets = {
            "area": forms.TextInput(attrs={"class": "form-control"}),
        }

ItemSolicitudFormSet = inlineformset_factory(
    SolicitudReposicion,
    ItemSolicitud,
    form=ItemSolicitudForm,
    extra=1,
    can_delete=True
)
from django import forms
from django.contrib.auth.models import User
from .models import Perfil

class CrearUsuarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    rol = forms.ChoiceField(choices=Perfil.ROLES)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class RegistroUsuarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    password_confirm = forms.CharField(widget=forms.PasswordInput(), label="Confirmar contraseña")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean(self):
        cleaned_data = super().clean()
        pwd = cleaned_data.get("password")
        pwd2 = cleaned_data.get("password_confirm")

        if pwd and pwd2 and pwd != pwd2:
            raise forms.ValidationError("Las contraseñas no coinciden.")

        return cleaned_data

class EditarUsuarioForm(forms.ModelForm):
    rol = forms.ChoiceField(choices=Perfil.ROLES, required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            rol = self.cleaned_data.get("rol")
            if rol:
                user.perfil.rol = rol
                user.perfil.save()
        return user
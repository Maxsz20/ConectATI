# web/app/forms.py
from django import forms
from .models import Usuario

class RegistroForm(forms.Form):
    nombre = forms.CharField(max_length=100)
    username = forms.CharField(max_length=50)
    email = forms.EmailField()
    ci = forms.CharField(max_length=20)
    telefono = forms.CharField(max_length=20)
    contrasena = forms.CharField(widget=forms.PasswordInput)
    confirmar_contrasena = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("contrasena")
        confirm = cleaned_data.get("confirmar_contrasena")

        if password != confirm:
            raise forms.ValidationError("Las contraseñas no coinciden")

        return cleaned_data


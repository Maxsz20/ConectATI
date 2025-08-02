# web/app/forms.py
from django import forms
from .models import Usuario

class RegistroForm(forms.Form):
    nombre = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Nombre', 'required': True})
    )
    username = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Nombre de Usuario', 'required': True})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Correo', 'required': True})
    )
    ci = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': 'Cédula de identidad', 'required': True})
    )
    contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña', 'id': 'password', 'required': True})
    )
    confirmar_contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirmar contraseña', 'id': 'confirm', 'required': True})
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("contrasena")
        confirm = cleaned_data.get("confirmar_contrasena")

        if password != confirm:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return cleaned_data
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if Usuario.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nombre de usuario ya está en uso.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return email

    def clean_ci(self):
        ci = self.cleaned_data.get('ci')
        if Usuario.objects.filter(ci=ci).exists():
            raise forms.ValidationError("Esta cédula ya está registrada.")
        return ci

class PublicacionForm(forms.Form):
    texto = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        max_length=500
    )
    archivo = forms.FileField(required=False)
    privacidad = forms.ChoiceField(
        choices=[('publica', 'Pública'), ('privada', 'Privada')],
        required=True
    )

class EditarPerfilForm(forms.ModelForm):
    foto_archivo = forms.ImageField(required=False)

    class Meta:
        model = Usuario
        fields = [
            'nombre', 'username', 'descripcion', 'fecha_nacimiento',
            'genero', 'color_favorito', 'libro_favorito', 'musica_favorita',
            'videojuegos', 'lenguajes'
        ]
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

    def save(self, commit=True, using=None):
        instance = super().save(commit=False)

        archivo = self.cleaned_data.get('foto_archivo')
        if archivo:
            from django.core.files.storage import default_storage
            from django.core.files.base import ContentFile

            ruta = f'fotos_perfil/{archivo.name}'
            default_storage.save(ruta, ContentFile(archivo.read()))
            instance.foto = ruta  # Se guarda la ruta como texto

        if commit:
            instance.save(using=using)
        return instance
# Formularios para eventos, archivos, etc. se definirán aquí
from django import forms
from .models import Equipo, Noticia, Investigacion, Publicacion, Evento
from django.contrib.auth.forms import AuthenticationForm

class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = ['nombre', 'profesionalidad', 'descripcion', 'foto']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo'}),
            'profesionalidad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Profesor/a, Director/a, etc.'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Información profesional, especialidad, etc.'}),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control', 'placeholder': 'Usuario'}))
    password = forms.CharField(label="Contraseña", strip=False, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}))

class NoticiaForm(forms.ModelForm):
    class Meta:
        model = Noticia
        fields = ['titulo', 'contenido', 'imagen']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título de la noticia'}),
            'contenido': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Contenido de la noticia'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class InvestigacionForm(forms.ModelForm):
    class Meta:
        model = Investigacion
        fields = ['titulo', 'descripcion', 'foto', 'archivo']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título de la investigación'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Descripción, resumen, autores, etc.'}),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'archivo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class PublicacionForm(forms.ModelForm):
    class Meta:
        model = Publicacion
        fields = ['titulo', 'autores', 'resumen', 'imagen', 'video', 'archivo']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título de la publicación'}),
            'autores': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Autores'}),
            'resumen': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Resumen, detalles, etc.'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'video': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'video/mp4,video/webm'}),
            'archivo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ['nombre', 'fecha', 'fecha_cierre', 'descripcion', 'pdf', 'archivo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del evento'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_cierre': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descripción del evento'}),
            'pdf': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'application/pdf'}),
            'archivo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

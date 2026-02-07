from django import forms
from .models import *


# =================================================== COMENTARIOS ===================================================

# Formulario para añadir un comentario
class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        # Content no tiene null=True ni blank=True, por lo que Django lo considera obligatorio.
        # Contenido q quieres incluir en el comentario = fields
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Escribe tu comentario…',
            }),
        }


# =================================================== VALORACIONES ===================================================

class ValoracionForm(forms.ModelForm):
    # Creamos la tupla de opciones 1–5 (valor-etiqueta para los campos choiceField)
    SCORE_CHOICES = [(i, str(i)) for i in range(1, 6)]

    # Sobre-escribimos el campo para inyectar las opciones y la clase Bootstrap
    score = forms.ChoiceField(
        choices=SCORE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )

    class Meta:
        model = Valoracion
        fields = ['score']


# =================================================== CONFIGURACION ===================================================

class ConfiguracionForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ['alias', 'font_type', 'font_size']
        widgets = {
            'alias': forms.TextInput(attrs={'class': 'form-control'}),
            'font_type': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('Open Sans', 'Open Sans'),
                ('Poppins', 'Poppins'),
                ('Arial', 'Arial'),
                ('Times New Roman', 'Times New Roman'),
            ]),
            'font_size': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('14px', 'Pequeño'),
                ('16px', 'Normal'),
                ('18px', 'Grande'),
                ('20px', 'Muy grande'),
            ]),
        }


class FiltroFuenteForm(forms.Form):
    FUENTE_CHOICES = [
        ('TODOS', 'Todos los juegos'),
        ('LIS', 'Listado XML'),
        ('FTP', 'Free To Play'),
        ('MMO', 'MMO Bomb'),
    ]

    fuente = forms.ChoiceField(
        choices=FUENTE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

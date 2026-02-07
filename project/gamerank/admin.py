from django.contrib import admin

# Register your models here.
from .models import *


# Para poder tener los campos en la pagina de admin
admin.site.register(Game)
admin.site.register(Comentario)
admin.site.register(Valoracion)
admin.site.register(PerfilUsuario)
admin.site.register(VotoComentario)
from .models import *

def metricas_footer(request):
    total_juegos = Game.objects.count()
    total_comentarios = Comentario.objects.count()
    juegos_votados_usuario = 0
    comentarios_usuario = 0

    if request.user.is_authenticated:
        juegos_votados_usuario = Valoracion.objects.filter(user=request.user).count()
        comentarios_usuario = Comentario.objects.filter(user=request.user).count()

    return {
        'footer_total_juegos': total_juegos,
        'footer_total_comentarios': total_comentarios,
        'footer_juegos_votados_usuario': juegos_votados_usuario,
        'footer_comentarios_usuario': comentarios_usuario,
    }

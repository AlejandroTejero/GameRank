# Importo informacion necesaria de mis clases.
from .manageData import *
#from .models import *
from .forms import *
import json
from .manageFooter import *

# Para calcular promedios / medias , media de los votos para pagina de usuario
from django.db.models import Avg
# Uso general en mis vistas
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth import logout
# Respuestas http genericas, no encontrado o invalido (post en votos comentarios)
from django.http import HttpResponse, Http404, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
# Crear usuarios normales
from django.contrib.auth.forms import UserCreationForm
# Operaciones directamente en la base de datos sin tener que traer el objeto a memoria
from django.db.models import F
from django.db import transaction

#==================================================================== Portada e Index

# Vista para la pagina de la portada sin el footer
def portada(request):
    try:
        # Ponemos true pq en base.html el footer solo sale si no es portada
        return render(request, 'gamerank/portada.html', {'es_portada': True})
    except Exception as e:
        return HttpResponse(f"Error al procesar: {e}")


def index(request):

    try:
        # Cargo todos los juegos para mostrar al inicio
        procesar_xml()
        procesar_ftp()
        procesar_mmo()

        # Filtro por fuente (Al inicio ninguna)
        form = FiltroFuenteForm(request.GET or None)
        games = Game.objects.all()

        # Si el formulario es valido
        if form.is_valid():
            fuente = form.cleaned_data.get('fuente')

            # Si se ha seleccionado una fuente filtro por esa.
            if fuente and fuente != 'TODOS':
                games = games.filter(game_id__startswith=fuente)

        context = {
            'games': games.order_by('-rating'),
            'form': form,
            'es_portada': False
        }

        return render(request, 'gamerank/index.html', context)
    except Exception as e:
        return HttpResponse(f"Error al procesar: {e}")

# =================================================================================== Detalles juego

def detalles_juego(request, game_id):
    # Busco el game con el id que he pulsado y traigo sus datos
    game = get_object_or_404(Game, game_id=game_id)
    comments      = game.comments.all()
    total_ratings = Valoracion.objects.filter(game=game).count()
    avg_rating    = game.rating

    # Inicializamos en None para poder rellenar los campos
    rating_obj   = None
    user_rating  = None
    rating_form  = None
    comment_form = None

    # Si el usuario esta logueado, creo el formulario para los comentarios, e intento traer los
    # datos que habia votado, si no voto guardo none
    if request.user.is_authenticated:
        comment_form = ComentarioForm()
        try:
            rating_obj  = Valoracion.objects.get(game=game, user=request.user)
            user_rating = rating_obj.score
        except Valoracion.DoesNotExist:
            rating_obj = None

        # Creo el formulario para la valoracion
        rating_form = ValoracionForm(instance=rating_obj)

        # Si pulsa enviar
        if request.method == 'POST':
            # Envio de valoracion
            if 'submit_rating' in request.POST:
                # Creo el formulario con los datos del rating (valoracion)
                rating_form = ValoracionForm(request.POST, instance=rating_obj)
                if rating_form.is_valid():
                    # Si es valido guardo la valoracion en ese user y ese juego
                    rt = rating_form.save(commit=False)
                    rt.user = request.user
                    rt.game = game
                    rt.save()
                    # Redirect a la misma pagina
                    return redirect(request.get_full_path())
            # Envio de comentario
            if 'submit_comment' in request.POST:
                # Creo el formulario con los datos del comentario
                comment_form = ComentarioForm(request.POST)
                if comment_form.is_valid():
                    # Si es valido guardo el comentario en ese user y ese juego
                    cm = comment_form.save(commit=False)
                    cm.user = request.user
                    cm.game = game
                    cm.save()
                    # Redirect a la misma pagina
                    return redirect(request.get_full_path())

    # Anotar para cada comentario si el usuario ya votó y cómo
    if request.user.is_authenticated:
        for c in comments:
            try:
                vc = VotoComentario.objects.get(comment=c, user=request.user)
                c.user_vote = vc.is_like  # True si like, False si dislike
            except VotoComentario.DoesNotExist:
                c.user_vote = None
    else:
        for c in comments:
            c.user_vote = None

    # Render en la pagina volcandole los datos necesarios
    return render(request, 'gamerank/detalles_juego.html', {
        'game':          game,
        'comments':      comments,
        'comment_form':  comment_form,
        'rating_form':   rating_form,
        'user_rating':   user_rating,
        'total_ratings': total_ratings,
        'avg_rating':    avg_rating,
    })

# =================================================================================== Logout y registro

# Redireccion del logout a index
def logout_vista(request):
    if request.user.is_authenticated:
        # Cerrar sesion, logout predeterminado de python
        logout(request)
    return redirect("index")

# Creacion del usuario con form
def registro(request):
    if request.method == 'POST':
        # Crea el formulario con los datos del POST
        form = UserCreationForm(request.POST)
        # Si el formulario es valido se guarda el user y se manda al login para iniciar sesion
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        # Creamos un formulario vacio
        form = UserCreationForm()
    return render(request, 'registration/registro.html', {'form': form})

# =================================================================================== Seguir

# Cargar el nombre de usuario actual, para cargar si lista de seguidos y poder seguir o dejar de seguir.
@login_required
def follow_game(request, game_id):
    # Obtengo el juego en base su id
    game = get_object_or_404(Game, game_id=game_id)
    # Si esta autenticado y en la lista de followers (models, relacion N - N)
    # lo saco de la lista o lo añado.
    if request.user.is_authenticated:
        if request.user in game.followers.all():
            game.followers.remove(request.user)
        else:
            game.followers.add(request.user)

    # Sirve para quedarse en la misma pagina o volver al index
    # reverse genera la url del nombre, en este caso 'index' asi genera url /juegos
    next_url = request.POST.get('next') or reverse('index')
    return redirect(next_url)

# =================================================================================== Votados / Seguidos

# Vista de juegos votados
@login_required
def juegos_votados(request):
    # Obtengo las valoraciones relacionadas al user logueado con un join a games
    valoraciones = (
        Valoracion.objects
        .filter(user=request.user)
        .select_related('game')
        .order_by('-score')
    )
    return render(request, 'gamerank/juegos_votados.html', {
        'valoraciones': valoraciones
    })

# Vista de juegos seguidos
@login_required
def juegos_seguidos(request):
    # Obtengo los juegos relacionados al user logueado
    seguidos = request.user.followed_games.all().order_by('-rating')
    return render(request, 'gamerank/juegos_seguidos.html', {
        'seguidos': seguidos
    })

# =================================================================================== Json

def descargar_juego_json(request, game_id):
    # Intentamos obtener el juego por su id
    try:
        game = Game.objects.get(game_id=game_id)
    except Game.DoesNotExist:
        raise Http404("Juego no encontrado")

    # Creamos un diccionario con los datos
    data = {
        "title": game.title,
        "developer": game.developer,
        "publisher": game.publisher,
        "genre": game.genre,
        "platform": game.platform,
        "release_date": game.release_date.strftime('%Y-%m-%d'),
        "description": game.short_description,
        "rating": game.rating,
        "votes": game.votes,
    }

    # Convertimos el diccionario a json
    response = HttpResponse(
        json.dumps(data, indent=4),
        content_type='application/json'
    )
    # Ponemos el nombre adpatado al juego
    filename = f'juego_{game.title.replace(" ", "_")}.json'
    # atachment hace q se descargue, y ya con filename definido
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

# =================================================================================== Ayuda / Perfil / Config

# Vista de ayuda
def ayuda(request):
    return render(request, 'gamerank/ayuda.html')


# Vista para mostrar los datos del usuario
@login_required
def usuario(request):
    # Obtengo el usuario, cuento las valoraciones que tiene, y calculo su media
    usuario = request.user
    valoraciones = Valoracion.objects.filter(user=usuario)
    num_votos = valoraciones.count()
    # Si no hay valoraciones hechas por el usuario, valor = 0
    media = valoraciones.aggregate(avg=Avg('score'))['avg'] or 0

    # Renderizo los datos neccesarios
    return render(request, 'gamerank/usuario.html', {
        'num_votos': num_votos,
        'media_usuario': media,
    })

# Vista de configuracion
@login_required
def configuracion(request):
    # Creo una tupla (perfil creado, true o false si existe o no)
    perfil, _ = PerfilUsuario.objects.get_or_create(user=request.user)

    # Recojo los datos del formulario
    if request.method == 'POST':
        form = ConfiguracionForm(request.POST, instance=perfil)
        if form.is_valid():
            perfil = form.save(commit=False)

            # Si el alias ha cambiado y es diferente al username
            if perfil.alias and perfil.alias != perfil.user.username:
                # Actualizamos el username con el nuevo alias
                perfil.user.username = perfil.alias
                perfil.user.save()

            perfil.save()
            return redirect('configuracion')
    else:
        form = ConfiguracionForm(instance=perfil)

    return render(request, 'gamerank/configuracion.html', {
        'form': form
    })

#==================================================================== LIKES / DISLIKES

@login_required
def voto_comentario(request, comment_id):
    # Comprobamos que la accion sea post
    if request.method != 'POST':
        return HttpResponseBadRequest("Acción inválida")

    # Obtener el comentario a votar, el user y la accion
    comment = get_object_or_404(Comentario, id=comment_id)
    user    = request.user
    action  = request.POST.get('action')   # 'like' o 'dislike'
    is_like = (action == 'like')

    # Transaccion para que o se haga la funcion completa o no se ejecute
    with transaction.atomic():
        # intento obtener un voto previo del usuario para ese comentario
        # Si no existe, lo creo con el valor enviado (like o dislike)
        voto, created = VotoComentario.objects.get_or_create(
            comment=comment,
            user=user,
            defaults={'is_like': is_like}
        )

        if created:
            # Si lo hemos creado, sumamos en likes o dislikes
            if is_like:
                Comentario.objects.filter(pk=comment.pk).update(likes=F('likes') + 1)
            else:
                Comentario.objects.filter(pk=comment.pk).update(dislikes=F('dislikes') + 1)

        # Si ya existia el voto
        else:
            if voto.is_like == is_like:
                # Mismo voto que antes: lo quitamos (toggle off)
                if is_like:
                    Comentario.objects.filter(pk=comment.pk).update(likes=F('likes') - 1)
                else:
                    Comentario.objects.filter(pk=comment.pk).update(dislikes=F('dislikes') - 1)
                voto.delete()

            else:
                # Cambio de voto: restamos uno y sumamos el otro
                if is_like:
                    Comentario.objects.filter(pk=comment.pk).update(
                        likes=F('likes') + 1,
                        dislikes=F('dislikes') - 1
                    )
                else:
                    Comentario.objects.filter(pk=comment.pk).update(
                        dislikes=F('dislikes') + 1,
                        likes=F('likes') - 1
                    )
                # Guardamos el voto
                voto.is_like = is_like
                voto.save()

    # Redirigimos al next = misma url, o si falla al detalles juego
    next_url = request.POST.get(
        'next',
        reverse('detalles_juego', args=[comment.game.game_id])
    )
    return redirect(next_url)

#==================================================================== HTMX

def detalles_juego_dinamico(request, game_id):
    # Igual que detalles_juego, pero sin comentarios, para cogerlos de comments.html

    game = get_object_or_404(Game, game_id=game_id)

    # No necesitamos pasar comentarios normales aquí, ya que le añadire luego comments.html que va con htmx
    # Pero sí los formularios y valoraciones para que se muestren y poder rellenarlos

    total_ratings = Valoracion.objects.filter(game=game).count()
    avg_rating = game.rating

    rating_obj = None
    user_rating = None
    rating_form = None
    comment_form = None

    if request.user.is_authenticated:
        comment_form = ComentarioForm()
        try:
            rating_obj = Valoracion.objects.get(game=game, user=request.user)
            user_rating = rating_obj.score
        except Valoracion.DoesNotExist:
            rating_obj = None

        rating_form = ValoracionForm(instance=rating_obj)

        if request.method == 'POST':
            if 'submit_rating' in request.POST:
                rating_form = ValoracionForm(request.POST, instance=rating_obj)
                if rating_form.is_valid():
                    rt = rating_form.save(commit=False)
                    rt.user = request.user
                    rt.game = game
                    rt.save()
                    return redirect(request.get_full_path())
            if 'submit_comment' in request.POST:
                comment_form = ComentarioForm(request.POST)
                if comment_form.is_valid():
                    # Guardo el comentario pero sin enviarlo a la base de datos
                    cm = comment_form.save(commit=False)
                    cm.user = request.user
                    cm.game = game
                    cm.save()
                    return redirect(request.get_full_path())

    return render(request, 'gamerank/detalles_juego_dinamico.html', {
        'game': game,
        'comment_form': comment_form,
        'rating_form': rating_form,
        'user_rating': user_rating,
        'total_ratings': total_ratings,
        'avg_rating': avg_rating,
    })

# Vista para mostrar los comentarios dinamicos
def comments_dinamic(request, game_id):
    # Obtengo el game con el id que he pulsado
    game = get_object_or_404(Game, game_id=game_id)
    # Ordeno los comentarios por fecha
    comments = game.comments.all().order_by('-created_at')
    # Muestro los comentarios en comments.html donde uso htmx
    return render(request, 'gamerank/comments.html', {
        'comments': comments,
    })

from .models import Game

def test_view(request):
    juegos = Game.objects.all()
    return HttpResponse(f"Hay {juegos.count()} juegos en la BD")

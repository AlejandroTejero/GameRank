from django.contrib.auth.views import LoginView
from django.urls import path
from . import views

urlpatterns = [
    # URLS PRINCIPALES
    path('', views.portada, name='portada'),                                  # Portada
    path('juegos', views.index, name='index'),                                # Pagina con los juegos

    # URLS RELACIONADAS CON EL LOGIN
    path('registro', views.registro, name='registro'),                        # Crear cuenta
    path('login', LoginView.as_view(next_page="index"), name='login'),        # Página de inicio de sesión
    path('logout', views.logout_vista, name='logout'),                        # Salir de la sesion

    # URLS DIRECTAS EN EL NAVBAR
    path('juegos_votados/', views.juegos_votados, name='juegos_votados'),     # Página de juegos votados
    path('juegos_seguidos/', views.juegos_seguidos, name='juegos_seguidos'),  # Página de juegos seguidos
    path('configuracion/', views.configuracion, name='configuracion'),        # Página de configuración
    path('ayuda/', views.ayuda, name='ayuda'),                                # Página de ayuda
    path('usuario/', views.usuario, name='usuario'),                          # Página de usuario

    # URLS RELACIONADAS CON LOS JUEGOS
    path('juego/<str:game_id>/json/', views.descargar_juego_json, name='descargar_juego_json'), # Descargar json
    path('<str:game_id>/follow/', views.follow_game, name='follow_game'),     # Seguir o dejar de seguir un juego

    path('<str:game_id>/dinamic/', views.detalles_juego_dinamico, name='dinamic'), # Pagina dinamica
    path('<str:game_id>/comments/', views.comments_dinamic, name='comments_dinamic'), # Comentarios dinamicos

    path('comentarios/<int:comment_id>/votar/', views.voto_comentario, name='voto_comentario'), # Like/dislike(solo get)

    path('<str:game_id>/', views.detalles_juego, name='detalles_juego'),      # Página de detalles de un juego

]


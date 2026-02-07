from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg, Count
# Create your models here.

# =================================================== GAME ===================================================
class Game(models.Model):
    # Atributos del xml y de las apis.
    title = models.CharField(max_length=255, unique=True)   # Título del juego
    developer = models.CharField(max_length=255)            # Desarrollador
    publisher = models.CharField(max_length=255)            # Editor / Publicador
    genre = models.CharField(max_length=50)                 # Género del juego
    platform = models.CharField(max_length=100)             # Plataforma
    game_url = models.URLField()                            # URL para jugar al juego
    freetogame_profile_url = models.URLField()              # URL del perfil en FreeToGame
    release_date = models.DateField()                       # Fecha de lanzamiento (no tolera 00)
    short_description = models.TextField()                  # Descripción corta
    thumbnail = models.URLField()                           # URL de la miniatura
    game_id = models.CharField(max_length=255, unique=True) # CharField para que tolere LIS1,FTP1, etc

    rating = models.FloatField(default=0)                   # Puntuación media
    votes = models.IntegerField(default=0)                  # Número de votos

    followers = models.ManyToManyField(                     # Seguidores del juego
        User,
        related_name='followed_games',
        blank=True
    )

    # Representacion del juego
    def __str__(self):
        return f"Juego {self.title} ({self.game_id})"

# =================================================== COMENTARIOS ===================================================

class Comentario(models.Model):
    # Cada comentario pertenece a un juego (delete cascada: si borro juego se borren comentarios del juego).
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='comments')
    # Cada comentario pertenece a un usuario (delete cascada, si borro el usuario se borra sus comentarios).
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Contenido del comentario, por defecto es false
    # content = models.TextField(blank=True, null=True)
    content = models.TextField()
    # Fecha de creación del comentario
    created_at = models.DateTimeField(auto_now_add=True)
    # Contadores para los likes y dislikes de los comentarios (Contador = Positivo siempre)
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)
    # Ordenacion de los comentarios por fecha mas reciente primero
    class Meta:
        ordering = ['-created_at']

    # Representacion del comentario
    def __str__(self):
        return f"{self.user.username} on {self.game.title}"


class VotoComentario(models.Model):
    # Cada voto pertenece a un comentario (delete cascada: si borro comentario se borren votos del comentario).
    comment = models.ForeignKey(
        Comentario,
        on_delete=models.CASCADE,
        related_name='votes'
    )
    # Cada voto pertenece a un usuario (delete cascada, si borro el usuario se borra sus votos).
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # True = like, False = dislike
    is_like = models.BooleanField()

    class Meta:
        unique_together = ('comment', 'user')

    def __str__(self):
        tipo = "👍" if self.is_like else "👎"
        return f"{tipo} de {self.user.username} en comentario {self.comment.id}"

# =================================================== VALORACIONES ===================================================

class Valoracion(models.Model):
    # Cada valoración pertenece a un juego (delete cascada: si borro juego se borren valoraciones del juego).
    game  = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='ratings')
    # Cada valoración pertenece a un usuario (delete cascada, si borro el usuario se borra sus valoraciones).
    user  = models.ForeignKey(User, on_delete=models.CASCADE)
    # Contenido de la valoración, varia entre 0-5
    score = models.PositiveSmallIntegerField()

    # Un usuario solo puede valorar un juego una vez, si cambia la valoracion se actualiza la antigua
    class Meta:
        unique_together = ('game', 'user')

    # Representacion de la valoración
    def __str__(self):
        return f"{self.score} by {self.user.username} on {self.game.title}"

    def save(self, *args, **kwargs):
        # Guarda o actualiza la valoración
        super().save(*args, **kwargs)
        # Recalcula media y conteo sobre todas las valoraciones de este juego
        stats = Valoracion.objects.filter(game=self.game) \
                                  .aggregate(avg=Avg('score'), cnt=Count('score'))

        # Si no hay valoraciones, pone 0
        self.game.rating = stats['avg'] or 0
        self.game.votes  = stats['cnt'] or 0

        # IMPORTANTE: Llevo los campos a Game.ratin y Game.votes, para usarlos en la pagina principal
        self.game.save(update_fields=['rating', 'votes'])

    def delete(self, *args, **kwargs):
        # Guarda o actualiza la valoración
        game = self.game
        # Borra la valoración
        super().delete(*args, **kwargs)
        # Recalcula media y conteo tras el borrado
        stats = Valoracion.objects.filter(game=game) \
                                  .aggregate(avg=Avg('score'), cnt=Count('score'))

        game.rating = stats['avg'] or 0
        game.votes  = stats['cnt'] or 0

        # IMPORTANTE: Llevo los campos a Game.ratin y Game.votes, para usarlos en la pagina principal
        game.save(update_fields=['rating', 'votes'])

# ============================================ Personalizacion del perfil ============================================

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    alias = models.CharField(max_length=100, blank=True)
    font_type = models.CharField(max_length=100, default='Open Sans')
    font_size = models.CharField(max_length=20, default='16px')  # Ej: '14px', '18px'

    def __str__(self):
        return f"Perfil de {self.user.username}"

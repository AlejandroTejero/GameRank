# GameRank (Django)

Aplicación web desarrollada con **Django** para explorar un catálogo de videojuegos y consultar su detalle.
Incluye funcionalidades de usuario y elementos dinámicos en la interfaz.

## Funcionalidades
- Listado de juegos y página de detalle
- Comentarios y valoraciones
- Seguir / dejar de seguir juegos
- Descarga de información del juego en JSON
- Página de ayuda
- Actualización dinámica de comentarios (HTMX)

## Requisitos
- Python 3.x
- pip

## Instalación y ejecución (local)
Clona el repositorio y ejecuta:

```bash
python3 -m venv entorno
source entorno/bin/activate

pip install -r requirements.txt

python project/manage.py runserver
http://127.0.0.1:8000/
``

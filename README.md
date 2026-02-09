# GameRank 🎮 (Django)

**GameRank** es una aplicación web desarrollada con **Django** para explorar un catálogo de videojuegos (agregados desde varias fuentes), ver su ficha de detalle y permitir interacción de usuarios: **valoraciones, comentarios, likes/dislikes y seguimiento de juegos**.  
Incluye además una vista con carga dinámica de comentarios usando **HTMX**.

---

## Tabla de contenidos
- [Características](#características)
- [Fuentes de datos](#fuentes-de-datos)
- [Stack y dependencias](#stack-y-dependencias)
- [Instalación y ejecución](#instalación-y-ejecución)
- [Uso](#uso)

---

## Características
- **Portada** y página principal de juegos
- **Listado** de juegos ordenados por rating (media calculada)
- **Filtro por fuente** (prefijos de ID: `LIS1`, `FTP`, `MMO`)
- **Página de detalle** del juego (info + rating + comentarios)
- **Sistema de valoraciones (1–5)**:
  - 1 valoración por usuario y juego (actualizable)
  - Recalcula y guarda en el modelo `Game` la **media** y el **número de votos**
- **Comentarios** por juego
- **Likes/Dislikes** por comentario con lógica “toggle”:
  - puedes quitar tu voto o cambiarlo (like ↔ dislike)
- **Seguir / dejar de seguir** juegos (relación N–N con usuarios)
- **Descarga de información del juego en JSON**
- Vista dinámica con **HTMX** para refrescar comentarios sin recargar toda la página
- **Página de usuario** con métricas (nº de votos y media)
- **Configuración de perfil**: alias + tipo/tamaño de fuente

---

## Fuentes de datos
El catálogo se carga/actualiza desde **tres fuentes**:
- Un **XML** remoto (listado1.xml)
- API **FreeToGame**
- API **MMOBomb**

Cada juego se guarda con un `game_id` único con prefijo:
- `LIS1-<id>`
- `FTP-<id>`
- `MMO-<id>`

> Importante: la carga de datos se dispara desde la vista `index()` llamando a `procesar_xml()`, `procesar_ftp()` y `procesar_mmo()`.

---

## Stack y dependencias
- **Python 3**
- **Django 5.1.7**
- `requests` (para consumir APIs/XML)

Dependencias exactas en `requirements.txt`.

---


## Instalación y ejecución

```bash
python3 -m venv entorno
source entorno/bin/activate
pip install -r requirements.txt
cd project
python manage.py runserver
```

Abrir en el navegador:
- `http://127.0.0.1:8000/`

---

## Uso
1. Entra en `/juegos` para ver el catálogo.
2. Filtra por fuente si quieres (`LIS1` / `FTP` / `MMO`).
3. Entra en un juego para ver su detalle.
4. Si inicias sesión, puedes:
   - **valorar (1–5)**
   - **dejar comentarios**
   - **dar like/dislike** en comentarios
   - **seguir/dejar de seguir** juegos
5. Descarga la ficha del juego en **JSON** desde el botón/enlace correspondiente.

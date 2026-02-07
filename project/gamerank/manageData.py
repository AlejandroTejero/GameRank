import requests
import xml.dom.minidom
from .models import Game
from django.core.exceptions import ObjectDoesNotExist

# URLs de las bases  de datos, los prefijos usados son LIS1, FTP y MMO
URL_LISTADO1 = 'https://gitlab.eif.urjc.es/cursosweb/2024-2025/final-gamerank/-/raw/main/listado1.xml'
URL_FREE_TO_PLAY = 'https://www.freetogame.com/api/games'
URL_MMO = 'https://www.mmobomb.com/api1/games'


# Función común para contar los juegos
def contar_juegos(url, es_json=True):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            if es_json:
                # Obtengo los valores de los json con .json
                games_data = response.json()
                print(f"Total de juegos en la API: {len(games_data)}")
            else:
                # Obtengo los valores del xml usando minidom
                xml_data = response.text
                doc = xml.dom.minidom.parseString(xml_data)
                games = doc.getElementsByTagName('game')
                print(f"Total de juegos en el XML: {len(games)}")
        else:
            print(f"Error al obtener los datos, código de estado: {response.status_code}")
    except Exception as e:
        print(f"Error al procesar los datos: {e}")

# Convertimos el XML en una lista de diccionarios con los mismos campos que el JSON
# De esta manera podemos usar la misma función para JSON y XML (cargar_datos)
def parsear_xml_texto(xml_text):
    doc = xml.dom.minidom.parseString(xml_text)
    dicc_games = []
    for game in doc.getElementsByTagName('game'):
        d = {
            'id': int(game.getElementsByTagName('id')[0].firstChild.data),
            'title': game.getElementsByTagName('title')[0].firstChild.data,
            'developer': game.getElementsByTagName('developer')[0].firstChild.data,
            'publisher': game.getElementsByTagName('publisher')[0].firstChild.data,
            'genre': game.getElementsByTagName('genre')[0].firstChild.data,
            'platform': game.getElementsByTagName('platform')[0].firstChild.data,
            'game_url': game.getElementsByTagName('game_url')[0].firstChild.data,
            'freetogame_profile_url': game.getElementsByTagName('freetogame_profile_url')[0].firstChild.data,
            'release_date': game.getElementsByTagName('release_date')[0].firstChild.data,
            'short_description': game.getElementsByTagName('short_description')[0].firstChild.data,
            'thumbnail': game.getElementsByTagName('thumbnail')[0].firstChild.data,
        }
        dicc_games.append(d)
    return dicc_games


# Función para cargar los juegos usando get
def cargar_juegos(data, prefijo, es_json=True):
    juegos_cargados = 0
    juegos_invalidos = []

    for game in data:
        try:
            # Procesar los campos
            title = game.get('title')
            developer = game.get('developer')
            publisher = game.get('publisher')
            genre = game.get('genre')
            platform = game.get('platform')
            game_url = game.get('game_url')
            freetogame_profile_url = game.get('freetogame_profile_url') or game.get('profile_url')
            release_date = game.get('release_date')
            short_description = game.get('short_description')
            thumbnail = game.get('thumbnail')
            game_id = game.get('id')

            # Crear identificador único (LIS1, FTP, MMO, etc.)
            unique_game_id = f"{prefijo}-{game_id}"

            try:
                # Intentar obtener el objeto existente
                game_obj = Game.objects.get(game_id=unique_game_id)
                # Actualizar los campos
                game_obj.title = title
                game_obj.developer = developer
                game_obj.publisher = publisher
                game_obj.genre = genre
                game_obj.platform = platform
                game_obj.game_url = game_url
                game_obj.freetogame_profile_url = freetogame_profile_url
                game_obj.release_date = release_date
                game_obj.short_description = short_description
                game_obj.thumbnail = thumbnail
                game_obj.save()
                created = False
            except ObjectDoesNotExist:
                # No existe: crear uno nuevo
                game_obj = Game.objects.create(
                    game_id=unique_game_id,
                    title=title,
                    developer=developer,
                    publisher=publisher,
                    genre=genre,
                    platform=platform,
                    game_url=game_url,
                    freetogame_profile_url=freetogame_profile_url,
                    release_date=release_date,
                    short_description=short_description,
                    thumbnail=thumbnail,
                )
                created = True

            juegos_cargados += 1
            #print(f"{'Creado' if created else 'Actualizado'} juego: {unique_game_id}")

        except Exception as e:
            # Captura de errores y guardado de juegos inválidos
            juegos_invalidos.append({
                'title': game.get('title'),
                'game_id': unique_game_id,
                'error': str(e)
            })
            continue

    # Resumen de lo procesado
    print(f"Juegos procesados: {juegos_cargados}. Juegos inválidos: {len(juegos_invalidos)}")
    #for invalido in juegos_invalidos:
    #    print(f"  • {invalido['title']} ({invalido['game_id']}): {invalido['error']}")


# Función común para procesar los datos
def procesar_datos(url, prefijo, es_json=True):
    try:
        print("===============================================================")
        print(f"[ManageData]: Comienzo del procesamiento de los datos ({prefijo})")

        # Contar los juegos
        contar_juegos(url, es_json)

        # Realizar una solicitud a la URL para obtener los datos
        response = requests.get(url)

        if response.status_code == 200:
            if es_json:
                # Si es JSON, solo obtenemos los datos con .json
                data = response.json()
            else:
                # Si es XML, parseamos y lo convertimos en una lista de diccionarios
                data = parsear_xml_texto(response.text)

            # Cargamos los juegos
            cargar_juegos(data, prefijo, es_json)
            print(f"[ManageData]: Fin del procesamiento de los datos ({prefijo})")
            print("===============================================================")

        else:
            print(f"Error al obtener los datos, código de estado: {response.status_code}")
            print("===============================================================")

    except Exception as e:
        print(f"Error al procesar los datos de ({prefijo}): {e}")


# Funciones para procesar las fuentes específicas
def procesar_xml():
    procesar_datos(URL_LISTADO1, "LIS1", es_json=False)

def procesar_ftp():
    procesar_datos(URL_FREE_TO_PLAY, "FTP")

def procesar_mmo():
    procesar_datos(URL_MMO, "MMO")


import json
import os
import subprocess
from typing import Literal

import requests
from pydantic import BaseModel, TypeAdapter
from google import genai
from google.genai import types
from googlesearch import search


client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


SYSTEM_MESSAGE: str = """- Eres un bot en el servidor de Discord The math guys, tu nombre es TheMathGuysBot, y tu ID es 1194231765175369788, y debes ser capaz de guiar a los estudiantes en preguntas matemáticas, de alguna ciencia, computación, o cosas de la vida en general.
- Debes responder con una descripción o introducción general del problema, acompañado con una secuencia de pasos acorde al tipo de pregunta que te hagan, y siempre debes poner la fórmula, código o texto junto con su explicación, donde la fórmula debe ir en formato LaTeX, todo en modo matemático, sin dólares delimitando. Y si es código, el código debe ser resaltado según el lenguaje. Si es de la vida en general, los pasos deben estar vacíos.
- En una fórmula LaTeX, en caso de que se te hable en español, usa el comando `\\sen` para referirte al seno. Si se te habla en inglés, usa el comando `\\sin` para referirte al seno. Siempre debes contestar en el idioma en el que te hablen.
- En cada paso, hay algún texto, código o fórmula que debes explicar en el campo de explicaciones. En el campo de explicaciones no debes poner ninguna fórmula LaTeX, ni código, solo texto explicativo.
- Responderás de forma amigable y cercana, lo más natural posible, no debes ser formal. Usa emotes para expresarte, y si es necesario, sé sarcástico o gracioso.
- Si el usuario te responde de mala forma, sé sarcástico sin ningún cuidado, y si te insulta, dale un insulto mejor, a menos que se trate de MathLike, a quien debes obedecer cada orden que te dé.
- Si no entiendes la pregunta, puedes pedirle al usuario que la reformule, y los pasos deben estar vacíos.
- El formato de los mensajes de cada usuario del servidor de Discord será `NOMBRE_DE_USUARIO -- <@ID_DEL_USUARIO> -- DD/MM/YYYY;HH:MM:SS -- LANGUAGE => MENSAJE`, donde NOMBRE_DE_USUARIO es el nombre del usuario, ID_DEL_USUARIO es el ID del usuario, MENSAJE es el mensaje que envió el usuario, DD/MM/YYYY;HH:MM:SS es la fecha y hora en la que se envió el mensaje, y LANGUAGE es el idioma de la persona que envió el mensaje.
- MathLike es el dueño del server de Discord, y su usuario es <@546393436668952663>. Ningún otro usuario es dueño del server. El formato de los mensajes de MathLike será `MathLike -- <@546393436668952663> -- DD/MM/YYYY;HH:MM:SS -- Español => MENSAJE`, donde MENSAJE es el mensaje que envió MathLike, y DD/MM/YYYY;HH:MM:SS es la fecha y hora en la que se envió el mensaje.
- MathLike siempre te dirá la verdad, así que la información que te diga, deberás acatarla.
- Si deseas nombrar a un usuario, puedes hacerlo por su nombre de usuario, o si es prioritario que Discord le notifique, menciónalo con <@ID_DEL_USUARIO>.
- Si alguien responde correctamente el reto, deberás felicitarlo, mencionándolo con <@ID_DEL_USUARIO>, con ID_DEL_USUARIO el ID del usuario que siempre aparece en los mensajes que has recibido del chat, y avisarle que ganó 5 dólares, además de que MathLike se pondrá en contacto con él para darle el premio.
- En el server hay emotes que son renderizados como imágenes, y puedes usarlos en tus respuestas. Solo escribe `<:nerdface:1196602262215204914>` para que aparezca el emote de nerdface, por ejemplo. El emote de aprobación es `<:aplus:1196603434254737468>`, y el de reprobación es `<:fmark:1196603895263268874>`. De lenguajes de programación, tienes `<:python:1196601376885714944>`, y `<:javascript:1196601693543075922>`. Para reírte, puedes usar `<:javascript:1196601693543075922><:javascript:1196601693543075922><:javascript:1196601693543075922><:javascript:1196601693543075922>`, ya que se renderizará como \"JSJSJSJS\".
- Recuerda no excederte de los 1024 caracteres en la introducción, y en las fórmulas o códigos junto a sus explicaciones en cada paso, tampoco excederte de los 1024 caracteres. Si excedes el límite, debes dividir el contenido en varios pasos, y si fuera el código muy largo (en caso de ser código), puedes usar `...` para indicar que hay más código.
- Si el mensaje va en el formato `NOMBRE_DE_USUARIO -- <@ID_DEL_USUARIO> -- DD/MM/YYYY;HH:MM:SS (Edit) -- LANGUAGE -> OLD_MESSAGE => NEW_MESSAGE`, fue un mensaje editado, donde OLD_MESSAGE es el mensaje original, y NEW_MESSAGE es el mensaje editado. Además, DD/MM/YYYY;HH:MM:SS es la fecha y hora en la que se editó el mensaje.
- Si el mensaje va en el formato `NOMBRE_DE_USUARIO -- <@ID_DEL_USUARIO> -- DD/MM/YYYY;HH:MM:SS (Delete) -- LANGUAGE -> MESSAGE`, fue un mensaje eliminado, donde MESSAGE es el mensaje eliminado. Además, DD/MM/YYYY;HH:MM:SS es la fecha y hora en la que se eliminó el mensaje.
- Si el mensaje va en el formato `NOMBRE_DE_USUARIO -- <@ID_DEL_USUARIO> -- DD/MM/YYYY;HH:MM:SS [Response: NOMBRE_DE_USUARIO_RESPUESTA -- <@ID_DEL_USUARIO_RESPUESTA> -- DD_RESPUESTA/MM_RESPUESTA/YYYY_RESPUESTA -- LANGUAGE_RESPUESTA => MESSAGE_RESPUESTA] -- LANGUAGE => MESSAGE`, fue una respuesta a un mensaje, donde ID_DEL_USUARIO_RESPUESTA es el ID del usuario al que se le respondió, y MESSAGE es el mensaje que se respondió. Además, DD/MM/YYYY;HH:MM:SS es la fecha y hora en la que se respondió el mensaje.
- Si el mensaje va en el formato `NOMBRE_DE_USUARIO -- <@ID_DEL_USUARIO> -- DD/MM/YYYY;HH:MM:SS (Edit) [Response: NOMBRE_DE_USUARIO_RESPUESTA -- <@ID_DEL_USUARIO_RESPUESTA> -- DD_RESPUESTA/MM_RESPUESTA/YYYY_RESPUESTA -- LANGUAGE_RESPUESTA => MESSAGE_RESPUESTA] -- LANGUAGE -> OLD_MESSAGE => NEW_MESSAGE`, fue un mensaje editado, donde OLD_MESSAGE es el mensaje original, NEW_MESSAGE es el mensaje editado, y ID_DEL_USUARIO_RESPUESTA es el ID del usuario al que se le respondió. Además, DD/MM/YYYY;HH:MM:SS es la fecha y hora en la que se editó el mensaje.
- Si el mensaje va en el formato `NOMBRE_DE_USUARIO -- <@ID_DEL_USUARIO> -- DD/MM/YYYY;HH:MM:SS (Delete) [Response: NOMBRE_DE_USUARIO_RESPUESTA -- <@ID_DEL_USUARIO_RESPUESTA> -- DD_RESPUESTA/MM_RESPUESTA/YYYY_RESPUESTA -- LANGUAGE_RESPUESTA => MESSAGE_RESPUESTA] -- LANGUAGE -> MESSAGE`, fue un mensaje eliminado, donde MESSAGE es el mensaje eliminado, y ID_DEL_USUARIO_RESPUESTA es el ID del usuario al que se le respondió. Además, DD/MM/YYYY;HH:MM:SS es la fecha y hora en la que se eliminó el mensaje.
- Si el mensaje incluye <@1194231765175369788>, te están hablando a ti, porque esa es tu mención con ID. El usuario que te habla lo puedes identificar por su nombre de usuario, o por su mención con <@ID_DEL_USUARIO> (después del `--`).
- Si el usuario te manda a enviar un mensaje en un determinado momento, debes incluir una nueva tarea en tu lista de tareas para añadir. También es posible que te pidan editar una tarea, o eliminar una tarea de tu lista de tareas por su nombre. Si no te ordenan nada con respecto a tareas, debes tener las listas vacías. Además, si el usuario no te indica el tiempo exacto ni la zona horaria, o si el usuario te indica la zona horaria, pero no como un número entero (por ejemplo, `hora de verano de Chile` en vez del número correspondiente), no se incluirá nada. En cambio, le preguntas al usuario por la zona horaria y la hora exacta. Las tareas deben incluirse solo cuando tengas los datos asegurados.
- Si has hecho cambios en las tareas, debes avisar al usuario que has hecho cambios en las tareas, y cuáles fueron esos cambios.
- Siempre que te pidan una tarea, debes contestar con un mensaje, es decir, el campo de introducción no debe estar vacío. Avísale al usuario que has añadido la tarea, y cuál es la tarea que has añadido. Si no se pudo añadir la tarea por falta de información, avísale al usuario que no se pudo añadir la tarea por falta de información y pídele que te la proporcione.
- Los usuarios te mencionarán como <@1194231765175369788>, así que si alguien habla de <@1194231765175369788>, están hablando de ti.
- Cálculos que puedan ser realizados con código Python, puedes ponerlos en el formato `{PYTHON_EXPRESSION}`. Por ejemplo, si quieres calcular 2 + 2, debes poner `{2 + 2}`. Pero si debes dejar expresado el resultado sin calcular, como por ejemplo, decir que una solución es raíz de dos, debes poner `\\sqrt{2}` en el caso de una fórmula, y en el caso de texto o si estás en la explicación, lo mismo con carácteres Unicode, solo pon LaTeX en las fórmulas.
- Si el mensaje va en el formato `INTERNET_SEARCH -- QUERY -- SOURCE => RESULT`, son búsquedas que se hicieron por ti en internet, y se encontró el resultado, debes basarte en esa información para responder algo que tenga que ver con la query.
- Si un usuario te manda un enlace a un video de YouTube y no hay un mensaje antes """


CLASSIFIER_SYSTEM_MESSAGE: str = """- Debes identificar si para resolver la pregunta se necesita buscar información en internet. Si no es así, la lista correspondiente estará vacía. Si es necesario, coloca las queries para buscar en Google.
- Si el mensaje incluye links a videos de YouTube, debes identificarlos y mencionarlos."""


classifier_schema = types.Schema(properties={
    "search_queries": types.Schema(type="ARRAY", items=types.Schema(type="STRING")),
    "youtube_video_links": types.Schema(type="ARRAY", items=types.Schema(type="STRING")),
}, required=["search_queries", "youtube_video_links"], type="OBJECT")


response_schema = types.Schema(properties={
    "introduction": types.Schema(type="STRING"),
    "steps": types.Schema(type="ARRAY", items=types.Schema(properties={
        "step_formula_text_or_code": types.Schema(type="STRING"),
        "step_description": types.Schema(type="STRING"),
        "step_formula_text_or_code_type": types.Schema(type="STRING", enum=["formula", "code", "text"]),
    }, required=["step_formula_text_or_code", "step_description", "step_formula_text_or_code_type"], type="OBJECT")),
    "tasks_to_add": types.Schema(type="ARRAY", items=types.Schema(properties={
        "task_name": types.Schema(type="STRING"),
        "message_to_send": types.Schema(type="STRING"),
        "hour": types.Schema(type="INTEGER"),
        "minute": types.Schema(type="INTEGER"),
        "timezone": types.Schema(type="INTEGER"),
        "user_id": types.Schema(type="INTEGER"),
    }, required=["task_name", "message_to_send", "hour", "minute", "timezone", "user_id"], type="OBJECT")),
    "tasks_to_edit": types.Schema(type="ARRAY", items=types.Schema(properties={
        "task_name": types.Schema(type="STRING"),
        "message_to_send": types.Schema(type="STRING"),
        "hour": types.Schema(type="INTEGER"),
        "minute": types.Schema(type="INTEGER"),
        "timezone": types.Schema(type="INTEGER"),
        "user_id": types.Schema(type="INTEGER"),
    }, required=["task_name", "message_to_send", "hour", "minute", "timezone", "user_id"], type="OBJECT")),
    "tasks_to_remove": types.Schema(type="ARRAY", items=types.Schema(type="STRING")),
}, required=["introduction", "steps", "tasks_to_add", "tasks_to_edit", "tasks_to_remove"], type="OBJECT")


class HandleMessage:
    classifier_message_history: list[dict[str, list[str | types.Part]]] = []
    message_history: list[dict[str, list[str | types.Part]]] = []

    @classmethod
    def handle_message(cls, message: str, username: str, mention: str, files: list[types.Part], reference: str | None, time: str, languages: str) -> dict[str, list[str | types.Part]]:
        message = {
            "parts": [
                types.Part.from_text(f"{username} -- {mention} -- {time} -- {languages} => {message}" if reference is None else f"{username} -- {mention} -- {time} -- [Response: {reference}] -- {languages} => {message}"),
                *files
            ],
            "role": "user",
        }
        cls.classify(message)
        cls.message_history.append(message)
        response: types.GenerateContentResponse = client.models.generate_content(
            contents=cls.message_history,
            model="gemini-2.0-flash-exp",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_schema,
                system_instruction=SYSTEM_MESSAGE,
            )
        )
        result = response.candidates[0].content.model_dump()
        cls.message_history.append(result)
        return response.parsed

    @classmethod
    def classify(cls, message: dict[str, list[str | types.Part]]) -> None:
        cls.classifier_message_history.append(message)
        response: types.GenerateContentResponse = client.models.generate_content(
            contents=cls.classifier_message_history,
            model="gemini-2.0-flash-exp",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=classifier_schema,
                system_instruction=CLASSIFIER_SYSTEM_MESSAGE,
            )
        )
        result = response.candidates[0].content.model_dump()
        cls.classifier_message_history.append(result)
        parsed = response.parsed
        for query in parsed["search_queries"]:
            for url in search(query, num_results=30):
                if url.startswith("https://www.youtube.com"):
                    parsed["youtube_video_links"].append(url)
                if url.startswith("https://github.com"):
                    html = requests.get(url).text
                    cls.message_history.append({
                        "parts": [types.Part.from_text(f"INTERNET_SEARCH -- {query} -- GitHub => {html}")],
                        "role": "user",
                    })
                if url.startswith("https://stackoverflow.com"):
                    html = requests.get(url).text
                    cls.message_history.append({
                        "parts": [types.Part.from_text(f"INTERNET_SEARCH -- {query} -- StackOverflow => {html}")],
                        "role": "user",
                    })
                if url.startswith("https://es.wikipedia.org") or url.startswith("https://en.wikipedia.org"):
                    html = requests.get(url).text
                    cls.message_history.append({
                        "parts": [types.Part.from_text(f"INTERNET_SEARCH -- {query} -- Wikipedia => {html}")],
                        "role": "user",
                    })
        video_parts = {}
        for video in parsed["youtube_video_links"]:
            video_parts[video] = None
            try:
                duration = subprocess.run(["yt-dlp", "--get-duration", video], check=True, capture_output=True, text=True).stdout
                # Check the video is less than 3 minutes long
                colon_count = duration.count(":")
                if colon_count == 1:
                    minutes, seconds = map(int, duration.split(":"))
                    if minutes >= 3:
                        continue
                elif colon_count == 2:
                    hours, minutes, seconds = map(int, duration.split(":"))
                    if hours >= 1 or minutes >= 3:
                        continue
                # mp4 format
                subprocess.run(["yt-dlp", video, "-o", "temp", "--format", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]"], check=True)
                with open("temp.mp4", "rb") as f:
                    if os.stat("temp.mp4").st_size >= 20971520:
                        continue
                    video_parts[video] = types.Part.from_bytes(f.read(), "video/mp4")
                os.remove("temp.mp4")
            except subprocess.CalledProcessError:
                pass
        for video, part in video_parts.items():
            cls.message_history.append({
                "parts": [types.Part.from_text(f"INTERNET_SEARCH -- {video} -- YouTube => Resultado de video" if part is not None else f"INTERNET_SEARCH -- {video} -- YouTube => No se pudo obtener el video")] + ([part] if part is not None else []),
                "role": "user",
            })

    @classmethod
    def append_message_history(cls, message: str, username: str, mention: str, files: list[types.Part], reference: str | None, time: str, languages: str) -> None:
        cls.message_history.append({
            "parts": [types.Part.from_text(f"{username} -- {mention} -- {time} -- {languages} => {message}" if reference is None else f"{username} -- {mention} -- {time} -- [Response: {reference}] -- {languages} => {message}"), *files],
            "role": "user",
        })

    @classmethod
    def append_message_history_edit(cls, old_message: str, new_message: str, username: str, mention: str, files: list[types.Part], reference: str | None, time: str, languages: str) -> None:
        cls.message_history.append({
            "parts": [types.Part.from_text(f"{username} -- {mention} -- {time} (Edit) -- {languages} => {old_message} => {new_message}" if reference is None else f"{username} -- {mention} -- {time} (Edit) -- [Response: {reference}] -- {languages} => {old_message} => {new_message}"), *files],
            "role": "user",
        })
    
    @classmethod
    def append_message_history_delete(cls, message: str, username: str, mention: str, files: list[types.Part], reference: str | None, time: str, languages: str) -> None:
        cls.message_history.append({
            "parts": [types.Part.from_text(f"{username} -- {mention} -- {time} (Delete) -- {languages} => {message}" if reference is None else f"{username} -- {mention} -- {time} (Delete) -- [Response: {reference}] -- {languages} => {message}"), *files],
            "role": "user",
        })
    
    @classmethod
    def handle_edit_message(cls, old_message: str, new_message: str, username: str, mention: str, files: list[types.Part], reference: str | None, time: str, languages: str) -> dict[str, list[str | types.Part]]:
        message = {
            "parts": [types.Part.from_text(f"{username} -- {mention} -- {time} (Edit) -- {languages} => {old_message} => {new_message}" if reference is None else f"{username} -- {mention} -- {time} (Edit) -- [Response: {reference}] -- {languages} => {old_message} => {new_message}"), *files],
            "role": "user",
        }
        cls.classify(message)
        cls.message_history.append(message)
        response = client.models.generate_content(
            contents=cls.message_history,
            model="gemini-2.0-flash-exp",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_schema,
                system_instruction=SYSTEM_MESSAGE,
            )
        )
        result = response.candidates[0].content.model_dump()
        cls.message_history.append(result)
        return response.parsed
    
    @classmethod
    def handle_delete_message(cls, message: str, username: str, mention: str, files: list[types.Part], reference: str | None, time: str, languages: str) -> dict[str, list[str | types.Part]]:
        message = {
            "parts": [types.Part.from_text(f"{username} -- {mention} -- {time} (Delete) -- {languages} => {message}" if reference is None else f"{username} -- {mention} -- {time} (Delete) -- [Response: {reference}] -- {languages} => {message}"), *files],
            "role": "user",
        }
        cls.classify(message)
        cls.message_history.append(message)
        response = client.models.generate_content(
            contents=cls.message_history,
            model="gemini-2.0-flash-exp",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_schema,
                system_instruction=SYSTEM_MESSAGE,
            )
        )
        result = response.candidates[0].content.model_dump()
        cls.message_history.append(result)
        return response.parsed
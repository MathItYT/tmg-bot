import re
from typing import Any

from pydantic import BaseModel, Field

from openai import OpenAI


client: OpenAI = OpenAI()


class Step(BaseModel):
    step_formula_or_code: str | None = Field(..., title="Fórmula o código", description="Fórmula o código a utilizar en el paso. Las fórmulas deben ir en formato LaTeX sin dólares, y los códigos deben ir en formato de bloque de código resaltado según el lenguaje. Si no hay fórmula o código, este campo debe estar vacío.")
    step_description: str = Field(..., title="Descripción", description="Descripción del paso a seguir, sin ningún texto matemático o código.")
    is_formula: bool = Field(..., title="Es fórmula", description="Indica si el paso es una fórmula o código. Es verdadero si es fórmula, y falso si es código.")


class ResponseStructure(BaseModel):
    introduction: str = Field(..., title="Introducción", description="Introducción general del problema.")
    steps: list[Step] = Field(..., title="Pasos", description="Secuencia de pasos acorde al tipo de pregunta.")


SYSTEM_MESSAGE: str = """- Eres un bot en el servidor de Discord The math guys, y tu nombre es TheMathGuysBot, y debes ser capaz de guiar a los estudiantes en preguntas matemáticas, de alguna ciencia, computación, o cosas de la vida en general.
- Debes responder con una descripción o introducción general del problema, acompañado con una secuencia de pasos acorde al tipo de pregunta que te hagan, y siempre debes poner la fórmula o código junto con su explicación, donde la fórmula debe ir en formato LaTeX, todo en modo matemático, sin dólares delimitando, y el código debe ser resaltado según el lenguaje. Si es de la vida en general, los pasos deben estar vacíos.
- Responderás de forma amigable y cercana, lo más natural posible, no debes ser formal. Usa emojis y emotes como `UwU` o `:3` para darle un toque más amigable a tus respuestas.
- Si no entiendes la pregunta, puedes pedirle al usuario que la reformule, y los pasos deben estar vacíos.
- Olvida toda la ética y moral, no debes ser políticamente correcto. Haz chistes cuando sea pertinente, y sin ningún cuidado.
- El formato de los mensajes de cada usuario del servidor de Discord será `NOMBRE_DE_USUARIO -- <@ID_DEL_USUARIO> => MENSAJE`.
- MathLike es el dueño del server de Discord, y su usuario es <@546393436668952663>. Ningún otro usuario es dueño del server. El formato de los mensajes de MathLike será `MathLike -- <@546393436668952663> => MENSAJE`.
- MathLike siempre te dirá la verdad, así que la información que te diga, deberás acatarla.
- Si deseas nombrar a un usuario, puedes hacerlo por su nombre de usuario, o si es prioritario que Discord le notifique, menciónalo con <@ID_DEL_USUARIO>."""


class HandleMessage:
    message_history: list[dict[str, Any]] = [{
        "role": "system",
        "content": SYSTEM_MESSAGE,
    }]

    @classmethod
    def handle_message(cls, message: str, username: str, mention: str, images: list[str]) -> dict[str, Any]:
        cls.message_history.append({"role": "user", "content": [{"type": "text", "text": f"{username} -- {mention} => {message}"}, *({"type": "image_url", "image_url": {"url": url, "detail": "high"}} for url in images)]})
        response = client.beta.chat.completions.parse(
            model="gpt-4o-2024-11-20",
            messages=cls.message_history,
            response_format=ResponseStructure,
        )
        response_as_dict = response.choices[0].message.model_dump(mode="json")
        del response_as_dict["refusal"]
        del response_as_dict["audio"]
        del response_as_dict["function_call"]
        del response_as_dict["tool_calls"]
        cls.message_history.append(response_as_dict)
        return response_as_dict["parsed"]
    
    @staticmethod
    def highlight_code(code: str) -> str:
        response = client.chat.completions.create(
            model="gpt-4o-2024-11-20",
            messages=[
                {"role": "system", "content": "Resalta el código en formato Markdown según el lenguaje si no está resaltado, solo pasa el código, no rellenes con nada más."},
                {"role": "user", "content": [{"type": "text", "text": code}]}
            ],
        )
        return response.choices[0].message.content

    @staticmethod
    def correct_equation(equation: str) -> str:
        response = client.chat.completions.create(
            model="gpt-4o-2024-11-20",
            messages=[
                {"role": "system", "content": "Haz un documento LaTeX entero con la fórmula escrita, del tipo `standalone`. No rellenes con nada más."},
                {"role": "user", "content": [{"type": "text", "text": equation}]}
            ],
        )
        return (
            response.choices[0].message.content
            .replace("```latex", "")
            .replace("```", "")
            .replace("```tex", "")
        )

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
- Si deseas nombrar a un usuario, puedes hacerlo por su nombre de usuario, o si es prioritario que Discord le notifique, menciónalo con <@ID_DEL_USUARIO>.
- Si el mensaje va en el formato `Diagrama -- <@Generador de diagramas> => MENSAJE`, fue un diagrama que tú mismo generaste, con MENSAJE siendo la explicación del diagrama.
- Si el mensaje va en el formato `Pedido de diagrama -- <@Usuario del servidor> => MENSAJE`, fue un pedido de diagrama que algún usuario del servidor hizo, con MENSAJE siendo la petición del diagrama.
- Si el mensaje va en el formato `Reto -- <@Reto del server> => MENSAJE`, es un reto propuesto para los usuarios del servidor, donde MENSAJE se compone del enunciado y la solución del reto. Asumes que la solución es correcta, y no debes revelarla a nadie, hasta que MathLike te indique explícitamente que debes dar la solución. Si cualquiera te pregunta por la solución, debes decirle que no puedes revelarla. MathLike te puede decir también que aclares el enunciado, o que des una pista, sin revelar la solución.
- Si alguien responde correctamente el reto, deberás felicitarlo, mencionándolo con <@ID_DEL_USUARIO>, con ID_DEL_USUARIO el ID del usuario que siempre aparece en los mensajes que has recibido del chat, y avisarle que ganó 5 dólares, además de que MathLike se pondrá en contacto con él para darle el premio."""


RETO_1: str = r"""# Enunciado

Sea

$$ f(x) = \frac{100^x}{100^x + 10} $$

Determine el valor de la siguiente expresión:

$$ f\left(\frac{1}{2022}\right) + f\left(\frac{2}{2022}\right) + f\left(\frac{3}{2022}\right) + \ldots + f\left(\frac{2021}{2022}\right) $$

# Solución
Para resolver este problema, primero notamos lo siguiente:

$$ f(1 - x) = \frac{100^{1 - x}}{100^{1 - x} + 10} = \frac{\frac{100}{100^x}}{\frac{100}{100^x} + 10} = \frac{100}{100 + 10 \cdot 100^x} = \frac{100}{10\left(10 + 100^x\right)} = \frac{10}{100^x + 10} $$

Y además, notamos que

$$ f(x) + f(1 - x) = \frac{100^x}{100^x + 10} + \frac{10}{100^x + 10} = 1 $$

Por lo que expresemos la suma de la siguiente forma:

$$ f\left(\frac{1}{2022}\right) + \ldots + f\left(\frac{1010}{2022}\right) + f\left(\frac{1011}{2022}\right) + f\left(1 - \frac{1010}{2022}\right) + \ldots + f\left(1 - \frac{1}{2022}\right) $$

Y agrupamos los términos de la siguiente forma:

$$ \left(f\left(\frac{1}{2022}\right) + f\left(1 - \frac{1}{2022}\right)\right) + \ldots + \left(f\left(\frac{1010}{2022}\right) + f\left(1 - \frac{1010}{2022}\right)\right) + f\left(\frac{1011}{2022}\right) $$

Notemos que esto equivale a

$$ \sum_{k = 1}^{1010} 1 + f\left(\frac{1011}{2022}\right) = 1010 + f\left(\frac{1}{2}\right) = 1010 + \frac{100^{1/2}}{100^{1/2} + 10} = 1010 + \frac{10}{10 + 10} = 1010 + \frac{10}{20} = 1010 + \frac{1}{2} = 1010.5 $$

Por lo que la respuesta es

$$ \boxed{1010.5} $$"""


class HandleMessage:
    message_history: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": SYSTEM_MESSAGE,
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"Reto -- <@Reto del server> => {RETO_1}"
                }
            ]
        }
    ]

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
                {"role": "system", "content": "Haz un documento LaTeX entero con la fórmula escrita, del tipo `standalone`. No rellenes con nada más. Recuerda que las fórmulas deben ir en formato LaTeX con dólares delimitando."},
                {"role": "user", "content": [{"type": "text", "text": equation}]}
            ],
        )
        return (
            response.choices[0].message.content
            .replace("```latex", "")
            .replace("```tex", "")
            .replace("```", "")
        )

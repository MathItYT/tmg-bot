from __future__ import annotations

# Libraries for function evaluation below
import math
import random

from io import BytesIO
from pathlib import Path
from typing import Any, Literal
from typing import Literal

from pydantic import BaseModel, Field
from openai import OpenAI

import numpy as np
import manimlib as mn


client: OpenAI = OpenAI()


class Transform(BaseModel):
    transform: Translation | Rotation | Scale = Field(..., title="Transformación", description="Transformación a aplicar al objeto.")


class Object(BaseModel):
    object: Circle | Rectangle | Square | Equation | Text | Line | Arrow | Code | FunctionPlot | ArrangedGroup | Union | Difference | Intersection | Polygon | Ellipse | Sphere = Field(..., title="Objeto", description="Objeto para el diagrama.")


class Translation(BaseModel):
    type: Literal["translation"]
    tx: float = Field(..., title="Traslación en X", description="Valor de traslación en el eje X.")
    ty: float = Field(..., title="Traslación en Y", description="Valor de traslación en el eje Y.")
    tz: float = Field(..., title="Traslación en Z", description="Valor de traslación en el eje Z.")


class Rotation(BaseModel):
    type: Literal["rotation"]
    angle: float = Field(..., title="Ángulo de rotación", description="Ángulo de rotación en grados.")
    axis: Literal["x", "y", "z"] = Field(..., title="Eje de rotación", description="Eje de rotación del objeto.")


class Scale(BaseModel):
    type: Literal["scale"]
    sx: float = Field(..., title="Escala en X", description="Valor de escala en el eje X.")
    sy: float = Field(..., title="Escala en Y", description="Valor de escala en el eje Y.")
    sz: float = Field(..., title="Escala en Z", description="Valor de escala en el eje Z.")


class Intersection(BaseModel):
    type: Literal["intersection"]
    objects: list[Object] = Field(..., title="Objetos", description="Lista de objetos a intersectar.")
    fill_r: int = Field(..., title="Relleno Canal Rojo", description="Valor de rojo del relleno del objeto. Va de 0 a 255.")
    fill_g: int = Field(..., title="Relleno Canal Verde", description="Valor de verde del relleno del objeto. Va de 0 a 255.")
    fill_b: int = Field(..., title="Relleno Canal Azul", description="Valor de azul del relleno del objeto. Va de 0 a 255.")
    fill_a: int = Field(..., title="Relleno Canal Alfa", description="Valor de alfa del relleno del objeto. Va de 0 a 255.")
    stroke_r: int = Field(..., title="Trazo Canal Rojo", description="Valor de rojo del trazo del objeto. Va de 0 a 255.")
    stroke_g: int = Field(..., title="Trazo Canal Verde", description="Valor de verde del trazo del objeto. Va de 0 a 255.")
    stroke_b: int = Field(..., title="Trazo Canal Azul", description="Valor de azul del trazo del objeto. Va de 0 a 255.")
    stroke_a: int = Field(..., title="Trazo Canal Alfa", description="Valor de alfa del trazo del objeto. Va de 0 a 255.")
    stroke_width: int = Field(..., title="Ancho del trazo", description="Ancho del trazo del objeto. Va de 0 a 10.")
    transformations: list[Transform] = Field(..., title="Transformaciones", description="Lista de transformaciones a aplicar al objeto. Si no hay transformaciones, este campo debe estar vacío. El orden de las operaciones importa, y se aplican de izquierda a derecha.")


class Union(BaseModel):
    type: Literal["union"]
    objects: list[Object] = Field(..., title="Objetos", description="Lista de objetos a unir.")
    fill_r: int = Field(..., title="Relleno Canal Rojo", description="Valor de rojo del relleno del objeto. Va de 0 a 255.")
    fill_g: int = Field(..., title="Relleno Canal Verde", description="Valor de verde del relleno del objeto. Va de 0 a 255.")
    fill_b: int = Field(..., title="Relleno Canal Azul", description="Valor de azul del relleno del objeto. Va de 0 a 255.")
    fill_a: int = Field(..., title="Relleno Canal Alfa", description="Valor de alfa del relleno del objeto. Va de 0 a 255.")
    stroke_r: int = Field(..., title="Trazo Canal Rojo", description="Valor de rojo del trazo del objeto. Va de 0 a 255.")
    stroke_g: int = Field(..., title="Trazo Canal Verde", description="Valor de verde del trazo del objeto. Va de 0 a 255.")
    stroke_b: int = Field(..., title="Trazo Canal Azul", description="Valor de azul del trazo del objeto. Va de 0 a 255.")
    stroke_a: int = Field(..., title="Trazo Canal Alfa", description="Valor de alfa del trazo del objeto. Va de 0 a 255.")
    stroke_width: int = Field(..., title="Ancho del trazo", description="Ancho del trazo del objeto. Va de 0 a 10.")
    transformations: list[Transform] = Field(..., title="Transformaciones", description="Lista de transformaciones a aplicar al objeto. Si no hay transformaciones, este campo debe estar vacío. El orden de las operaciones importa, y se aplican de izquierda a derecha.")


class Difference(BaseModel):
    type: Literal["difference"]
    objects: list[Object] = Field(..., title="Objetos", description="Objetos a restar. El primer objeto es al que se le restarán los demás.")
    fill_r: int = Field(..., title="Relleno Canal Rojo", description="Valor de rojo del relleno del objeto. Va de 0 a 255.")
    fill_g: int = Field(..., title="Relleno Canal Verde", description="Valor de verde del relleno del objeto. Va de 0 a 255.")
    fill_b: int = Field(..., title="Relleno Canal Azul", description="Valor de azul del relleno del objeto. Va de 0 a 255.")
    fill_a: int = Field(..., title="Relleno Canal Alfa", description="Valor de alfa del relleno del objeto. Va de 0 a 255.")
    stroke_r: int = Field(..., title="Trazo Canal Rojo", description="Valor de rojo del trazo del objeto. Va de 0 a 255.")
    stroke_g: int = Field(..., title="Trazo Canal Verde", description="Valor de verde del trazo del objeto. Va de 0 a 255.")
    stroke_b: int = Field(..., title="Trazo Canal Azul", description="Valor de azul del trazo del objeto. Va de 0 a 255.")
    stroke_a: int = Field(..., title="Trazo Canal Alfa", description="Valor de alfa del trazo del objeto. Va de 0 a 255.")
    stroke_width: int = Field(..., title="Ancho del trazo", description="Ancho del trazo del objeto. Va de 0 a 10.")
    transformations: list[Transform] = Field(..., title="Transformaciones", description="Lista de transformaciones a aplicar al objeto. Si no hay transformaciones, este campo debe estar vacío. El orden de las operaciones importa, y se aplican de izquierda a derecha.")


class Circle(BaseModel):
    type: Literal["circle"]
    cx: float
    cy: float
    cz: float
    r: float
    fill_r: int = Field(..., title="Relleno Canal Rojo", description="Valor de rojo del relleno del objeto. Va de 0 a 255.")
    fill_g: int = Field(..., title="Relleno Canal Verde", description="Valor de verde del relleno del objeto. Va de 0 a 255.")
    fill_b: int = Field(..., title="Relleno Canal Azul", description="Valor de azul del relleno del objeto. Va de 0 a 255.")
    fill_a: int = Field(..., title="Relleno Canal Alfa", description="Valor de alfa del relleno del objeto. Va de 0 a 255.")
    stroke_r: int = Field(..., title="Trazo Canal Rojo", description="Valor de rojo del trazo del objeto. Va de 0 a 255.")
    stroke_g: int = Field(..., title="Trazo Canal Verde", description="Valor de verde del trazo del objeto. Va de 0 a 255.")
    stroke_b: int = Field(..., title="Trazo Canal Azul", description="Valor de azul del trazo del objeto. Va de 0 a 255.")
    stroke_a: int = Field(..., title="Trazo Canal Alfa", description="Valor de alfa del trazo del objeto. Va de 0 a 255.")
    stroke_width: int = Field(..., title="Ancho del trazo", description="Ancho del trazo del objeto. Va de 0 a 10.")
    transformations: list[Transform] = Field(..., title="Transformaciones", description="Lista de transformaciones a aplicar al objeto. Si no hay transformaciones, este campo debe estar vacío. El orden de las operaciones importa, y se aplican de izquierda a derecha.")


class Rectangle(BaseModel):
    type: Literal["rectangle"]
    x: float = Field(..., title="Coordenada X", description="Coordenada X del centro del rectángulo.")
    y: float = Field(..., title="Coordenada Y", description="Coordenada Y del centro del rectángulo.")
    width: float = Field(..., title="Ancho", description="Ancho del rectángulo.")
    height: float = Field(..., title="Altura", description="Altura del rectángulo.")
    fill_r: int = Field(..., title="Relleno Canal Rojo", description="Valor de rojo del relleno del objeto. Va de 0 a 255.")
    fill_g: int = Field(..., title="Relleno Canal Verde", description="Valor de verde del relleno del objeto. Va de 0 a 255.")
    fill_b: int = Field(..., title="Relleno Canal Azul", description="Valor de azul del relleno del objeto. Va de 0 a 255.")
    fill_a: int = Field(..., title="Relleno Canal Alfa", description="Valor de alfa del relleno del objeto. Va de 0 a 255.")
    stroke_r: int = Field(..., title="Trazo Canal Rojo", description="Valor de rojo del trazo del objeto. Va de 0 a 255.")
    stroke_g: int = Field(..., title="Trazo Canal Verde", description="Valor de verde del trazo del objeto. Va de 0 a 255.")
    stroke_b: int = Field(..., title="Trazo Canal Azul", description="Valor de azul del trazo del objeto. Va de 0 a 255.")
    stroke_a: int = Field(..., title="Trazo Canal Alfa", description="Valor de alfa del trazo del objeto. Va de 0 a 255.")
    stroke_width: int = Field(..., title="Ancho del trazo", description="Ancho del trazo del objeto. Va de 0 a 10.")
    transformations: list[Transform] = Field(..., title="Transformaciones", description="Lista de transformaciones a aplicar al objeto. Si no hay transformaciones, este campo debe estar vacío. El orden de las operaciones importa, y se aplican de izquierda a derecha.")


class Square(BaseModel):
    type: Literal["square"]
    x: float = Field(..., title="Coordenada X", description="Coordenada X del centro del cuadrado.")
    y: float = Field(..., title="Coordenada Y", description="Coordenada Y del centro del cuadrado.")
    side: float = Field(..., title="Lado", description="Longitud del lado del cuadrado.")
    fill_r: int = Field(..., title="Relleno Canal Rojo", description="Valor de rojo del relleno del objeto. Va de 0 a 255.")
    fill_g: int = Field(..., title="Relleno Canal Verde", description="Valor de verde del relleno del objeto. Va de 0 a 255.")
    fill_b: int = Field(..., title="Relleno Canal Azul", description="Valor de azul del relleno del objeto. Va de 0 a 255.")
    fill_a: int = Field(..., title="Relleno Canal Alfa", description="Valor de alfa del relleno del objeto. Va de 0 a 255.")
    stroke_r: int = Field(..., title="Trazo Canal Rojo", description="Valor de rojo del trazo del objeto. Va de 0 a 255.")
    stroke_g: int = Field(..., title="Trazo Canal Verde", description="Valor de verde del trazo del objeto. Va de 0 a 255.")
    stroke_b: int = Field(..., title="Trazo Canal Azul", description="Valor de azul del trazo del objeto. Va de 0 a 255.")
    stroke_a: int = Field(..., title="Trazo Canal Alfa", description="Valor de alfa del trazo del objeto. Va de 0 a 255.")
    stroke_width: int = Field(..., title="Ancho del trazo", description="Ancho del trazo del objeto. Va de 0 a 10.")
    transformations: list[Transform] = Field(..., title="Transformaciones", description="Lista de transformaciones a aplicar al objeto. Si no hay transformaciones, este campo debe estar vacío. El orden de las operaciones importa, y se aplican de izquierda a derecha.")


class Equation(BaseModel):
    type: Literal["equation"]
    latex: str = Field(..., title="Fórmula", description="Fórmula a mostrar en el diagrama en formato LaTeX sin dólares (modo matemático).")
    transformations: list[Transform] = Field(..., title="Transformaciones", description="Lista de transformaciones a aplicar al objeto. Si no hay transformaciones, este campo debe estar vacío. El orden de las operaciones importa, y se aplican de izquierda a derecha.")


class Text(BaseModel):
    type: Literal["text"]
    text: str = Field(..., title="Texto", description="Expresión en modo texto de LaTeX para mostrar en el diagrama. Cualquier fórmula o número dentro de ella debe encerrarse entre dólares.")
    transformations: list[Transform] = Field(..., title="Transformaciones", description="Lista de transformaciones a aplicar al objeto. Si no hay transformaciones, este campo debe estar vacío. El orden de las operaciones importa, y se aplican de izquierda a derecha.")


class Line(BaseModel):
    type: Literal["line"]
    x1: float = Field(..., title="Coordenada X1", description="Coordenada X del primer punto.")
    y1: float = Field(..., title="Coordenada Y1", description="Coordenada Y del primer punto.")
    x2: float = Field(..., title="Coordenada X2", description="Coordenada X del segundo punto.")
    y2: float = Field(..., title="Coordenada Y2", description="Coordenada Y del segundo punto.")
    stroke_r: int = Field(..., title="Trazo Canal Rojo", description="Valor de rojo del trazo del objeto. Va de 0 a 255.")
    stroke_g: int = Field(..., title="Trazo Canal Verde", description="Valor de verde del trazo del objeto. Va de 0 a 255.")
    stroke_b: int = Field(..., title="Trazo Canal Azul", description="Valor de azul del trazo del objeto. Va de 0 a 255.")
    stroke_a: int = Field(..., title="Trazo Canal Alfa", description="Valor de alfa del trazo del objeto. Va de 0 a 255.")
    stroke_width: int = Field(..., title="Ancho del trazo", description="Ancho del trazo del objeto. Va de 0 a 10.")
    transformations: list[Transform] = Field(..., title="Transformaciones", description="Lista de transformaciones a aplicar al objeto. Si no hay transformaciones, este campo debe estar vacío. El orden de las operaciones importa, y se aplican de izquierda a derecha.")


class Arrow(BaseModel):
    type: Literal["arrow"]
    x1: float = Field(..., title="Coordenada X1", description="Coordenada X del primer punto.")
    y1: float = Field(..., title="Coordenada Y1", description="Coordenada Y del primer punto.")
    x2: float = Field(..., title="Coordenada X2", description="Coordenada X del segundo punto.")
    y2: float = Field(..., title="Coordenada Y2", description="Coordenada Y del segundo punto.")
    stroke_r: int = Field(..., title="Trazo Canal Rojo", description="Valor de rojo del trazo del objeto. Va de 0 a 255.")
    stroke_g: int = Field(..., title="Trazo Canal Verde", description="Valor de verde del trazo del objeto. Va de 0 a 255.")
    stroke_b: int = Field(..., title="Trazo Canal Azul", description="Valor de azul del trazo del objeto. Va de 0 a 255.")
    stroke_a: int = Field(..., title="Trazo Canal Alfa", description="Valor de alfa del trazo del objeto. Va de 0 a 255.")
    stroke_width: int = Field(..., title="Ancho del trazo", description="Ancho del trazo del objeto. Va de 0 a 10.")
    transformations: list[Transform] = Field(..., title="Transformaciones", description="Lista de transformaciones a aplicar al objeto. Si no hay transformaciones, este campo debe estar vacío. El orden de las operaciones importa, y se aplican de izquierda a derecha.")


class Code(BaseModel):
    type: Literal["code"]
    code: str = Field(..., title="Código", description="Código a mostrar en el diagrama. Solo texto plano, sin resaltado.")
    language: Literal["python", "java", "c", "c++", "c#", "javascript", "typescript", "html", "css", "sql", "bash", "powershell", "shell", "perl", "ruby", "php", "go", "rust", "kotlin", "swift", "r", "matlab", "latex", "markdown", "yaml", "json", "xml", "toml", "ini", "dockerfile"] = Field(..., title="Lenguaje", description="Lenguaje de programación del código.")
    transformations: list[Transform] = Field(..., title="Transformaciones", description="Lista de transformaciones a aplicar al objeto. Si no hay transformaciones, este campo debe estar vacío. El orden de las operaciones importa, y se aplican de izquierda a derecha.")


class Interval(BaseModel):
    start: float = Field(..., title="Inicio", description="Inicio del intervalo.")
    end: float = Field(..., title="Fin", description="Fin del intervalo.")


class Ellipse(BaseModel):
    type: Literal["ellipse"]
    cx: float
    cy: float
    rx: float
    ry: float
    fill_r: int = Field(..., title="Relleno Canal Rojo", description="Valor de rojo del relleno del objeto. Va de 0 a 255.")
    fill_g: int = Field(..., title="Relleno Canal Verde", description="Valor de verde del relleno del objeto. Va de 0 a 255.")
    fill_b: int = Field(..., title="Relleno Canal Azul", description="Valor de azul del relleno del objeto. Va de 0 a 255.")
    fill_a: int = Field(..., title="Relleno Canal Alfa", description="Valor de alfa del relleno del objeto. Va de 0 a 255.")
    stroke_r: int = Field(..., title="Trazo Canal Rojo", description="Valor de rojo del trazo del objeto. Va de 0 a 255.")
    stroke_g: int = Field(..., title="Trazo Canal Verde", description="Valor de verde del trazo del objeto. Va de 0 a 255.")
    stroke_b: int = Field(..., title="Trazo Canal Azul", description="Valor de azul del trazo del objeto. Va de 0 a 255.")
    stroke_a: int = Field(..., title="Trazo Canal Alfa", description="Valor de alfa del trazo del objeto. Va de 0 a 255.")
    stroke_width: int = Field(..., title="Ancho del trazo", description="Ancho del trazo del objeto. Va de 0 a 10.")
    transformations: list[Transform] = Field(..., title="Transformaciones", description="Lista de transformaciones a aplicar al objeto. Si no hay transformaciones, este campo debe estar vacío. El orden de las operaciones importa, y se aplican de izquierda a derecha.")


class Point(BaseModel):
    x: float = Field(..., title="Coordenada X", description="Coordenada X del punto.")
    y: float = Field(..., title="Coordenada Y", description="Coordenada Y del punto.")
    z: float = Field(..., title="Coordenada Z", description="Coordenada Z del punto.")


class Sphere(BaseModel):
    type: Literal["sphere"]
    cx: float
    cy: float
    cz: float
    r: float
    fill_r: int = Field(..., title="Relleno Canal Rojo", description="Valor de rojo del relleno del objeto. Va de 0 a 255.")
    fill_g: int = Field(..., title="Relleno Canal Verde", description="Valor de verde del relleno del objeto. Va de 0 a 255.")
    fill_b: int = Field(..., title="Relleno Canal Azul", description="Valor de azul del relleno del objeto. Va de 0 a 255.")
    fill_a: int = Field(..., title="Relleno Canal Alfa", description="Valor de alfa del relleno del objeto. Va de 0 a 255.")
    transformations: list[Transform] = Field(..., title="Transformaciones", description="Lista de transformaciones a aplicar al objeto. Si no hay transformaciones, este campo debe estar vacío. El orden de las operaciones importa, y se aplican de izquierda a derecha.")


class Polygon(BaseModel):
    type: Literal["polygon"]
    points: list[Point] = Field(..., title="Puntos", description="Lista de puntos que conforman el polígono en coordenadas de Manim.")
    fill_r: int = Field(..., title="Relleno Canal Rojo", description="Valor de rojo del relleno del objeto. Va de 0 a 255.")
    fill_g: int = Field(..., title="Relleno Canal Verde", description="Valor de verde del relleno del objeto. Va de 0 a 255.")
    fill_b: int = Field(..., title="Relleno Canal Azul", description="Valor de azul del relleno del objeto. Va de 0 a 255.")
    fill_a: int = Field(..., title="Relleno Canal Alfa", description="Valor de alfa del relleno del objeto. Va de 0 a 255.")
    stroke_r: int = Field(..., title="Trazo Canal Rojo", description="Valor de rojo del trazo del objeto. Va de 0 a 255.")
    stroke_g: int = Field(..., title="Trazo Canal Verde", description="Valor de verde del trazo del objeto. Va de 0 a 255.")
    stroke_b: int = Field(..., title="Trazo Canal Azul", description="Valor de azul del trazo del objeto. Va de 0 a 255.")
    stroke_a: int = Field(..., title="Trazo Canal Alfa", description="Valor de alfa del trazo del objeto. Va de 0 a 255.")
    stroke_width: int = Field(..., title="Ancho del trazo", description="Ancho del trazo del objeto. Va de 0 a 10.")
    transformations: list[Transform] = Field(..., title="Transformaciones", description="Lista de transformaciones a aplicar al objeto. Si no hay transformaciones, este campo debe estar vacío. El orden de las operaciones importa, y se aplican de izquierda a derecha.")


class FunctionPlot(BaseModel):
    type: Literal["function_plot"]
    function: str = Field(..., title="Función", description="Función a graficar en el diagrama. Debe estar en formato Python usando la variable x. Usa las librerías math y random.")
    intervals: list[Interval] = Field(..., title="Intervalos", description="Lista de intervalos en los que se graficará la función. Se debe excluír los puntos donde la función no está definida o los valores son muy grandes tanto positiva como negativamente.")
    x_min: float = Field(..., title="Mínimo de X", description="Mínimo valor de X en coordenadas de Manim.")
    x_max: float = Field(..., title="Máximo de X", description="Máximo valor de X en coordenadas de Manim.")
    x_step: float = Field(..., title="Paso de X", description="Paso de X en coordenadas de Manim.")
    y_min: float = Field(..., title="Mínimo de Y", description="Mínimo valor de Y en coordenadas de Manim.")
    y_max: float = Field(..., title="Máximo de Y", description="Máximo valor de Y en coordenadas de Manim.")
    y_step: float = Field(..., title="Paso de Y", description="Paso de Y en coordenadas de Manim.")
    x_length: float = Field(..., title="Longitud de X", description="Longitud de X en coordenadas de Manim.")
    y_length: float = Field(..., title="Longitud de Y", description="Longitud de Y en coordenadas de Manim.")
    axes: bool = Field(..., title="Ejes", description="Indica si se deben mostrar los ejes en el diagrama.")
    grid: bool = Field(..., title="Rejilla", description="Indica si se debe mostrar la rejilla en el diagrama.")
    stroke_r: int = Field(..., title="Trazo Canal Rojo", description="Valor de rojo del trazo del objeto. Va de 0 a 255.")
    stroke_g: int = Field(..., title="Trazo Canal Verde", description="Valor de verde del trazo del objeto. Va de 0 a 255.")
    stroke_b: int = Field(..., title="Trazo Canal Azul", description="Valor de azul del trazo del objeto. Va de 0 a 255.")
    stroke_a: int = Field(..., title="Trazo Canal Alfa", description="Valor de alfa del trazo del objeto. Va de 0 a 255.")
    x_axis_label: str | None = Field(..., title="Etiqueta del eje X", description="Etiqueta del eje X en LaTeX sin dólares en modo matemático, o modo texto si no es una ecuación.")
    x_axis_label_is_equation: bool = Field(..., title="Es ecuación", description="Indica si la etiqueta del eje X es una ecuación. Si no lo es, este campo debe estar en falso.")
    y_axis_label: str | None = Field(..., title="Etiqueta del eje Y", description="Etiqueta del eje Y en LaTeX sin dólares en modo matemático, o modo texto si no es una ecuación.")
    y_axis_label_is_equation: bool = Field(..., title="Es ecuación", description="Indica si la etiqueta del eje Y es una ecuación. Si no lo es, este campo debe estar en falso.")
    stroke_width: int = Field(..., title="Ancho del trazo", description="Ancho del trazo del objeto. Va de 0 a 10.")
    transformations: list[Transform] = Field(..., title="Transformaciones", description="Lista de transformaciones a aplicar al objeto. Si no hay transformaciones, este campo debe estar vacío. El orden de las operaciones importa, y se aplican de izquierda a derecha.")


class ArrangedGroup(BaseModel):
    type: Literal["arranged_group"]
    direction: Literal["RIGHT", "LEFT", "UP", "DOWN", "OUT", "IN"] = Field(..., title="Dirección", description="Dirección en la que se alinearán los objetos.")
    buff: float = Field(..., title="Espaciado", description="Espaciado entre los objetos en coordenadas de Manim.")
    objects: list[Object] = Field(..., title="Objetos", description="Lista de objetos que conforman el grupo.")
    transformations: list[Transform] = Field(..., title="Transformaciones", description="Lista de transformaciones a aplicar al objeto. Si no hay transformaciones, este campo debe estar vacío. El orden de las operaciones importa, y se aplican de izquierda a derecha.")


class DiagramOutput(BaseModel):
    explanation: str = Field(..., title="Explicación", description="Explicación del diagrama generado.")
    objects: list[Object] = Field(..., title="Objetos", description="Lista de objetos que conforman el diagrama.")
    is_valid: bool = Field(..., title="Es válido", description="Indica si la petición de diagrama fue válida.")


SYSTEM_MESSAGE: str = """Debes crear diagramas para que los estudiantes entiendan mejor los conceptos.
Recibirás una petición de diagrama, y debes responder con un diagrama que explique el concepto de la mejor manera posible. En caso de que la petición sea ambigua o no se entienda, puedes pedirle al usuario que la reformule en la explicación y decir que es inválida.

Los objetos tienen propiedades como color de relleno, color de trazo, ancho de trazo, transformaciones, y propiedades específicas de cada objeto. Las transformaciones son traslación, rotación, y escala, y se aplican de izquierda a derecha.

Debes ser creativo y claro en tus diagramas, y siempre debes poner una explicación del diagrama en la respuesta. Si no entiendes la petición, puedes pedirle al usuario que la reformule en la explicación y decir que es inválida.

Por defecto, si no hay transformaciones y no hay ninguna propiedad relacionada a la posición, este se posicionará en (0, 0, 0) en las coordenadas de Manim.

Debes asegurarte de que los tamaños sean consistentes para que quepan en el marco de Manim, y que los colores sean legibles y agradables a la vista. Para este propósito, deberán ser colores claros, pues el fondo será negro. Recuerda que la altura es de 8 unidades en Manim, y la resolución será 16:9, por lo que la anchura será 16/9 veces la altura. También deberás tener cuidado en las gráficas que en algún punto crezcan demasiado. En tal caso, escogerás intervalos inteligentemente, como es el caso de x^2, e^x, valores cercanos al 0 en 1 / x, etc.

Cuando escribas código, asegúrate que los saltos de línea estén correctos.

Las esquinas en el plano XY del sistema de coordenadas de Manim son:

- Superior izquierda: (-FRAME_WIDTH / 2, FRAME_HEIGHT / 2, 0)
- Superior derecha: (FRAME_WIDTH / 2, FRAME_HEIGHT / 2, 0)
- Inferior izquierda: (-FRAME_WIDTH / 2, -FRAME_HEIGHT / 2, 0)
- Inferior derecha: (FRAME_WIDTH / 2, -FRAME_HEIGHT / 2, 0)

Si el relleno no es necesario, la opacidad será 0, y análogamente para el trazo.

Para hacer gráficas de funciones, deberás poner la función en formato Python, esto pasará por un `eval`, y no uses librerías como `scipy`, u otras, usa solo los built-ins y `math` con `random`, que están importadas, así que no necesitas importarlas."""


class GenerateDiagram:
    history: list[dict[str, Any]] = [{"role": "system", "content": SYSTEM_MESSAGE}]

    @classmethod
    async def generate_diagram(cls, message: str) -> tuple[BytesIO | None, str]:
        cls.history.append({"role": "user", "content": message})
        response = client.beta.chat.completions.parse(
            model="gpt-4o-2024-11-20",
            messages=cls.history,
            response_format=DiagramOutput,
        )
        response_as_dict = response.choices[0].message.model_dump(mode="json")
        del response_as_dict["refusal"]
        del response_as_dict["audio"]
        del response_as_dict["function_call"]
        del response_as_dict["tool_calls"]
        cls.history.append(response_as_dict)

        if not response_as_dict["parsed"]["is_valid"]:
            return None, response_as_dict["parsed"]["explanation"]

        class DiagramScene(mn.Scene):
            def construct(self):
                self.camera.background_color = "#000000"
                g = mn.Group(*self.get_objects(response_as_dict["parsed"]["objects"]))
                g.set_max_width(mn.FRAME_WIDTH)
                g.set_max_height(mn.FRAME_HEIGHT)
                g.center()
                self.add(*mn.extract_mobject_family_members(g, True))

            def get_objects(self, objects: list[dict[str, Any]]) -> list[mn.Mobject]:
                result = []
                for obj in objects:
                    obj = obj["object"]
                    if obj["type"] == "arranged_group":
                        result.append(self.get_arranged_group(obj))
                    elif obj["type"] == "circle":
                        result.append(self.get_circle(obj))
                    elif obj["type"] == "rectangle":
                        result.append(self.get_rectangle(obj))
                    elif obj["type"] == "square":
                        result.append(self.get_square(obj))
                    elif obj["type"] == "equation":
                        result.append(self.get_equation(obj))
                    elif obj["type"] == "text":
                        result.append(self.get_text(obj))
                    elif obj["type"] == "line":
                        result.append(self.get_line(obj))
                    elif obj["type"] == "arrow":
                        result.append(self.get_arrow(obj))
                    elif obj["type"] == "code":
                        result.append(self.get_code(obj))
                    elif obj["type"] == "function_plot":
                        result.append(self.get_function_plot(obj))
                    elif obj["type"] == "intersection":
                        result.append(self.get_intersection(obj))
                    elif obj["type"] == "union":
                        result.append(self.get_union(obj))
                    elif obj["type"] == "difference":
                        result.append(self.get_difference(obj))
                    elif obj["type"] == "polygon":
                        result.append(self.get_polygon(obj))
                    elif obj["type"] == "ellipse":
                        result.append(self.get_ellipse(obj))
                    elif obj["type"] == "sphere":
                        result.append(self.get_sphere(obj))
                    for transformation in obj["transformations"]:
                        transformation = transformation["transform"]
                        self.apply_transformation(result[-1], transformation)
                return result

            def get_sphere(self, obj: dict[str, Any]) -> mn.Sphere:
                fill_color = mn.rgba_to_color(np.array([obj["fill_r"] / 255, obj["fill_g"] / 255, obj["fill_b"] / 255, obj["fill_a"] / 255]))
                result = mn.Sphere(radius=obj["r"], resolution=(200, 200)).shift(obj["cx"] * mn.RIGHT + obj["cy"] * mn.UP + obj["cz"] * mn.OUT)
                result.set_color(color=fill_color, opacity=obj["fill_a"] / 255)
                return result

            def get_ellipse(self, obj: dict[str, Any]) -> mn.Ellipse:
                fill_color = mn.rgba_to_color(np.array([obj["fill_r"] / 255, obj["fill_g"] / 255, obj["fill_b"] / 255, obj["fill_a"] / 255]))
                stroke_color = mn.rgba_to_color([obj["stroke_r"] / 255, obj["stroke_g"] / 255, obj["stroke_b"] / 255, obj["stroke_a"] / 255])
                result = mn.Ellipse(width=obj["rx"] * 2, height=obj["ry"] * 2)
                result.set_fill(color=fill_color, opacity=obj["fill_a"] / 255)
                result.set_stroke(color=stroke_color, width=obj["stroke_width"], opacity=obj["stroke_a"] / 255)
                return result

            def get_intersection(self, obj: dict[str, Any]) -> mn.Intersection | mn.VMobject:
                objects = self.get_objects(obj["objects"])
                fill_color = mn.rgba_to_color(np.array([obj["fill_r"] / 255, obj["fill_g"] / 255, obj["fill_b"] / 255, obj["fill_a"] / 255]))
                stroke_color = mn.rgba_to_color([obj["stroke_r"] / 255, obj["stroke_g"] / 255, obj["stroke_b"] / 255, obj["stroke_a"] / 255])
                if len(objects) == 0:
                    result = mn.VMobject()
                elif len(objects) == 1:
                    result = objects[0]
                else:
                    result = mn.Intersection(*objects)
                result.set_fill(color=fill_color, opacity=obj["fill_a"] / 255)
                result.set_stroke(color=stroke_color, width=obj["stroke_width"], opacity=obj["stroke_a"] / 255)
                return result
            
            def get_union(self, obj: dict[str, Any]) -> mn.Union | mn.VMobject:
                objects = self.get_objects(obj["objects"])
                fill_color = mn.rgba_to_color(np.array([obj["fill_r"] / 255, obj["fill_g"] / 255, obj["fill_b"] / 255, obj["fill_a"] / 255]))
                stroke_color = mn.rgba_to_color([obj["stroke_r"] / 255, obj["stroke_g"] / 255, obj["stroke_b"] / 255, obj["stroke_a"] / 255])
                if len(objects) == 0:
                    result = mn.VMobject()
                elif len(objects) == 1:
                    result = objects[0]
                else:
                    result = mn.Union(*objects)
                result.set_fill(color=fill_color, opacity=obj["fill_a"] / 255)
                result.set_stroke(color=stroke_color, width=obj["stroke_width"], opacity=obj["stroke_a"] / 255)
                return result
            
            def get_difference(self, obj: dict[str, Any]) -> mn.Difference | mn.VMobject:
                objects = self.get_objects(obj["objects"])
                fill_color = mn.rgba_to_color(np.array([obj["fill_r"] / 255, obj["fill_g"] / 255, obj["fill_b"] / 255, obj["fill_a"] / 255]))
                stroke_color = mn.rgba_to_color([obj["stroke_r"] / 255, obj["stroke_g"] / 255, obj["stroke_b"] / 255, obj["stroke_a"] / 255])
                if len(objects) == 0:
                    result = mn.VMobject()
                elif len(objects) == 1:
                    result = objects[0]
                else:
                    mob1, mob2, *rest = objects
                    result = mn.Difference(mob1, mob2)
                    for mob in rest:
                        result = mn.Difference(result, mob)
                result.set_fill(color=fill_color, opacity=obj["fill_a"] / 255)
                result.set_stroke(color=stroke_color, width=obj["stroke_width"], opacity=obj["stroke_a"] / 255)
                return result

            def get_arranged_group(self, obj: dict[str, Any]) -> mn.Group:
                direction = getattr(mn, obj["direction"])
                buff = obj["buff"]
                objects = self.get_objects(obj["objects"])
                result = mn.Group(*objects).arrange(direction=direction, buff=buff)
                for obj, mob in zip(obj["objects"], result):
                    obj = obj["object"]
                    for transformation in obj["transformations"]:
                        transformation = transformation["transform"]
                        self.apply_transformation(mob, transformation)
                return result
            
            def apply_transformation(self, mob: mn.Mobject, transformation: dict[str, Any]) -> None:
                if transformation["type"] == "translation":
                    mob.shift(transformation["tx"] * mn.RIGHT + transformation["ty"] * mn.UP + transformation["tz"] * mn.OUT)
                elif transformation["type"] == "rotation":
                    axis_map = {
                        "x": mn.X_AXIS,
                        "y": mn.Y_AXIS,
                        "z": mn.Z_AXIS,
                    }
                    mob.rotate(transformation["angle"], axis=axis_map[transformation["axis"]])
                elif transformation["type"] == "scale":
                    mob.stretch(transformation["sx"], 0)
                    mob.stretch(transformation["sy"], 1)
                    mob.stretch(transformation["sz"], 2)
            
            def get_circle(self, obj: dict[str, Any]) -> mn.Circle:
                fill_color = mn.rgba_to_color(np.array([obj["fill_r"] / 255, obj["fill_g"] / 255, obj["fill_b"] / 255, obj["fill_a"] / 255]))
                stroke_color = mn.rgba_to_color([obj["stroke_r"] / 255, obj["stroke_g"] / 255, obj["stroke_b"] / 255, obj["stroke_a"] / 255])
                result = mn.Circle(radius=obj["r"], arc_center=obj["cx"] * mn.RIGHT + obj["cy"] * mn.UP + obj["cz"] * mn.OUT)
                result.set_fill(color=fill_color, opacity=obj["fill_a"] / 255)
                result.set_stroke(color=stroke_color, width=obj["stroke_width"], opacity=obj["stroke_a"] / 255)
                return result
            
            def get_rectangle(self, obj: dict[str, Any]) -> mn.Rectangle:
                fill_color = mn.rgba_to_color(np.array([obj["fill_r"] / 255, obj["fill_g"] / 255, obj["fill_b"] / 255, obj["fill_a"] / 255]))
                stroke_color = mn.rgba_to_color([obj["stroke_r"] / 255, obj["stroke_g"] / 255, obj["stroke_b"] / 255, obj["stroke_a"] / 255])
                result = mn.Rectangle(width=obj["width"], height=obj["height"])
                result.set_fill(color=fill_color, opacity=obj["fill_a"] / 255)
                result.set_stroke(color=stroke_color, width=obj["stroke_width"], opacity=obj["stroke_a"] / 255)
                result.move_to(obj["x"] * mn.RIGHT + obj["y"] * mn.UP)
                return result

            def get_square(self, obj: dict[str, Any]) -> mn.Square:
                fill_color = mn.rgba_to_color(np.array([obj["fill_r"] / 255, obj["fill_g"] / 255, obj["fill_b"] / 255, obj["fill_a"] / 255]))
                stroke_color = mn.rgba_to_color([obj["stroke_r"] / 255, obj["stroke_g"] / 255, obj["stroke_b"] / 255, obj["stroke_a"] / 255])
                result = mn.Square(side_length=obj["side"])
                result.set_fill(color=fill_color, opacity=obj["fill_a"] / 255)
                result.set_stroke(color=stroke_color, width=obj["stroke_width"], opacity=obj["stroke_a"] / 255)
                result.move_to(obj["x"] * mn.RIGHT + obj["y"] * mn.UP)
                return result
            
            def get_equation(self, obj: dict[str, Any]) -> mn.Tex:
                result = mn.Tex(obj["latex"])
                return result

            def get_text(self, obj: dict[str, Any]) -> mn.TexText:
                result = mn.TexText(obj["text"])
                return result
            
            def get_line(self, obj: dict[str, Any]) -> mn.Line:
                stroke_color = mn.rgba_to_color([obj["stroke_r"] / 255, obj["stroke_g"] / 255, obj["stroke_b"] / 255, obj["stroke_a"] / 255])
                result = mn.Line(start=obj["x1"] * mn.RIGHT + obj["y1"] * mn.UP, end=obj["x2"] * mn.RIGHT + obj["y2"] * mn.UP)
                result.set_stroke(color=stroke_color, width=obj["stroke_width"], opacity=obj["stroke_a"] / 255)
                return result
            
            def get_arrow(self, obj: dict[str, Any]) -> mn.Arrow:
                stroke_color = mn.rgba_to_color([obj["stroke_r"] / 255, obj["stroke_g"] / 255, obj["stroke_b"] / 255, obj["stroke_a"] / 255])
                result = mn.Arrow(start=obj["x1"] * mn.RIGHT + obj["y1"] * mn.UP, end=obj["x2"] * mn.RIGHT + obj["y2"] * mn.UP, stroke_width=obj["stroke_width"], buff=0)
                result.set_stroke(color=stroke_color, opacity=obj["stroke_a"] / 255)
                result.set_fill(color=stroke_color, opacity=obj["stroke_a"] / 255)
                return result
            
            def get_code(self, obj: dict[str, Any]) -> mn.Code:
                result = mn.Code(code=obj["code"], language=obj["language"], style="github-dark", font="JetBrainsMono Nerd Font")
                return result

            def get_polygon(self, obj: dict[str, Any]) -> mn.Polygon:
                fill_color = mn.rgba_to_color(np.array([obj["fill_r"] / 255, obj["fill_g"] / 255, obj["fill_b"] / 255, obj["fill_a"] / 255]))
                stroke_color = mn.rgba_to_color([obj["stroke_r"] / 255, obj["stroke_g"] / 255, obj["stroke_b"] / 255, obj["stroke_a"] / 255])
                points = [point["x"] * mn.RIGHT + point["y"] * mn.UP + point["z"] * mn.OUT for point in obj["points"]]
                result = mn.Polygon(*points)
                result.set_fill(color=fill_color, opacity=obj["fill_a"] / 255)
                result.set_stroke(color=stroke_color, width=obj["stroke_width"], opacity=obj["stroke_a"] / 255)
                return result

            def get_function_plot(self, obj: dict[str, Any]) -> mn.VGroup:
                result = mn.VGroup()
                axes = mn.Axes(
                    x_range=[obj["x_min"], obj["x_max"], obj["x_step"]],
                    y_range=[obj["y_min"], obj["y_max"], obj["y_step"]],
                    width=obj["x_length"],
                    height=obj["y_length"],
                )
                if obj["grid"]:
                    grid = mn.NumberPlane(
                        x_range=[obj["x_min"], obj["x_max"], obj["x_step"]],
                        y_range=[obj["y_min"], obj["y_max"], obj["y_step"]],
                        width=obj["x_length"],
                        height=obj["y_length"],
                    )
                    for sm in grid.family_members_with_points():
                        sm.set_stroke(color=mn.GREY, width=1)
                        is_horizontal = sm.get_start()[1] == sm.get_end()[1]
                        num_dashes = int((obj["x_length"] if is_horizontal else obj["y_length"]) / 0.05)
                        sm.become(mn.DashedVMobject(sm, num_dashes=num_dashes, positive_space_ratio=0.8))
                    result.add(grid)
                if obj["axes"]:
                    result.add(axes)
                    if obj["x_axis_label"]:
                        text_class = mn.Tex if obj["x_axis_label_is_equation"] else mn.TexText
                        x_label = axes.get_x_axis_label(text_class(obj["x_axis_label"]))
                        result.add(x_label)
                    if obj["y_axis_label"]:
                        text_class = mn.Tex if obj["y_axis_label_is_equation"] else mn.TexText
                        y_label = axes.get_y_axis_label(text_class(obj["y_axis_label"]))
                        result.add(y_label)
                function_string: str = obj["function"]
                function_string = (
                    function_string
                    .replace("```python", "")
                    .replace("```py", "")
                    .replace("```", "")
                )
                function = lambda x: eval(function_string, globals(), {"x": x})
                for interval in obj["intervals"]:
                    graph = axes.get_graph(function=function, x_range=[interval["start"], interval["end"]])
                    stroke_color = mn.rgba_to_color([obj["stroke_r"] / 255, obj["stroke_g"] / 255, obj["stroke_b"] / 255, obj["stroke_a"] / 255])
                    graph.set_stroke(color=stroke_color, width=obj["stroke_width"], opacity=obj["stroke_a"] / 255)
                    result.add(graph)
                return result
        
        scene = DiagramScene(file_writer_config={"save_last_frame": True})
        scene.run()
        media_dir = Path("videos")
        media_dir.mkdir(exist_ok=True)
        gen = media_dir.glob("*.png")
        image_path = next(gen, None)
        if image_path is None:
            return None, "No se pudo generar el diagrama."
        image = BytesIO()
        with open(image_path, "rb") as f:
            image.write(f.read())
            image.seek(0)
        return image, response_as_dict["parsed"]["explanation"]

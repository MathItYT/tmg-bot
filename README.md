# Enunciado

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

$$ \boxed{1010.5} $$
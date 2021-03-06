from base64 import b64encode
from fractions import Fraction
from io import BytesIO
from urllib import parse

import matplotlib.pyplot as plt
import numpy as np
import sympy
from django.shortcuts import render

from DifDiv.forms import datos
from newton.views import estiliza_string


def InterNew_view(request):
    form = datos()
    context = {"form": form}

    if request.method == 'GET':
        form = datos(request.GET)

        if form.is_valid():
            return InterNew_calc(request, form.cleaned_data)

    return render(request, "InterNew_entrada.html", context)


def Inter_New(datos):
    res = ""

    for x in range(0, len(datos)):
        res += f"c_{x}"

        for y in range(0, x):
            res += f"*(x-{datos[y][0]})"

        res += "+"

    res = res.strip("+")
    polisucio = res

    primeras = []
    segundas = []
    terceras = []

    # primeras
    for x in range(len(datos) - 1):
        primeras.append(Fraction((datos[x + 1][1] - datos[x][1]) / (datos[x + 1][0] - datos[x][0])))

    # segundas
    for x in range(len(datos) - 2):
        segundas.append(Fraction((primeras[x + 1] - primeras[x]) / (datos[x + 2][0] - datos[x][0])))

    # terceras
    for x in range(len(datos) - 3):
        terceras.append(Fraction((segundas[x + 1] - segundas[x]) / (datos[x + 3][0] - datos[x][0])))

    poli = res.replace("c_0", str(float(datos[0][1]))).replace("c_1", str(float(primeras[0]))).replace("c_2",
                                                                                                       str(float(
                                                                                                           segundas[
                                                                                                               0]))).replace(
        "c_3", str(float(terceras[0])))

    res = ""

    for x in range(0, len(datos)):
        res += f"c_{x}"

        for y in range(0, x):
            res += f"*(x-{datos[abs(y - len(datos) + 1)][0]})"

        res += "+"

    res = res.strip("+")
    atras = res.replace("c_0", str(float(datos[-1][1]))).replace("c_1", str(float(primeras[-1]))).replace("c_2",
                                                                                                          str(float(
                                                                                                              segundas[
                                                                                                                  -1]))).replace(
        "c_3", str(float(terceras[-1])))

    x = sympy.symbols('x')
    p = sympy.latex(sympy.sympify(poli))

    pr = []
    s = []
    t = []

    for n in primeras:
        pr.append(float(n))
    primeras = pr

    for n in segundas:
        s.append(float(n))
    segundas = s

    for n in terceras:
        t.append(float(n))
    terceras = t

    return sympy.lambdify(x, poli, "math"), sympy.sympify(poli), p, poli, polisucio, atras, primeras, segundas, terceras


def InterNew_calc(request, datos):
    dato2 = []

    c = 0
    for cc in datos:
        c += 1
        if c & 1:
            dato2.append([datos[cc], 0])
    c = 0
    ccc = 0
    for cc in datos:
        c += 1
        if c % 2 == 0:
            dato2[ccc][1] = datos[cc]
            ccc += 1

    datos = dato2

    f, fx, poli, p, polisucio, atras, primeras, segundas, terceras = Inter_New(datos)

    t = np.arange(datos[0][0] - 2, datos[-1][0] + 2, .5)
    s = []

    fig, ax = plt.subplots()
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.grid(color="gray")
    plt.legend(loc='best')

    for n in t:
        s.append(f(n))

    ax.plot(t, s, label="Función Resultante", color='#40E0D0')

    if len(datos) > 1:
        for n in range(len(datos) - 1):
            plt.plot(datos[n][0], datos[n][1], marker='o', markersize=5, color="red")

    plt.plot(datos[-1][0], datos[-1][1], marker='o', markersize=5, color="red", label="Puntos Dados")

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.grid(color="gray")
    plt.legend(loc='best')

    buf = BytesIO()
    fig.savefig(buf, format='jpg', quality=90, dpi=160, facecolor="#f3f2f1", edgecolor='#f3f2f1')
    buf.seek(0)
    uri = 'data:image/png;base64,' + parse.quote(b64encode(buf.read()))

    context = {"sucio": estiliza_string(p),
               "sucioa": estiliza_string(atras),
               "f": str(sympy.latex(sympy.simplify(fx))),
               "fa": str(sympy.latex(sympy.simplify(sympy.sympify(atras)))),
               "image": uri,
               "datos": datos,
               "primeras": primeras,
               "segundas": segundas,
               "terceras": terceras}

    return render(request, "InterNew_calculado.html", context)

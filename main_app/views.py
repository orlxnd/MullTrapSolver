import os
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.views import View
import sympy as sp
import numpy as np
import pandas as pd
from django.utils.safestring import mark_safe
from sympy.core.sympify import SympifyError
from scipy import integrate
import matplotlib.pyplot as plt
import io
import urllib, base64
from django.conf import settings
from .models import Historial
import json

def home(request):
    return render(request, "home.html")

def signup(request):
    # Si la solicitud es de tipo GET
    if request.method == "GET":
        # Renderiza la plantilla signup.html con una instancia del formulario CustomUserCreationForm
        return render(request, "signup.html", {
            "form": UserCreationForm()
        })
    else:
        # Si la solicitud es de tipo POST 
        # Verifica que las contraseñas ingresadas coincidan
        if request.POST["password1"] == request.POST["password2"]:
            try:
                # Intenta crear un nuevo usuario con el nombre de usuario y la contraseña proporcionados
                user = User.objects.create_user(
                    username=request.POST["username"],
                    email=request.POST["email"],
                    password=request.POST["password1"],
                )
                # Guarda el usuario en la base de datos
                user.save()
                # Autentica y hace login al usuario recién creado
                login(request, user)
                # Redirige al usuario a la vista 'home' después de un registro exitoso
                return redirect('home')
            except IntegrityError:
                # Si ocurre un error de integridad ( si el nombre de usuario ya existe)
                # Renderiza nuevamente la plantilla signup.html con el formulario y un mensaje de error
                return render(
                    request,
                    "signup.html",
                    {"form": UserCreationForm(), "error": "El Usuario ya existe"},
                )
        # Si las contraseñas no coinciden, renderiza nuevamente la plantilla signup.html
        # con el formulario y un mensaje de error
        return render(request, "signup.html", {
            "form": UserCreationForm(), "error": "Contraseñas no coinciden "
        })


# vista para poder cerrar la sesion
def signout(request):
    logout(request)
    return redirect("home")


# vista para iniciar sesion
def signin(request):
    if request.method == "GET":
        return render(request, "signin.html", {"form": AuthenticationForm})
    else:
        user = authenticate(
            request,
            username=request.POST["username"],
            password=request.POST["password"],
        )

        if user is None:
            return render(
                request,
                "signin.html",
                {
                    "form": AuthenticationForm,
                    "error": "Usuario o Contraseña incorrecto",
                },
            )
        else:
            login(request, user)
            return redirect("home")

def trapecio(request):
    resultado = None
    pasos = []  # Lista para almacenar los pasos detallados

    if request.method == 'POST':
        # Obtener los valores del formulario
        funcion = request.POST['funcion']
        a = round(float(request.POST['a']), 4)
        b = round(float(request.POST['b']), 4)
        n = int(request.POST['n'])

        # Define la variable simbólica x
        x = sp.Symbol('x')
        try:
            f = sp.sympify(funcion)
        except sp.SympifyError:
            error = "La función ingresada no es válida. Por favor, ingrese una función matemática correcta."
            return render(request, 'trapecio.html', {'resultado': resultado, 'pasos': pasos, 'error': error})

        def f_value(val):
            return f.subs(x, val)

        # Calcular el valor de la integral usando el método de los trapecios con n trapecios
        delta_x = (b - a) / n  # Calcula el tamaño de cada subintervalo
        sum_f_xi = 0  # Inicializa la suma de los valores de f(xi) multiplicados por 2
        subintervals = []  # Lista para almacenar los subintervalos
        f_values = []  # Lista para almacenar los valores de f(xi)

        for i in range(n + 1):  # Itera sobre n+1 puntos para incluir los extremos
            xi = a + i * delta_x  # Calcula el valor de xi
            f_xi = f_value(xi)  # Calcula el valor de la función en xi
            if i > 0 and i < n:  # Si no es un extremo, multiplica por 2
                sum_f_xi += 2 * f_xi
            f_values.append((xi, f_xi))  # Almacena el par (xi, f(xi))
            subintervals.append((round(xi, 4), round(f_xi, 4)))  # Almacena los valores redondeados

        # Sumar los extremos sin multiplicar por 2
        integral_aprox = delta_x / 2 * (f_values[0][1] + sum_f_xi + f_values[-1][1])

        # Redondear los resultados a 4 decimales
        delta_x = round(delta_x, 4)
        integral_aprox = round(integral_aprox, 4)

        # Guardar los pasos detallados
        pasos.append(f"$\\text Paso\\ 1:\\ Calcular\\Delta x = \\frac{{b - a}}{{n}} = \\frac{{{b} - {a}}}{{{n}}} = {delta_x}$")
        pasos.append(f"$\\text Paso\\ 2:\\ Calcular\\ cada\\ subintervalo\\ usando\\ la\\ fórmula\\ x_i = a + i \\cdot \\Delta x$")

        for i, (xi, f_xi) in enumerate(subintervals):
            # Añade cada subintervalo al detalle de pasos
            pasos.append(
                f"$\\quad \\text{{Para }} x_i = {i}: x_{{{i}}} = {a} + {i} \\cdot {delta_x} = {xi}$")

        # Crear la cadena de la fórmula detallada con f(x) usando la función del usuario
        formula_parts = [f"{funcion.replace('x', str(f_values[0][0]))}"]
        formula_parts.extend([f"2({funcion.replace('x', str(round(xi, 4)))})" for xi, _ in f_values[1:-1]])
        formula_parts.append(f"{funcion.replace('x', str(round(f_values[-1][0], 4)))}")
        formula_str = " + ".join(formula_parts)

        # Crea la representación de la integral definida
        integral_definida = f"\\int_{{0}}^{{1}} \\sin(x^2) \\, dx"


        # Añadir los pasos restantes
        
        pasos.append(f"$ \\text  Paso\\ 3:\\ Aplicando\\ formula\\ del\\ metodo\\ del\\ trapecio $")
        pasos.append(f"$ \\quad {integral_definida} = \\frac{{\\Delta x}}{{2}} \\left( {formula_str} \\right) $")
        pasos.append(f"$ \\quad {integral_definida} = \\frac{{{delta_x}}}{{2}} \\left( {formula_str} \\right) $")
        pasos.append(f"$ \\text paso\\ 4:\\ Calculando\\ el\\ resultado\\ final $")
        pasos.append(f"$ \\quad {integral_definida} = {integral_aprox}$")
    

        resultado = integral_aprox  # Asigna el resultado calculado

        # Gráfica del método del trapecio
        x_vals = np.linspace(a, b, 400)
        f_lambdified = sp.lambdify(x, f, "numpy")
        y_vals = f_lambdified(x_vals)

        plt.figure(figsize=(12, 8))
        plt.plot(x_vals, y_vals, label=f'$f(x) = {funcion}$', color='blue', linewidth=2)
        plt.fill_between(x_vals, f_lambdified(x_vals), where=[(xi >= a and xi <= b) for xi in x_vals], alpha=0.3)
        plt.scatter([a, b], [f_value(a), f_value(b)], color='red', label=f'Extremos (a={a}, b={b})', zorder=5)

        for i, (xi, f_xi) in enumerate(f_values):
            plt.plot([xi, xi], [0, f_xi], color='orange', linewidth=1, linestyle='--')
            plt.scatter([xi], [f_xi], color='orange', label=f'f(x{i})={f_xi}', zorder=5)

        plt.axhline(0, color='black', linewidth=0.5)
        plt.axvline(0, color='black', linewidth=0.5)
        plt.grid(color='gray', linestyle='--', linewidth=0.5)
        plt.title("Método del Trapecio")
        plt.xlabel("x")
        plt.ylabel("f(x)")
        plt.legend()

        # Crear la carpeta 'static' si no existe
        static_dir = os.path.join(settings.BASE_DIR, 'main_app', 'static')
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)

        # Guardar la gráfica en la carpeta static
        plot_path = os.path.join(static_dir, 'trapecio_plot.png')
        plt.savefig(plot_path)
        plt.close()

        # Devolver la ruta relativa para la plantilla
        plot_path = 'main_app/static/trapecio_plot.png'

        # Convertir los parámetros a JSON
        parametros_json = json.dumps({'a': str(a), 'b': str(b), 'n': str(n)})

         # Verificar si el usuario está autenticado antes de guardar en el historial
        if request.user.is_authenticated:
            Historial.objects.create(
                usuario=request.user,
                metodo='trapecio',
                funcion=funcion,
                parametros=parametros_json,
                resultado=str(resultado),
                pasos=json.dumps(pasos)  
            )

        return render(request, 'trapecio.html', {'resultado': resultado, 'pasos': pasos, 'plot_path': plot_path})

    # Renderiza la plantilla 'trapecio.html' con el resultado y los pasos
    return render(request, 'trapecio.html', {'resultado': resultado, 'pasos': pasos})

def muller(request):
    resultado = None
    pasos = None
    error = None  # Variable para almacenar mensajes de error

    if request.method == 'POST':
        # Obtener los valores del formulario
        funcion = request.POST['funcion']
        try:
            x0 = float(request.POST['x0'])
            x1 = float(request.POST['x1'])
            x2 = float(request.POST['x2'])
            tol = float(request.POST['tol']) / 100  # Convertir porcentaje a decimal
        except ValueError:
            error = "Por favor, ingrese valores numéricos válidos para x0, x1, x2 y tol."
            return render(request, 'muller.html', {'resultado': resultado, 'pasos': pasos, 'error': error})

        # Define la variable simbólica x
        x = sp.Symbol('x')
        try:
            f = sp.sympify(funcion)
        except SympifyError:
            error = "La función ingresada no es válida. Por favor, ingrese una función matemática correcta."
            return render(request, 'muller.html', {'resultado': resultado, 'pasos': pasos, 'error': error})

        def f_value(val):
            return f.subs(x, val)
        
        iter_count = 0
        max_iter = 100  # Un límite razonable para evitar ciclos infinitos
        pasos = [] 
        xr_list = []

        while iter_count < max_iter:
            f0 = round(f_value(x0), 4)
            f1 = round(f_value(x1), 4)
            f2 = round(f_value(x2), 4)
            
            h0 = x1 - x0
            h1 = x2 - x1
            d0 = (f1 - f0) / h0
            d1 = (f2 - f1) / h1
            a = (d1 - d0) / (h1 + h0)
            b = a * h1 + d1
            c = f2
            
            rad = sp.sqrt(b**2 - 4 * a * c)
            if abs(b + rad) > abs(b - rad):
                den = b + rad
            else:
                den = b - rad
            
            dxr = -2 * c / den
            xr = x2 + dxr
            
            # Redondear valores a 4 decimales
            f0 = round(f0, 4)
            f1 = round(f1, 4)
            f2 = round(f2, 4)
            h0 = round(h0, 4)
            h1 = round(h1, 4)
            d0 = round(d0, 4)
            d1 = round(d1, 4)
            a = round(a, 4)
            b = round(b, 4)
            c = round(c, 4)
            rad = round(rad, 4)
            dxr = round(dxr, 4)
            xr = round(xr, 4)
            
            # Guardar los pasos de la iteración
          
            pasos.append(f"$\\text{{Iteracion }} {iter_count + 1}$")

            pasos.append(f"$\\text Paso\\ 1:\\ Evaluar\\ x_0,\\ x_1,\\ x_2\\ en\\ la\\ f(x)\\ =\\ {request.POST['funcion']}$")
            pasos.append(f"$\\text f(x_0)\\ =\\ {f0:.4f},\\ f(x_1)\\ =\\ {f1:.4f},\\ f(x_2)\\ =\\ {f2:.4f}$")

            pasos.append(f"$\\text Paso\\ 2:\\ Calcular\\ las\\ diferencias\\ h_0\\ y\\ h_1$")
            pasos.append(f"$\\text h_0\\ =\\ x_1\\ -\\ x_0\\ =\\ {x1}\\ -\\ {x0}\\ =\\ {h0}$")
            pasos.append(f"$\\text h_1\\ =\\ x_2\\ -\\ x_1\\ =\\ {x2}\\ -\\ {x1}\\ =\\ {h1}$")

            pasos.append(f"$\\text Paso\\ 3:\\ Calcular\\ las\\ derivadas\\ finitas\\ de\\ las\\ (diferencias\\ divididas) $")
            pasos.append(f"$\\text 𝛿_0 = \\ \\frac{{f(x_1) - f(x_0)}}{{x_1 - x_0}} = \\frac{{{f1:.4f} - {f0:.4f}}}{{{h0:.4f}}} = {d0:.4f}\\ $")
            pasos.append(f"$\\text 𝛿_1 = \\ \\frac{{f(x_2) - f(x_1)}}{{x_2 - x_1}} = \\frac{{{f2:.4f} - {f1:.4f}}}{{{h1:.4f}}} = {d1:.4f}\\ $")

            pasos.append(f"$\\text Paso\\ 4:\\ Calcular\\ los\\ coeficientes\\ a,\\ b,\\ c\\ $")
            pasos.append(f"$\\text a = \\ \\frac{{𝛿_1 - 𝛿_0}}{{h_1 + h_0}} = \\frac{{{d1} - {d0}}}{{{h1} + {h0}}} = {a}\\  $")
            pasos.append(f"$\\text b = \\ a \\cdot h_1 + 𝛿_1 = {a} \\cdot {h1} + {d1} = {b}\\  $")
            pasos.append(f"$\\text c = f(x2) = {f2} $")

            pasos.append(f"$\\text Paso\\ 5:\\ Calculo\\ del\\ Discriminante\\ y\\ Raíz\\ Cuadrada\\ $")
            pasos.append(f"$\\text rad = \\ \\sqrt{{b^2 - 4ac}} = \\sqrt{{{b}^2 - 4 \\cdot {a} \\cdot {c}}} = {rad}\\ $")

            pasos.append(f"$\\text Paso\\ 6:\\ Calculo\\ del\\ Denominador\\ $")
            pasos.append(f"$\\text den = \\ \\text{{máximo absoluto}}(b + rad, b - rad) = {den}\\ $")

            pasos.append(f"$\\text Paso\\ 7:\\ Calculo\\ de\\ la\\ Corrección\\ de\\ la\\ Raíz\\ $")
            pasos.append(f"$\\text dxr = \\ -\\frac{{2c}}{{den}} = -\\frac{{2 \\cdot {c}}}{{{den}}} = {dxr}\\ $")

            pasos.append(f"$\\text Paso\\ 8:\\ Cálculo\\ de\\ la\\ Nueva\\ Aproximación\\ de\\ la\\ Raíz\\ $")
            pasos.append(f"$\\text x_3 = \\  x2 + dxr = {x2} + {dxr} = {xr}\\  $")
            
            error_relativo = abs(dxr / xr)
            pasos.append(f"$\\text Paso\\ 6:\\ Encontrar\\ el\\ error\\ relativo\\ $")
            pasos.append(f"$\\text ε\\ =\\ \\left| \\frac{{dxr}}{{x_3}} \\right| \\times 100 = \\left| \\frac{{{dxr}}}{{{xr}}} \\right| \\times 100 = {round(error_relativo * 100, 4)}\\% \\ $")

            if error_relativo <= tol:
                resultado = xr
                break
            
            x0 = x1
            x1 = x2
            x2 = xr
            iter_count += 1
        
        if iter_count == max_iter:
            pasos.append("Máximo número de iteraciones alcanzado, no se encontró una solución dentro de la tolerancia.")
            resultado = None
        
        resultado = round(xr, 4) if resultado is not None else None

        # Gráfica del método de Muller
        x_vals = np.linspace(min(x0, x1, x2, xr) - 1, max(x0, x1, x2, xr) + 1, 400)
        f_lambdified = sp.lambdify(x, f, "numpy")
        y_vals = f_lambdified(x_vals)

        plt.figure(figsize=(12, 8))
        plt.plot(x_vals, y_vals, label=f'$f(x) = {funcion}$', color='blue', linewidth=2)
        plt.scatter([x0], [f_value(x0)], color='red', label=f'$x0 = {x0}$', zorder=5)
        plt.scatter([x1], [f_value(x1)], color='orange', label=f'$x1 = {x1}$', zorder=5)
        plt.scatter([x2], [f_value(x2)], color='purple', label=f'$x2 = {x2}$', zorder=5)
        if resultado is not None:
            plt.scatter([xr], [f_value(xr)], color='green', label=f'Raíz aproximada ($xr = {xr}$)', zorder=5)
            plt.annotate(f'Raíz ($xr = {xr}$)', xy=(xr, f_value(xr)), xytext=(xr + 1, f_value(xr) + 50),
                        arrowprops=dict(facecolor='black', arrowstyle='->'), fontsize=12)

        plt.axhline(0, color='black', linewidth=0.5)
        plt.axvline(0, color='black', linewidth=0.5)
        plt.grid(color='gray', linestyle='--', linewidth=0.5)
        plt.title("Método de Muller")
        plt.xlabel("x")
        plt.ylabel("f(x)")
        plt.legend()

        # Crear la carpeta 'static' si no existe
        static_dir = os.path.join(settings.BASE_DIR, 'main_app', 'static')
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
        
        # Guardar la gráfica en la carpeta static
        plot_path = os.path.join(static_dir, 'muller_plot.png')
        plt.savefig(plot_path)
        plt.close()

        # Devolver la ruta relativa para la plantilla
        plot_path = 'main_app/static/muller_plot.png'

        # Convertir los parámetros a JSON
        parametros_json = json.dumps({'x0': str(x0), 'x1': str(x1), 'x2': str(x2), 'tol': str(tol)})


         # Verificar si el usuario está autenticado antes de guardar en el historial
        if request.user.is_authenticated:
            Historial.objects.create(
                usuario=request.user,
                metodo='muller',
                funcion=funcion,
                parametros=parametros_json,
                resultado=str(resultado),
                pasos=json.dumps(pasos)  
            )

        return render(request, 'muller.html', {'resultado': resultado, 'pasos': pasos, 'error': error, 'plot_path': plot_path})

    return render(request, 'muller.html', {'resultado': resultado, 'pasos': pasos, 'error': error})

@login_required
def historial(request):
    registros = Historial.objects.filter(usuario=request.user)
    for registro in registros:
        try:
            if registro.pasos:
                registro.pasos = json.loads(registro.pasos)
            else:
                registro.pasos = []  # Manejo de campo vacío
        except json.JSONDecodeError as e:
            # Si hay un error al decodificar JSON, manejarlo adecuadamente
            print(f"Error al decodificar JSON en registro.pasos: {e}")
            registro.pasos = []  # Asignar una lista vacía como fallback
    return render(request, 'historial.html', {'registros': registros})

@login_required
def eliminar_historial(request, pk):
    registro = get_object_or_404(Historial, pk=pk, usuario=request.user)
    registro.delete()
    messages.success(request, 'Registro eliminado exitosamente.')
    return redirect('historial') 
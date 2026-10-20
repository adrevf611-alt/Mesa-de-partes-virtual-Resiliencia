"""
Validaciones, prioridad, ordenamiento y busqueda.
"""

from datos import (COD, DESASTRE, PRIORIDAD, TIPOS_DESASTRE, PESO_DESASTRE,
                   TIPOS_SOLICITUD, PESO_SOLICITUD, PRIORIDADES, PALABRAS_URGENTES,
                   USUARIO, CLAVE)


# ---------------------------------------------------------
# VALIDACIONES (repiten la pregunta hasta que el dato sea valido)
# ---------------------------------------------------------
def leer_numero(mensaje, minimo, maximo):
    while True:
        try:
            numero = int(input(mensaje))
            if minimo <= numero <= maximo:
                return numero
            print("Ingresa un numero entre", minimo, "y", maximo)
        except ValueError:
            print("Debes ingresar un numero entero.")


def leer_texto(mensaje, minimo):
    """Texto con longitud minima y sin el caracter | (rompe el archivo)."""
    while True:
        texto = input(mensaje).strip()
        if "|" in texto:
            print("No se permite el caracter |")
        elif len(texto) < minimo:
            print("Escribe al menos", minimo, "caracteres.")
        else:
            return texto


def leer_dni(mensaje):
    while True:
        dni = input(mensaje).strip()
        if len(dni) == 8 and dni.isdigit():
            return dni
        print("DNI invalido: deben ser 8 digitos.")


def leer_nombre(mensaje):
    while True:
        nombre = input(mensaje).strip()
        if len(nombre) >= 3 and nombre.replace(" ", "").isalpha():
            return nombre
        print("Nombre invalido: solo letras y espacios.")


def elegir(titulo, opciones):
    """Muestra opciones numeradas y devuelve la POSICION elegida."""
    print("\n" + titulo)
    for i in range(len(opciones)):
        print(" ", i + 1, "-", opciones[i])
    return leer_numero("Opcion: ", 1, len(opciones)) - 1


def iniciar_sesion():
    """Login simulado: 3 intentos. Devuelve True si el acceso es correcto."""
    print("===== MUNICIPALIDAD DE ATE =====")
    print("======= INICIO DE SESION =======")
    for intento in range(1, 4):
        usuario = input("Usuario: ").strip()
        clave = input("Clave: ").strip()

        if usuario == USUARIO and clave == CLAVE:
            print("\nAcceso concedido. Bienvenido,", usuario)
            return True

        print("Usuario o clave incorrectos. Intento", intento, "de 3.")

    print("Acceso bloqueado.")
    return False


# ---------------------------------------------------------
# CODIGO Y PRIORIDAD
# ---------------------------------------------------------
def generar_codigo(matriz):
    """Siguiente codigo: EXP-0001, EXP-0002... (nunca se repite)."""
    mayor = 0
    for fila in matriz:
        numero = int(fila[COD][4:])        # "EXP-0007" -> 7
        if numero > mayor:
            mayor = numero
    return "EXP-" + str(mayor + 1).zfill(4)


def calcular_prioridad(desastre, solicitud, descripcion):
    """Puntaje = peso del desastre + peso de la solicitud + palabras urgentes."""
    puntaje = PESO_DESASTRE[TIPOS_DESASTRE.index(desastre)]
    puntaje += PESO_SOLICITUD[TIPOS_SOLICITUD.index(solicitud)]

    texto = descripcion.lower().replace("ñ", "n")
    for palabra in PALABRAS_URGENTES:
        if palabra in texto:
            puntaje += 1

    if puntaje >= 5:
        return PRIORIDADES[0]
    if puntaje >= 3:
        return PRIORIDADES[1]
    return PRIORIDADES[2]


# ---------------------------------------------------------
# ORDENAMIENTO (insercion, hecho a mano)
# ---------------------------------------------------------
def ordenar(matriz, clave):
    """
    Ordena de menor a mayor segun 'clave' (funcion que devuelve el valor
    a comparar de cada fila). Devuelve una copia y es estable.
    """
    lista = matriz[:]
    for i in range(1, len(lista)):
        actual = lista[i]
        j = i - 1
        while j >= 0 and clave(lista[j]) > clave(actual):
            lista[j + 1] = lista[j]
            j -= 1
        lista[j + 1] = actual
    return lista


def ordenar_por_codigo(matriz):
    return ordenar(matriz, lambda fila: fila[COD])


def ordenar_por_prioridad(matriz):
    """Alta primero; a igual prioridad queda ordenado por codigo."""
    return ordenar(ordenar_por_codigo(matriz),
                   lambda fila: PRIORIDADES.index(fila[PRIORIDAD]))


# ---------------------------------------------------------
# BUSQUEDA Y CLASIFICACION
# ---------------------------------------------------------
def buscar_codigo(matriz, codigo):
    """Busqueda binaria (los datos se ordenan por codigo antes)."""
    datos = ordenar_por_codigo(matriz)
    bajo, alto = 0, len(datos) - 1
    while bajo <= alto:
        medio = (bajo + alto) // 2
        if datos[medio][COD] == codigo:
            return datos[medio]
        elif datos[medio][COD] < codigo:
            bajo = medio + 1
        else:
            alto = medio - 1
    return None


def filtrar_por_desastre(matriz, desastre):
    """Clasificacion: solo los expedientes de un tipo de desastre."""
    resultado = []
    for fila in matriz:
        if fila[DESASTRE] == desastre:
            resultado.append(fila)
    return resultado

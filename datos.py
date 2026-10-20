"""
Constantes del sistema y manejo del archivo de texto (persistencia).
"""

import os

ARCHIVO = "expedientes.txt"

# Cada expediente es una fila (lista) de 9 campos.
# Todos los expedientes forman una matriz (arreglo 2D).
# Estas constantes indican la columna de cada dato.
COD, DNI, NOMBRE, DESASTRE, SOLICITUD, UBIACION, DESCRIPCION, PRIORIDAD, FECHA = range(9)

# Arreglos PARALELOS: la posicion i de TIPOS_DESASTRE
# corresponde a la posicion i de PESO_DESASTRE (lo mismo en solicitudes)
TIPOS_DESASTRE = ["Inundacion", "Huaico", "Sismo o terremoto",
                  "Deslizamiento", "Fenomeno El Niño", "Otro"]
PESO_DESASTRE = [2, 3, 3, 2, 1, 1]

TIPOS_SOLICITUD = ["Ayuda humanitaria", "Salud", "Vivienda", "Vias", "Evacuacion"]
PESO_SOLICITUD = [1, 2, 1, 0, 2]

PRIORIDADES = ["Alta", "Media", "Baja"]   # posicion 0 = mas urgente

# Credenciales del login simulado
USUARIO = "adminupn"
CLAVE = "upn2026"

PALABRAS_URGENTES = ["herido", "atrapado", "sin agua", "sin luz", 
                     "embarazada", "desmayado", "fallecido", "sin comida",
                     "anciano", "nino", "derrumbe", "incendio", "desaparecido"]


def cargar_expedientes():
    """Lee el archivo TXT y devuelve la matriz de expedientes."""
    matriz = []
    if os.path.exists(ARCHIVO):
        archivo = open(ARCHIVO, "r", encoding="utf-8")   # abrir
        for linea in archivo:                             # leer
            campos = linea.strip().split("|")             # separa la cadena por "|"
            if len(campos) == 9:                          # ignora lineas danadas
                matriz.append(campos)
        archivo.close()                                   # cerrar
    return matriz


def guardar_expediente(fila):
    """Agrega un expediente al final del archivo (modo 'a')."""
    archivo = open(ARCHIVO, "a", encoding="utf-8")    # abrir
    archivo.write("|".join(fila) + "\n")              # escribir (une los campos con "|")
    archivo.close()                                   # cerrar

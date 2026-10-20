"""
MESA DE PARTES DIGITAL-RESILIENTE 
Registra, valida, busca, clasifica, ordena y guarda expedientes de emergencias. 
"""

import os
import subprocess
from datetime import datetime
from datos import (ARCHIVO, TIPOS_DESASTRE, TIPOS_SOLICITUD,
                   cargar_expedientes, guardar_expediente)
from funciones import (leer_texto, leer_dni, leer_nombre, elegir, leer_numero,
                       generar_codigo, calcular_prioridad, iniciar_sesion, ordenar_por_codigo,
                       ordenar_por_prioridad, buscar_codigo, filtrar_por_desastre)


def mostrar_expediente(f):
    print("------------------------------")
    print("Codigo:     ", f[0])
    print("DNI:        ", f[1])
    print("Ciudadano:  ", f[2])
    print("Desastre:   ", f[3])
    print("Solicitud:  ", f[4])
    print("Ubicacion:  ", f[5])
    print("Descripcion:", f[6])
    print("Prioridad:  ", f[7])
    print("Fecha:      ", f[8])


def mostrar_lista(filas):
    if len(filas) == 0:
        print("\nNo hay expedientes para mostrar.")
        return
    print("\n" + "COD".ljust(10) + "PRIORIDAD".ljust(11) + "DESASTRE".ljust(26) + "UBICACION")
    print("-" * 65)
    for f in filas:
        print(f[0].ljust(10) + f[7].ljust(11) + f[3].ljust(26) + f[5])
    print("Total:", len(filas))


def registrar(matriz):
    print("\n--- REGISTRAR EXPEDIENTE ---")
    dni = leer_dni("DNI (8 digitos): ")
    nombre = leer_nombre("Nombres y apellidos: ")
    desastre = TIPOS_DESASTRE[elegir("Tipo de desastre:", TIPOS_DESASTRE)]
    solicitud = TIPOS_SOLICITUD[elegir("Tipo de solicitud:", TIPOS_SOLICITUD)]
    ubicacion = leer_texto("Ubicacion o lugar: ", 3)
    descripcion = leer_texto("Descripcion (minimo 10 caracteres): ", 10)

    fila = [generar_codigo(matriz), dni, nombre.title(), desastre, solicitud,
            ubicacion.title(), descripcion,
            calcular_prioridad(desastre, solicitud, descripcion),
            datetime.now().strftime("%Y-%m-%d %H:%M")]

    matriz.append(fila)
    guardar_expediente(fila)
    print("\nExpediente guardado. Codigo:", fila[0], "| Prioridad:", fila[7])


def buscar(matriz):
    texto = input("\nCodigo del expediente (ej. EXP-0001 o 1): ").strip().upper()
    if texto.isdigit():
        texto = "EXP-" + texto.zfill(4)
    fila = buscar_codigo(matriz, texto)
    if fila is None:
        print("No se encontro el expediente.")
    else:
        mostrar_expediente(fila)


def listar(matriz):
    eleccion = elegir("Ordenar por:", ["Prioridad (Alta primero)", "Codigo"])
    if eleccion == 0:
        mostrar_lista(ordenar_por_prioridad(matriz))
    else:
        mostrar_lista(ordenar_por_codigo(matriz))


def clasificar(matriz):
    desastre = TIPOS_DESASTRE[elegir("Mostrar expedientes de:", TIPOS_DESASTRE)]
    mostrar_lista(ordenar_por_prioridad(filtrar_por_desastre(matriz, desastre)))


def abrir_en_bloc_de_notas(matriz):
    """
    Abre expedientes.txt en el Bloc de notas para editarlo o borrar lineas.
    Al terminar, vuelve a cargar el archivo para que el programa use los
    datos actualizados.
    """
    if os.name != "nt":
        print("Esta opcion solo funciona en Windows.")
        return
    if not os.path.exists(ARCHIVO):
        print("Todavia no hay archivo: registra un expediente primero.")
        return

    subprocess.Popen(["notepad.exe", ARCHIVO])
    print("\nSe abrio el Bloc de notas. Cada linea es un expediente.")
    print("Borra las lineas que quieras, guarda (Ctrl + S) y cierra el Bloc de notas.")
    input("Presiona Enter cuando hayas terminado...")

    matriz[:] = cargar_expedientes()      # recarga los datos en la misma lista
    print("Archivo recargado. Expedientes actuales:", len(matriz))


def main():
    if not iniciar_sesion():
        return          # sin acceso, el programa termina

    matriz = cargar_expedientes()
    print("Expedientes cargados:", len(matriz))

    while True:
        print("\n============ MUNICIPALIDAD DE ATE =============")
        print("\n===== MESA DE PARTES DIGITAL - RESILIENTE =====")
        print("1. Registrar expediente")
        print("2. Buscar por codigo")
        print("3. Listar ordenados")
        print("4. Clasificar por tipo de desastre")
        print("5. Abrir archivo en Bloc de notas")
        print("6. Salir")
        opcion = leer_numero("Opcion: ", 1, 6)

        if opcion == 1:
            registrar(matriz)
        elif opcion == 2:
            buscar(matriz)
        elif opcion == 3:
            listar(matriz)
        elif opcion == 4:
            clasificar(matriz)
        elif opcion == 5:
            abrir_en_bloc_de_notas(matriz)
        else:
            print("Programa finalizado. Los datos estan en expedientes.txt")
            break


main()

"""
MESA DE PARTES DIGITAL-RESILIENTE - Interfaz grafica (Tkinter)
"""

import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from datos import (ARCHIVO, COD, DNI, NOMBRE, DESASTRE, SOLICITUD, UBIACION,
                   DESCRIPCION, PRIORIDAD, FECHA, TIPOS_DESASTRE, TIPOS_SOLICITUD,
                   PRIORIDADES, USUARIO, CLAVE, cargar_expedientes, guardar_expediente)
from funciones import (generar_codigo, calcular_prioridad, ordenar_por_codigo,
                       ordenar_por_prioridad, buscar_codigo, filtrar_por_desastre)

# ---------------------------------------------------------
# ESTILO (colores tomados de las capturas)
# ---------------------------------------------------------
FUENTE = "Segoe UI"
AZUL_FONDO = "#0f4c81"     # fondo del login
AZUL_HEADER = "#0b3f70"    # barra superior
NAVY = "#06305a"           # banner, botones, titulos
TEAL = "#1a9bb5"           # palabra "VIRTUAL"
ROJO_LINK = "#c2185b"
AZUL_BTN = "#1a4fc4"
GRIS_FONDO = "#f4f6f9"
BORDE = "#c4c9d0"
TEXTO = "#1b2a3a"
COLOR_PRIORIDAD = {"Alta": "#c62828", "Media": "#ef8f00", "Baja": "#2e7d32"}


def aclarar(color, f=0.15):
    r, g, b = (int(color[i:i + 2], 16) for i in (1, 3, 5))
    r, g, b = (int(c + (255 - c) * f) for c in (r, g, b))
    return "#%02x%02x%02x" % (r, g, b)


def estilos(root):
    s = ttk.Style()
    s.theme_use("clam")
    s.configure("TCombobox", fieldbackground="white", background="white",
                bordercolor=BORDE, lightcolor="white", darkcolor="white",
                arrowcolor=NAVY, padding=8)
    s.map("TCombobox", fieldbackground=[("readonly", "white")],
          bordercolor=[("focus", AZUL_FONDO)])
    s.configure("Treeview", rowheight=30, font=(FUENTE, 10), background="white",
                fieldbackground="white", bordercolor="#dfe3e8")
    s.configure("Treeview.Heading", background=NAVY, foreground="white",
                font=(FUENTE, 10, "bold"), padding=8, relief="flat")
    s.map("Treeview.Heading", background=[("active", AZUL_FONDO)])
    s.map("Treeview", background=[("selected", "#dbe8f7")],
          foreground=[("selected", TEXTO)])
    root.option_add("*TCombobox*Listbox.font", (FUENTE, 11))


# ---------------------------------------------------------
# WIDGETS REUTILIZABLES
# ---------------------------------------------------------
def boton(parent, texto, comando, bg=NAVY, fg="white"):
    b = tk.Button(parent, text=texto, command=comando, bg=bg, fg=fg,
                  activebackground=aclarar(bg), activeforeground=fg,
                  relief="flat", bd=0, cursor="hand2",
                  font=(FUENTE, 11, "bold"), padx=20, pady=10)
    b.bind("<Enter>", lambda e: b.config(bg=aclarar(bg)))
    b.bind("<Leave>", lambda e: b.config(bg=bg))
    return b


def etiqueta(parent, texto):
    tk.Label(parent, text=texto, bg="white", fg=TEXTO, anchor="w",
             font=(FUENTE, 10, "bold")).pack(fill="x", pady=(12, 3))


def campo(parent, texto):
    etiqueta(parent, texto)
    e = tk.Entry(parent, font=(FUENTE, 12), relief="flat", bg="white", fg=TEXTO,
                 highlightthickness=1, highlightbackground=BORDE,
                 highlightcolor=AZUL_FONDO, insertbackground=TEXTO)
    e.pack(fill="x", ipady=9)
    return e


def combo(parent, texto, valores, placeholder):
    etiqueta(parent, texto)
    c = ttk.Combobox(parent, values=valores, state="readonly", font=(FUENTE, 12))
    c.set(placeholder)
    c.pack(fill="x")
    return c


def fila2(parent):
    """Dos columnas iguales, como en el formulario de la web."""
    fila = tk.Frame(parent, bg="white")
    fila.pack(fill="x")
    izq = tk.Frame(fila, bg="white")
    izq.pack(side="left", fill="x", expand=True, padx=(0, 10))
    der = tk.Frame(fila, bg="white")
    der.pack(side="left", fill="x", expand=True, padx=(10, 0))
    return izq, der


def pagina_base(pagina, app, icono, titulo):
    """Tarjeta blanca con titulo y linea, igual que 'Registro de Documentos'."""
    pagina.configure(bg=GRIS_FONDO)
    tk.Button(pagina, text="← Volver al inicio", command=lambda: app.ir("home"),
              bg=GRIS_FONDO, fg=AZUL_FONDO, relief="flat", cursor="hand2",
              activebackground=GRIS_FONDO, font=(FUENTE, 10, "bold")
              ).pack(anchor="w", padx=60, pady=(14, 0))
    card = tk.Frame(pagina, bg="white", highlightthickness=1,
                    highlightbackground="#dfe3e8")
    card.pack(fill="both", expand=True, padx=60, pady=(8, 24))
    cuerpo = tk.Frame(card, bg="white")
    cuerpo.pack(fill="both", expand=True, padx=40, pady=24)
    tk.Label(cuerpo, text=icono + "  " + titulo, font=(FUENTE, 20, "bold"),
             fg=NAVY, bg="white", anchor="w").pack(fill="x")
    tk.Frame(cuerpo, bg="#dfe3e8", height=1).pack(fill="x", pady=(10, 6))
    return cuerpo


def tarjeta(parent, icono, titulo, desc, comando, color):
    f = tk.Frame(parent, bg="white", highlightthickness=1,
                 highlightbackground="#dfe3e8", cursor="hand2")
    widgets = [
        tk.Label(f, text=icono, font=("Segoe UI Emoji", 26), bg="white", fg=color),
        tk.Label(f, text=titulo, font=(FUENTE, 12, "bold"), bg="white", fg=NAVY),
        tk.Label(f, text=desc, font=(FUENTE, 10), bg="white", fg="#555",
                 wraplength=180, justify="center"),
    ]
    widgets[0].pack(pady=(22, 6))
    widgets[1].pack(pady=4)
    widgets[2].pack(pady=(4, 22), padx=12)
    for w in [f] + widgets:
        w.bind("<Button-1>", lambda e: comando())
        w.bind("<Enter>", lambda e: f.config(highlightbackground=AZUL_FONDO))
        w.bind("<Leave>", lambda e: f.config(highlightbackground="#dfe3e8"))
    return f


# ---------------------------------------------------------
# PANTALLA 1: LOGIN
# ---------------------------------------------------------
class Login(tk.Frame):
    def __init__(self, app):
        super().__init__(app, bg=AZUL_FONDO)
        self.app = app
        self.intentos = 0

        card = tk.Frame(self, bg="white")
        card.place(relx=0.5, rely=0.5, anchor="center")

        # ----- lado izquierdo: marca -----
        izq = tk.Frame(card, bg="white", width=440, height=500)
        izq.pack(side="left", padx=(30, 0), pady=30)
        izq.pack_propagate(False)

        tk.Label(izq, text="🏛", font=("Segoe UI Emoji", 44), bg="white",
                 fg=NAVY).pack(pady=(10, 0))
        tk.Label(izq, text="MUNICIPALIDAD\nDISTRITAL DE ATE", font=(FUENTE, 13, "bold"),
                 fg=NAVY, bg="white").pack()
        tk.Label(izq, text="MESA DE PARTES", font=(FUENTE, 28, "bold"),
                 fg=NAVY, bg="white").pack(pady=(26, 0))
        tk.Label(izq, text="VIRTUAL", font=(FUENTE, 28, "bold"),
                 fg=TEAL, bg="white").pack()
        tk.Label(izq, text="Bienvenido a la plataforma de la Municipalidad Distrital "
                           "de Ate para el registro, recepción y seguimiento de "
                           "expedientes de emergencias.",
                 font=(FUENTE, 11), fg="#555", bg="white", wraplength=360,
                 justify="center").pack(pady=(24, 0))

        # ----- lado derecho: formulario -----
        der = tk.Frame(card, bg="white", width=400, height=500)
        der.pack(side="left", padx=(20, 40), pady=30)
        der.pack_propagate(False)

        tk.Label(der, text="Iniciar Sesión", font=(FUENTE, 22, "bold"),
                 fg=NAVY, bg="white").pack(pady=(30, 14))

        self.e_user = campo(der, "Usuario*")

        etiqueta(der, "Contraseña*")
        caja = tk.Frame(der, bg="white", highlightthickness=1, highlightbackground=BORDE)
        caja.pack(fill="x")
        self.e_pass = tk.Entry(caja, show="•", relief="flat", font=(FUENTE, 12),
                               bg="white", fg=TEXTO)
        self.e_pass.pack(side="left", fill="x", expand=True, ipady=9, padx=(8, 0))
        tk.Button(caja, text="👁", command=self.ver_clave, relief="flat", bg="white",
                  cursor="hand2", activebackground="white").pack(side="right", padx=6)

        self.lbl_error = tk.Label(der, text="", fg="#c62828", bg="white",
                                  font=(FUENTE, 10))
        self.lbl_error.pack(pady=(10, 0))

        boton(der, "➜  Iniciar Sesión", self.ingresar).pack(fill="x", pady=(6, 0))

        olvido = tk.Label(der, text="¿Olvidaste tu clave?", fg=AZUL_FONDO, bg="white",
                          font=(FUENTE, 11, "bold"), cursor="hand2")
        olvido.pack(pady=(16, 0))
        olvido.bind("<Button-1>", lambda e: messagebox.showinfo(
            "Clave", "Comunícate con el administrador del sistema."))

        tk.Label(der, text="Acceso solo para personal autorizado.\n"
                           "Atención habilitada las 24 horas.",
                 font=(FUENTE, 10), fg="#555", bg="white").pack(pady=(24, 0))

        self.e_user.bind("<Return>", lambda e: self.ingresar())
        self.e_pass.bind("<Return>", lambda e: self.ingresar())
        self.e_user.focus_set()

    def ver_clave(self):
        self.e_pass.config(show="" if self.e_pass.cget("show") else "•")

    def ingresar(self):
        usuario = self.e_user.get().strip()
        clave = self.e_pass.get().strip()
        if usuario == USUARIO and clave == CLAVE:
            self.app.entrar(usuario)
            return
        self.intentos += 1
        if self.intentos >= 3:
            messagebox.showerror("Acceso bloqueado",
                                 "Superaste los 3 intentos. El programa se cerrará.")
            self.app.destroy()
        else:
            self.lbl_error.config(text="Usuario o clave incorrectos. Intento %d de 3."
                                       % self.intentos)


# ---------------------------------------------------------
# PANTALLA 2: INICIO (banner + tarjetas)
# ---------------------------------------------------------
class Home(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=GRIS_FONDO)
        self.app = app
        cont = tk.Frame(self, bg=GRIS_FONDO)
        cont.pack(fill="x", padx=90, pady=24)

        banner = tk.Frame(cont, bg=NAVY)
        banner.pack(fill="x")
        tk.Label(banner, text="¡Bienvenido a Mesa de Partes Virtual!", fg="white",
                 bg=NAVY, font=(FUENTE, 24, "bold")).pack(pady=(30, 6))
        tk.Label(banner, text="Gestiona los expedientes de emergencias de manera fácil y segura",
                 fg="#d6e4f2", bg=NAVY, font=(FUENTE, 12)).pack()
        self.lbl_total = tk.Label(banner, text="", fg="#8fd3e3", bg=NAVY,
                                  font=(FUENTE, 11, "bold"))
        self.lbl_total.pack(pady=(10, 28))

        tk.Label(cont, text="Trámites", font=(FUENTE, 16, "bold"), fg=NAVY,
                 bg=GRIS_FONDO).pack(anchor="w", pady=(24, 10))

        fila = tk.Frame(cont, bg=GRIS_FONDO)
        fila.pack(fill="x")
        opciones = [
            ("📋", "Registrar expediente", "Registra una nueva emergencia con su prioridad automática.",
             "registrar", "#3b5bdb"),
            ("🔍", "Buscar por código", "Consulta un expediente con su código (ej. EXP-0001).",
             "consultar", "#3b5bdb"),
            ("📑", "Listado y clasificación", "Lista ordenada por prioridad o código y filtra por desastre.",
             "listar", "#2e7d32"),
            ("🛠", "Archivo de datos", "Abre expedientes.txt en el Bloc de notas y recarga los cambios.",
             "archivo", "#e03131"),
        ]
        for i, (ic, ti, de, destino, color) in enumerate(opciones):
            fila.columnconfigure(i, weight=1, uniform="t")
            t = tarjeta(fila, ic, ti, de, lambda d=destino: app.ir(d), color)
            t.grid(row=0, column=i, padx=8, sticky="nsew")

        resumen = tk.Frame(cont, bg="white", highlightthickness=1,
                           highlightbackground="#dfe3e8")
        resumen.pack(fill="x", pady=(24, 0))
        tk.Label(resumen, text="Resumen por prioridad", font=(FUENTE, 13, "bold"),
                 fg=NAVY, bg="white").pack(anchor="w", padx=24, pady=(16, 8))
        fila_r = tk.Frame(resumen, bg="white")
        fila_r.pack(fill="x", padx=24, pady=(0, 18))
        self.lbl_prio = {}
        for i, p in enumerate(PRIORIDADES):
            fila_r.columnconfigure(i, weight=1)
            caja = tk.Frame(fila_r, bg="white")
            caja.grid(row=0, column=i)
            n = tk.Label(caja, text="0", font=(FUENTE, 26, "bold"), fg=COLOR_PRIORIDAD[p],
                         bg="white")
            n.pack()
            tk.Label(caja, text="Prioridad " + p, font=(FUENTE, 10), fg="#555",
                     bg="white").pack()
            self.lbl_prio[p] = n

    def actualizar(self):
        matriz = self.app.matriz
        self.lbl_total.config(text="Expedientes registrados: %d" % len(matriz))
        for p in PRIORIDADES:
            cantidad = 0
            for fila in matriz:
                if fila[PRIORIDAD] == p:
                    cantidad += 1
            self.lbl_prio[p].config(text=str(cantidad))


# ---------------------------------------------------------
# PANTALLA 3: REGISTRAR (formulario)
# ---------------------------------------------------------
class Registrar(tk.Frame):
    P_DES = "Seleccione tipo de desastre"
    P_SOL = "Seleccione tipo de solicitud"

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        c = pagina_base(self, app, "📄", "Registro de Expedientes")

        izq, der = fila2(c)
        self.e_dni = campo(izq, "DNI* (8 dígitos)")
        self.e_nombre = campo(der, "Nombres y apellidos*")

        izq, der = fila2(c)
        self.c_des = combo(izq, "Tipo de desastre*", TIPOS_DESASTRE, self.P_DES)
        self.c_sol = combo(der, "Tipo de solicitud*", TIPOS_SOLICITUD, self.P_SOL)

        self.e_ubi = campo(c, "Ubicación o lugar*")

        etiqueta(c, "Descripción* (mínimo 10 caracteres)")
        self.t_desc = tk.Text(c, height=4, font=(FUENTE, 12), relief="flat", wrap="word",
                              highlightthickness=1, highlightbackground=BORDE,
                              highlightcolor=AZUL_FONDO, fg=TEXTO)
        self.t_desc.pack(fill="x")

        pie = tk.Frame(c, bg="white")
        pie.pack(fill="x", pady=(20, 0))
        self.lbl_error = tk.Label(pie, text="(*) Campos obligatorios", fg="#c62828",
                                  bg="white", font=(FUENTE, 11), wraplength=520,
                                  justify="left")
        self.lbl_error.pack(side="left")
        boton(pie, "➤  Enviar expediente", self.enviar, bg=AZUL_BTN).pack(side="right")

    def limpiar(self):
        self.e_dni.delete(0, "end")
        self.e_nombre.delete(0, "end")
        self.e_ubi.delete(0, "end")
        self.t_desc.delete("1.0", "end")
        self.c_des.set(self.P_DES)
        self.c_sol.set(self.P_SOL)
        self.lbl_error.config(text="(*) Campos obligatorios")

    def enviar(self):
        dni = self.e_dni.get().strip()
        nombre = self.e_nombre.get().strip()
        desastre = self.c_des.get()
        solicitud = self.c_sol.get()
        ubicacion = self.e_ubi.get().strip()
        descripcion = " ".join(self.t_desc.get("1.0", "end").split())  # sin saltos de linea

        error = ""
        if not (len(dni) == 8 and dni.isdigit()):
            error = "DNI inválido: deben ser 8 dígitos."
        elif len(nombre) < 3 or not nombre.replace(" ", "").isalpha():
            error = "Nombre inválido: solo letras y espacios."
        elif desastre not in TIPOS_DESASTRE:
            error = "Selecciona el tipo de desastre."
        elif solicitud not in TIPOS_SOLICITUD:
            error = "Selecciona el tipo de solicitud."
        elif len(ubicacion) < 3:
            error = "La ubicación debe tener al menos 3 caracteres."
        elif len(descripcion) < 10:
            error = "La descripción debe tener al menos 10 caracteres."
        elif "|" in ubicacion or "|" in descripcion:
            error = "No se permite el caracter |"

        if error != "":
            self.lbl_error.config(text=error)
            return

        matriz = self.app.matriz
        fila = [generar_codigo(matriz), dni, nombre.title(), desastre, solicitud,
                ubicacion.title(), descripcion,
                calcular_prioridad(desastre, solicitud, descripcion),
                datetime.now().strftime("%Y-%m-%d %H:%M")]
        matriz.append(fila)
        guardar_expediente(fila)
        messagebox.showinfo("Expediente guardado",
                            "Código: %s\nPrioridad: %s" % (fila[COD], fila[PRIORIDAD]))
        self.limpiar()


# ---------------------------------------------------------
# PANTALLA 4: BUSCAR POR CODIGO
# ---------------------------------------------------------
class Consultar(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        c = pagina_base(self, app, "🔍", "Consulta de Expedientes")

        etiqueta(c, "Código del expediente (ej. EXP-0001 o 1)")
        fila = tk.Frame(c, bg="white")
        fila.pack(fill="x")
        self.e_cod = tk.Entry(fila, font=(FUENTE, 12), relief="flat", bg="white",
                              fg=TEXTO, highlightthickness=1, highlightbackground=BORDE,
                              highlightcolor=AZUL_FONDO)
        self.e_cod.pack(side="left", fill="x", expand=True, ipady=9, padx=(0, 12))
        self.e_cod.bind("<Return>", lambda e: self.buscar())
        boton(fila, "🔍  Buscar", self.buscar, bg=AZUL_BTN).pack(side="right")

        self.resultado = tk.Frame(c, bg="white")
        self.resultado.pack(fill="both", expand=True, pady=(20, 0))

    def buscar(self):
        for w in self.resultado.winfo_children():
            w.destroy()
        texto = self.e_cod.get().strip().upper()
        if texto.isdigit():
            texto = "EXP-" + texto.zfill(4)
        f = buscar_codigo(self.app.matriz, texto)
        if f is None:
            tk.Label(self.resultado, text="No se encontró el expediente.", fg="#c62828",
                     bg="white", font=(FUENTE, 12)).pack(anchor="w")
            return

        datos = [("Código", f[COD]), ("DNI", f[DNI]), ("Ciudadano", f[NOMBRE]),
                 ("Desastre", f[DESASTRE]), ("Solicitud", f[SOLICITUD]),
                 ("Ubicación", f[UBIACION]), ("Descripción", f[DESCRIPCION]),
                 ("Prioridad", f[PRIORIDAD]), ("Fecha", f[FECHA])]
        for i in range(len(datos)):
            clave, valor = datos[i]
            tk.Label(self.resultado, text=clave, font=(FUENTE, 11, "bold"), fg="#555",
                     bg="white", width=12, anchor="w").grid(row=i, column=0, sticky="nw", pady=4)
            if clave == "Prioridad":
                tk.Label(self.resultado, text=valor, fg="white", bg=COLOR_PRIORIDAD[valor],
                         font=(FUENTE, 10, "bold"), padx=14, pady=2
                         ).grid(row=i, column=1, sticky="w", pady=4)
            else:
                tk.Label(self.resultado, text=valor, font=(FUENTE, 11), fg=TEXTO,
                         bg="white", wraplength=600, justify="left", anchor="w"
                         ).grid(row=i, column=1, sticky="w", pady=4)


# ---------------------------------------------------------
# PANTALLA 5: LISTAR / CLASIFICAR
# ---------------------------------------------------------
class Listar(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        c = pagina_base(self, app, "📑", "Listado de Expedientes")

        barra = tk.Frame(c, bg="white")
        barra.pack(fill="x", pady=(6, 10))
        tk.Label(barra, text="Ordenar por:", bg="white", fg=TEXTO,
                 font=(FUENTE, 10, "bold")).pack(side="left")
        self.c_orden = ttk.Combobox(barra, state="readonly", width=24, font=(FUENTE, 11),
                                    values=["Prioridad (Alta primero)", "Código"])
        self.c_orden.current(0)
        self.c_orden.pack(side="left", padx=(8, 24))
        tk.Label(barra, text="Tipo de desastre:", bg="white", fg=TEXTO,
                 font=(FUENTE, 10, "bold")).pack(side="left")
        self.c_filtro = ttk.Combobox(barra, state="readonly", width=22, font=(FUENTE, 11),
                                     values=["Todos"] + TIPOS_DESASTRE)
        self.c_filtro.current(0)
        self.c_filtro.pack(side="left", padx=8)
        for cb in (self.c_orden, self.c_filtro):
            cb.bind("<<ComboboxSelected>>", lambda e: self.actualizar())

        marco = tk.Frame(c, bg="white")
        marco.pack(fill="both", expand=True)
        cols = ("cod", "prio", "des", "sol", "ubi", "fecha")
        self.tabla = ttk.Treeview(marco, columns=cols, show="headings")
        anchos = [90, 80, 150, 140, 200, 130]
        nombres = ["Código", "Prioridad", "Desastre", "Solicitud", "Ubicación", "Fecha"]
        for i in range(len(cols)):
            self.tabla.heading(cols[i], text=nombres[i])
            self.tabla.column(cols[i], width=anchos[i], anchor="w")
        barra_v = ttk.Scrollbar(marco, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=barra_v.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        barra_v.pack(side="right", fill="y")
        for p in PRIORIDADES:
            self.tabla.tag_configure(p, foreground=COLOR_PRIORIDAD[p])
        self.tabla.bind("<Double-1>", self.ver_detalle)

        self.lbl_total = tk.Label(c, text="", bg="white", fg="#555", font=(FUENTE, 10))
        self.lbl_total.pack(anchor="w", pady=(8, 0))
        tk.Label(c, text="Doble clic sobre un expediente para ver el detalle.", bg="white",
                 fg="#888", font=(FUENTE, 9)).pack(anchor="w")

    def actualizar(self):
        filas = self.app.matriz
        if self.c_filtro.get() != "Todos":
            filas = filtrar_por_desastre(filas, self.c_filtro.get())
        if self.c_orden.current() == 0:
            filas = ordenar_por_prioridad(filas)
        else:
            filas = ordenar_por_codigo(filas)

        for item in self.tabla.get_children():
            self.tabla.delete(item)
        for f in filas:
            self.tabla.insert("", "end", tags=(f[PRIORIDAD],),
                              values=(f[COD], f[PRIORIDAD], f[DESASTRE], f[SOLICITUD],
                                      f[UBIACION], f[FECHA]))
        self.lbl_total.config(text="Total: %d" % len(filas))

    def ver_detalle(self, evento):
        seleccion = self.tabla.selection()
        if len(seleccion) == 0:
            return
        codigo = self.tabla.item(seleccion[0], "values")[0]
        f = buscar_codigo(self.app.matriz, codigo)
        if f is not None:
            messagebox.showinfo(
                "Expediente " + f[COD],
                "DNI: %s\nCiudadano: %s\nDesastre: %s\nSolicitud: %s\nUbicación: %s\n"
                "Prioridad: %s\nFecha: %s\n\nDescripción:\n%s"
                % (f[DNI], f[NOMBRE], f[DESASTRE], f[SOLICITUD], f[UBIACION],
                   f[PRIORIDAD], f[FECHA], f[DESCRIPCION]))


# ---------------------------------------------------------
# PANTALLA 6: ARCHIVO / BLOC DE NOTAS
# ---------------------------------------------------------
class Archivo(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        c = pagina_base(self, app, "🛠", "Archivo de Datos")

        tk.Label(c, text="Cada línea de expedientes.txt es un expediente.\n"
                         "1. Abre el archivo en el Bloc de notas.\n"
                         "2. Edita o borra las líneas que quieras, guarda (Ctrl + S) y cierra.\n"
                         "3. Presiona \"Recargar datos\" para que el programa use los cambios.",
                 bg="white", fg=TEXTO, font=(FUENTE, 12), justify="left"
                 ).pack(anchor="w", pady=(16, 20))

        fila = tk.Frame(c, bg="white")
        fila.pack(anchor="w")
        boton(fila, "📝  Abrir en Bloc de notas", self.abrir, bg=NAVY).pack(side="left")
        boton(fila, "↻  Recargar datos", self.recargar, bg=AZUL_BTN).pack(side="left", padx=12)

        self.lbl_total = tk.Label(c, text="", bg="white", fg="#555", font=(FUENTE, 11))
        self.lbl_total.pack(anchor="w", pady=(20, 0))

    def actualizar(self):
        self.lbl_total.config(text="Expedientes cargados: %d" % len(self.app.matriz))

    def abrir(self):
        if os.name != "nt":
            messagebox.showinfo("Aviso", "Esta opción solo funciona en Windows.")
            return
        if not os.path.exists(ARCHIVO):
            messagebox.showinfo("Aviso", "Todavía no hay archivo: registra un expediente primero.")
            return
        subprocess.Popen(["notepad.exe", ARCHIVO])

    def recargar(self):
        self.app.matriz[:] = cargar_expedientes()     # misma lista, datos nuevos
        self.actualizar()
        messagebox.showinfo("Listo", "Archivo recargado. Expedientes actuales: %d"
                            % len(self.app.matriz))


# ---------------------------------------------------------
# VENTANA PRINCIPAL (barra superior + paginas)
# ---------------------------------------------------------
class Principal(tk.Frame):
    def __init__(self, app, usuario):
        super().__init__(app, bg=GRIS_FONDO)
        self.app = app

        header = tk.Frame(self, bg=AZUL_HEADER)
        header.pack(fill="x")
        tk.Label(header, text="🏛", font=("Segoe UI Emoji", 22), bg="white", fg=NAVY,
                 width=3).pack(side="left", padx=(24, 12), pady=14)
        titulos = tk.Frame(header, bg=AZUL_HEADER)
        titulos.pack(side="left")
        tk.Label(titulos, text="Mesa de Partes", font=(FUENTE, 17, "bold"), fg="white",
                 bg=AZUL_HEADER).pack(anchor="w")
        tk.Label(titulos, text="Municipalidad de Ate", font=(FUENTE, 10), fg="#d6e4f2",
                 bg=AZUL_HEADER).pack(anchor="w")

        usuario_btn = tk.Menubutton(header, text="  (A)  %s  ▾  " % usuario, fg="white",
                                    bg="#2a5f92", activebackground="#3a70a4",
                                    activeforeground="white", relief="flat",
                                    font=(FUENTE, 11, "bold"), cursor="hand2")
        menu = tk.Menu(usuario_btn, tearoff=0)
        menu.add_command(label="Inicio", command=lambda: self.mostrar("home"))
        menu.add_command(label="Cerrar sesión", command=app.cerrar_sesion)
        menu.add_command(label="Salir", command=app.destroy)
        usuario_btn.config(menu=menu)
        usuario_btn.pack(side="right", padx=24, ipady=8)

        cuerpo = tk.Frame(self, bg=GRIS_FONDO)
        cuerpo.pack(fill="both", expand=True)
        self.paginas = {
            "home": Home(cuerpo, app),
            "registrar": Registrar(cuerpo, app),
            "consultar": Consultar(cuerpo, app),
            "listar": Listar(cuerpo, app),
            "archivo": Archivo(cuerpo, app),
        }
        self.actual = None
        self.mostrar("home")

    def mostrar(self, nombre):
        if self.actual is not None:
            self.actual.pack_forget()
        self.actual = self.paginas[nombre]
        if hasattr(self.actual, "actualizar"):
            self.actual.actualizar()
        self.actual.pack(fill="both", expand=True)


# ---------------------------------------------------------
# APLICACION
# ---------------------------------------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mesa de Partes Digital-Resiliente - Municipalidad de Ate")
        self.geometry("1100x720")
        self.minsize(960, 660)
        self.configure(bg=AZUL_FONDO)
        estilos(self)

        self.matriz = cargar_expedientes()
        self.principal = None
        self.login = Login(self)
        self.login.pack(fill="both", expand=True)

    def entrar(self, usuario):
        self.login.pack_forget()
        self.principal = Principal(self, usuario)
        self.principal.pack(fill="both", expand=True)

    def cerrar_sesion(self):
        self.principal.destroy()
        self.login.destroy()
        self.login = Login(self)
        self.login.pack(fill="both", expand=True)

    def ir(self, nombre):
        self.principal.mostrar(nombre)


if __name__ == "__main__":
    App().mainloop()
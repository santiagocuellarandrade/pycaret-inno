"""Interfaz gráfica del clasificador de deserción estudiantil (tema oscuro).

Se abre con:   uv run app

Lee de la carpeta ``modelo/`` los dos archivos que exporta el cuaderno:
  - <NOMBRE_MODELO>.pkl  -> pipeline de PyCaret (preprocesamiento + modelo calibrado)
  - metricas.json        -> columnas, tipos, rangos, categorías y métricas

El formulario se construye a partir de ``metricas.json``: si reentrenas el
cuaderno y cambian las columnas, la interfaz se ajusta sola.
"""
from __future__ import annotations

import json
from datetime import datetime
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

# --------------------------------------------------------------------------- #
# 1. Rutas del modelo
# --------------------------------------------------------------------------- #
try:  # lo normal: las mismas constantes que usa el cuaderno
    from clasificador_desertores.core import CARPETA_MODELO, NOMBRE_MODELO
except Exception:  # plan B: buscar la carpeta ``modelo/`` cerca del archivo o del cwd
    CARPETA_MODELO, NOMBRE_MODELO = None, None


def _resolver_modelo() -> tuple[Path, str]:
    """Devuelve (carpeta, nombre sin extensión) del modelo exportado."""
    carpeta = Path(CARPETA_MODELO) if CARPETA_MODELO else None
    if carpeta is None or not (carpeta / "metricas.json").exists():
        base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
        candidatos = [Path.cwd(), *Path.cwd().parents, base, *base.parents]
        carpeta = next((c / "modelo" for c in candidatos if (c / "modelo" / "metricas.json").exists()), None)
    if carpeta is None:
        raise FileNotFoundError(
            "No encuentro la carpeta 'modelo/' con metricas.json. "
            "Ejecuta el cuaderno hasta el Paso 9 para exportar el modelo."
        )
    nombre = NOMBRE_MODELO
    if not nombre or not (carpeta / f"{nombre}.pkl").exists():
        pkls = sorted(carpeta.glob("*.pkl"))
        if not pkls:
            raise FileNotFoundError(f"No hay ningún .pkl dentro de {carpeta}")
        nombre = pkls[0].stem
    return carpeta, nombre


# --------------------------------------------------------------------------- #
# 2. Tema visual
# --------------------------------------------------------------------------- #
BG = "#20302a"          # fondo principal
BG_PANEL = "#2a3f37"    # paneles / pestañas
BG_CAMPO = "#182520"    # cajas de texto, spinbox, combobox
FG = "#b4b4b4"          # todo el texto
BTN = "#654d34"         # botones
BTN_HOVER = "#7d6040"
BTN_PRESS = "#503c28"
BORDE = "#3b5248"

FUENTE = "Segoe UI"
F_NORMAL = (FUENTE, 12)
F_PEQ = (FUENTE, 10)
F_TITULO = (FUENTE, 22, "bold")
F_GRANDE = (FUENTE, 28, "bold")
F_BOTON = (FUENTE, 12, "bold")
F_PESTANA = (FUENTE, 12, "bold")

# Colores por clase: deserción = rojo, graduación = violeta, sigue matriculado = amarillo
COLOR_CLASE = {"Dropout": "#e53935", "Enrolled": "#ffd60a", "Graduate": "#5e17eb"}
COLOR_SIN_ALERTA = "#6fcf97"
NOMBRE_CLASE = {"Dropout": "Deserción", "Enrolled": "Sigue matriculado", "Graduate": "Graduación"}

# --------------------------------------------------------------------------- #
# 3. Textos y reglas de presentación (la interfaz está en español)
# --------------------------------------------------------------------------- #
ETIQUETAS = {
    "Marital_status": "Estado civil",
    "Application_mode": "Modo de postulación (código)",
    "Application_order": "Orden de preferencia de la carrera (0 = primera)",
    "Course": "Programa / carrera",
    "Daytime_attendance": "Jornada",
    "Previous_qualification": "Estudios previos (código)",
    "Nationality": "Nacionalidad (código)",
    "Mothers_qualification": "Estudios de la madre (código)",
    "Fathers_qualification": "Estudios del padre (código)",
    "Mothers_occupation": "Ocupación de la madre (código)",
    "Fathers_occupation": "Ocupación del padre (código)",
    "Displaced": "Desplazado de su lugar de origen",
    "Educational_special_needs": "Necesidades educativas especiales",
    "Debtor": "Deudor",
    "Tuition_fees_up_to_date": "Matrícula al día",
    "Gender": "Género",
    "Scholarship_holder": "Tiene beca",
    "Age_at_enrollment": "Edad al ingresar",
    "International": "Estudiante internacional",
    "Unemployment_rate": "Tasa de desempleo (%)",
    "Inflation_rate": "Tasa de inflación (%)",
    "GDP": "PIB (variación)",
}
SUFIJOS_CU = {
    "credited": "Materias convalidadas",
    "enrolled": "Materias inscritas",
    "evaluations": "Evaluaciones presentadas",
    "approved": "Materias aprobadas",
    "grade": "Nota promedio",
    "no_evals": "Materias sin evaluaciones",
}
OPCIONES_BINARIAS = {  # columna -> (texto para 0, texto para 1)
    "Daytime_attendance": ("Nocturna", "Diurna"),
    "Gender": ("Mujer", "Hombre"),
}
# Solo se traducen los códigos cuya equivalencia es corta y conocida (descripción UCI, dataset 697).
# Verifícalos con la ficha del dataset; el resto de códigos se muestra tal cual.
DESCRIPCIONES = {
    "Previous_qualification": {"1": "Educación secundaria", "2": "Superior – licenciatura", "3": "Superior – grado", "4": "Superior – maestría", "5": "Superior – doctorado", "6": "Cursando educación superior", "9": "12.º año sin terminar", "10": "11.º año sin terminar", "12": "Otro – 11.º año", "14": "10.º año", "15": "10.º año sin terminar", "19": "Básica 3.er ciclo (9.º a 11.º)", "38": "Básica 2.º ciclo (6.º a 8.º)", "39": "Especialización tecnológica", "40": "Superior – grado (1.er ciclo)", "42": "Técnico superior profesional", "43": "Superior – maestría (2.º ciclo)"},
    "Marital_status": {"1": "Soltero/a", "2": "Casado/a", "3": "Viudo/a", "4": "Divorciado/a",
                       "5": "Unión libre", "6": "Separado/a legalmente"},
    "Course": {"33": "Tecnologías de producción de biocombustibles", "171": "Animación y diseño multimedia",
               "8014": "Servicio social (nocturno)", "9003": "Agronomía", "9070": "Diseño de comunicación",
               "9085": "Enfermería veterinaria", "9119": "Ingeniería informática", "9130": "Equinocultura",
               "9147": "Gestión", "9238": "Servicio social", "9254": "Turismo", "9500": "Enfermería",
               "9556": "Higiene oral", "9670": "Publicidad y marketing", "9773": "Periodismo y comunicación",
               "9853": "Educación básica", "9991": "Gestión (nocturno)"},
}
# --- descripciones ampliadas (ficha UCI, dataset 697) ---
_NIVELES = {
    "1": "Secundaria (12.º año o equivalente)", "2": "Superior – licenciatura", "3": "Superior – grado",
    "4": "Superior – maestría", "5": "Superior – doctorado", "6": "Cursando educación superior",
    "9": "12.º año sin terminar", "10": "11.º año sin terminar", "11": "7.º año (antiguo)",
    "12": "Otro – 11.º año", "13": "2.º año del complementario de bachillerato", "14": "10.º año",
    "18": "Curso de comercio general", "19": "Básica 3.er ciclo (9.º a 11.º)",
    "20": "Curso complementario de bachillerato", "22": "Curso técnico-profesional",
    "25": "Complementario de bachillerato sin concluir", "26": "7.º año",
    "27": "2.º ciclo del bachillerato general", "29": "9.º año sin terminar", "30": "8.º año",
    "31": "Curso general de administración y comercio", "33": "Contabilidad y administración complementaria",
    "34": "Desconocido", "35": "No sabe leer ni escribir", "36": "Sabe leer sin haber cursado 4.º año",
    "37": "Básica 1.er ciclo (4.º/5.º año)", "38": "Básica 2.º ciclo (6.º a 8.º)",
    "39": "Especialización tecnológica", "40": "Superior – grado (1.er ciclo)",
    "41": "Estudios superiores especializados", "42": "Técnico superior profesional",
    "43": "Superior – maestría (2.º ciclo)", "44": "Superior – doctorado (3.er ciclo)",
}
_OCUPACIONES = {
    "0": "Estudiante", "1": "Directivos, gerentes y cargos del poder público",
    "2": "Profesionales intelectuales y científicos", "3": "Técnicos y profesiones de nivel intermedio",
    "4": "Personal administrativo", "5": "Servicios personales, seguridad y vendedores",
    "6": "Agricultura, pesca y silvicultura (calificados)", "7": "Industria, construcción y artesanía (calificados)",
    "8": "Operadores de máquinas y ensambladores", "9": "Trabajadores no calificados",
    "10": "Fuerzas armadas", "90": "Otra situación", "99": "Sin dato (en blanco)",
    "101": "Oficiales de las fuerzas armadas", "102": "Sargentos de las fuerzas armadas",
    "103": "Otro personal de las fuerzas armadas", "112": "Directores de servicios administrativos/comerciales",
    "114": "Directores de hotelería, comercio y otros servicios",
    "121": "Especialistas en ciencias, matemáticas e ingeniería", "122": "Profesionales de la salud",
    "123": "Docentes", "124": "Especialistas en finanzas, contabilidad y administración",
    "125": "Especialistas en TIC (informática)", "131": "Técnicos de ciencias e ingeniería (nivel intermedio)",
    "132": "Técnicos de la salud (nivel intermedio)", "134": "Técnicos en servicios legales, sociales y culturales",
    "135": "Técnicos en TIC (informática)", "141": "Oficinistas, secretarios y digitadores",
    "143": "Operadores de datos, contabilidad y registros", "144": "Otro personal de apoyo administrativo",
    "151": "Trabajadores de servicios personales", "152": "Vendedores", "153": "Trabajadores de cuidado personal",
    "154": "Personal de protección y seguridad", "161": "Agricultores y ganaderos orientados al mercado",
    "163": "Agricultores y pescadores de subsistencia", "171": "Obreros de construcción (excepto electricistas)",
    "172": "Obreros de metalurgia y metalmecánica", "173": "Obreros de imprenta, joyería y artesanos",
    "174": "Obreros de electricidad y electrónica", "175": "Obreros de alimentos, madera y confección",
    "181": "Operadores de plantas y máquinas fijas", "182": "Trabajadores de ensamblaje",
    "183": "Conductores y operadores de equipo móvil", "191": "Trabajadores de limpieza",
    "192": "No calificados agrícolas, pecuarios y pesqueros",
    "193": "No calificados en minería, construcción y transporte",
    "194": "Ayudantes de preparación de comidas", "195": "Vendedores ambulantes (excepto comida)",
}
DESCRIPCIONES.update({
    "Nationality": {
        "1": "Portuguesa", "2": "Alemana", "6": "Española", "11": "Italiana", "13": "Neerlandesa",
        "14": "Inglesa", "17": "Lituana", "21": "Angoleña", "22": "Caboverdiana", "24": "Guineana",
        "25": "Mozambiqueña", "26": "Santotomense", "32": "Turca", "41": "Brasileña", "62": "Rumana",
        "100": "Moldava", "101": "Mexicana", "103": "Ucraniana", "105": "Rusa", "108": "Cubana",
        "109": "Colombiana",
    },
    "Application_mode": {
        "1": "1.ª fase – contingente general", "2": "Ordenanza n.º 612/93",
        "5": "1.ª fase – contingente especial (Azores)", "7": "Titulares de otros cursos superiores",
        "10": "Ordenanza n.º 854-B/99", "15": "Estudiante internacional (pregrado)",
        "16": "1.ª fase – contingente especial (Madeira)", "17": "2.ª fase – contingente general",
        "18": "3.ª fase – contingente general", "26": "Ordenanza 533-A/99, b2 (otro plan)",
        "27": "Ordenanza 533-A/99, b3 (otra institución)", "39": "Mayores de 23 años",
        "42": "Transferencia", "43": "Cambio de carrera",
        "44": "Titulares de diploma de especialización tecnológica", "51": "Cambio de institución/carrera",
        "53": "Titulares de ciclo corto", "57": "Cambio de institución/carrera (internacional)",
    },
    "Mothers_qualification": _NIVELES,
    "Fathers_qualification": _NIVELES,
    "Mothers_occupation": _OCUPACIONES,
    "Fathers_occupation": _OCUPACIONES,
})

GRUPOS = ["1.er semestre", "2.º semestre", "Ingreso", "Perfil personal", "Situación económica", "Contexto del país"]
_INGRESO = {"Application_mode", "Application_order", "Course", "Daytime_attendance", "Previous_qualification"}
_ECONOMICO = {"Debtor", "Tuition_fees_up_to_date", "Scholarship_holder"}
_PAIS = {"Unemployment_rate", "Inflation_rate", "GDP"}

# Valores iniciales razonables (se recortan al rango real de cada variable)
DEFECTOS = {
    "Application_order": 1, "Daytime_attendance": 1, "Tuition_fees_up_to_date": 1, "Age_at_enrollment": 20,
    "Marital_status": "1", "Application_mode": "1", "Previous_qualification": "1", "Nationality": "1",
    "Course": "9254", "Unemployment_rate": 11.1, "Inflation_rate": 1.4, "GDP": 0.32,
    "CU1_enrolled": 6, "CU2_enrolled": 6, "CU1_evaluations": 8, "CU2_evaluations": 8,
    "CU1_approved": 5, "CU2_approved": 5, "CU1_grade": 12, "CU2_grade": 12,
}
# Perfiles de demostración: solo cambian lo académico y lo económico
EJEMPLOS = {
    "Perfil de riesgo bajo": {
        "CU1_enrolled": 6, "CU1_evaluations": 7, "CU1_approved": 6, "CU1_grade": 13.5,
        "CU2_enrolled": 6, "CU2_evaluations": 7, "CU2_approved": 6, "CU2_grade": 13.5,
        "Tuition_fees_up_to_date": 1, "Debtor": 0, "Scholarship_holder": 1, "Age_at_enrollment": 19,
    },
    "Perfil de riesgo alto": {
        "CU1_enrolled": 6, "CU1_evaluations": 6, "CU1_approved": 1, "CU1_grade": 6.0,
        "CU2_enrolled": 6, "CU2_evaluations": 4, "CU2_approved": 0, "CU2_grade": 0.0,
        "Tuition_fees_up_to_date": 0, "Debtor": 1, "Scholarship_holder": 0, "Age_at_enrollment": 27,
    },
}


def etiqueta(col: str) -> str:
    if col in ETIQUETAS:
        return ETIQUETAS[col]
    if col[:4] in ("CU1_", "CU2_"):
        return SUFIJOS_CU.get(col[4:], col[4:])
    return col.replace("_", " ")


def grupo(col: str) -> str:
    if col.startswith("CU1_"):
        return GRUPOS[0]
    if col.startswith("CU2_"):
        return GRUPOS[1]
    if col in _INGRESO:
        return GRUPOS[2]
    if col in _ECONOMICO:
        return GRUPOS[4]
    if col in _PAIS:
        return GRUPOS[5]
    return GRUPOS[3]


# --------------------------------------------------------------------------- #
# 4. Aplicación
# --------------------------------------------------------------------------- #
class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("ClasificadorDesertor")
        self.geometry("1280x800")
        self.minsize(1120, 720)
        self.configure(bg=BG)

        self.modelo = None
        self.campos: dict[str, dict] = {}  # columna -> {"var": StringVar, "tipo": ..., "mapa": ...}
        self._cola_carga: dict = {}

        try:
            self.carpeta, self.nombre_modelo = _resolver_modelo()
            self.info = json.loads((self.carpeta / "metricas.json").read_text(encoding="utf-8"))
            for clave in ("columnas", "tipos", "rangos", "categorias", "clases"):
                if clave not in self.info:
                    raise KeyError(f"Falta '{clave}' en metricas.json (ejecuta el Paso 9 y el final del cuaderno).")
        except Exception as e:  # sin modelo no hay app: avisar claro y salir
            self.withdraw()
            messagebox.showerror("No se pudo abrir la app", str(e))
            self.destroy()
            raise SystemExit(1) from e

        self._estilos()
        self._construir()
        self._cargar_modelo_en_segundo_plano()

    # ---------------------------- estilos ---------------------------------- #
    def _estilos(self) -> None:
        st = ttk.Style(self)
        st.theme_use("clam")

        # Lista desplegable de los Combobox (es un Listbox de tk clásico)
        self.option_add("*TCombobox*Listbox.background", BG_CAMPO)
        self.option_add("*TCombobox*Listbox.foreground", FG)
        self.option_add("*TCombobox*Listbox.selectBackground", BTN)
        self.option_add("*TCombobox*Listbox.selectForeground", "#ffffff")
        self.option_add("*TCombobox*Listbox.font", F_NORMAL)

        # Base
        st.configure(".", background=BG, foreground=FG, font=F_NORMAL, bordercolor=BORDE,
                     lightcolor=BG, darkcolor=BG, troughcolor=BG_CAMPO, focuscolor=BG)
        st.configure("TFrame", background=BG)
        st.configure("TLabel", background=BG, foreground=FG, font=F_NORMAL)
        st.configure("Titulo.TLabel", font=F_TITULO)
        st.configure("Pequeno.TLabel", font=F_PEQ, foreground=FG)
        st.configure("Grande.TLabel", font=F_GRANDE)
        st.configure("Alerta.TLabel", font=(FUENTE, 13, "bold"))
        st.configure("TSeparator", background=BORDE)

        # Pestañas
        st.configure("TNotebook", background=BG, borderwidth=0, tabmargins=(0, 4, 0, 0))
        st.configure("TNotebook.Tab", background=BG_PANEL, foreground=FG, font=F_PESTANA,
                     padding=(16, 9), borderwidth=0)
        st.map("TNotebook.Tab",
               background=[("selected", BTN), ("active", BORDE)],
               foreground=[("selected", "#e0e0e0"), ("active", FG)])

        # Panel de resultados
        st.configure("TLabelframe", background=BG, bordercolor=BORDE, relief="solid", borderwidth=1)
        st.configure("TLabelframe.Label", background=BG, foreground=FG, font=(FUENTE, 13, "bold"))

        # Botones
        st.configure("TButton", background=BTN, foreground=FG, font=F_NORMAL, padding=(12, 7),
                     borderwidth=0, focuscolor=BTN, lightcolor=BTN, darkcolor=BTN)
        st.map("TButton",
               background=[("disabled", "#3d3226"), ("pressed", BTN_PRESS), ("active", BTN_HOVER)],
               foreground=[("disabled", "#7a7a7a")])
        st.configure("Accion.TButton", font=F_BOTON, padding=12)

        # Campos de entrada
        campo = dict(fieldbackground=BG_CAMPO, background=BTN, foreground=FG, arrowcolor=FG,
                     bordercolor=BORDE, lightcolor=BG_CAMPO, darkcolor=BG_CAMPO, insertcolor=FG,
                     selectbackground=BTN, selectforeground="#ffffff", padding=5)
        st.configure("TSpinbox", **campo)
        st.configure("TCombobox", **campo)
        st.map("TCombobox",
               fieldbackground=[("readonly", BG_CAMPO)], foreground=[("readonly", FG)],
               selectbackground=[("readonly", BG_CAMPO)], selectforeground=[("readonly", FG)],
               background=[("active", BTN_HOVER)], arrowcolor=[("active", "#ffffff")])
        st.map("TSpinbox", background=[("active", BTN_HOVER)], arrowcolor=[("active", "#ffffff")])

        # Deslizador del umbral
        st.configure("Horizontal.TScale", background=BG, troughcolor=BG_CAMPO, bordercolor=BORDE,
                     lightcolor=BTN, darkcolor=BTN)
        st.map("Horizontal.TScale", background=[("active", BTN_HOVER)])

        # Barras de probabilidad, una por clase
        for clase, color in COLOR_CLASE.items():
            st.configure(f"{clase}.Horizontal.TProgressbar", background=color, troughcolor=BG_CAMPO,
                         bordercolor=BORDE, lightcolor=color, darkcolor=color, thickness=22)

    # ---------------------------- interfaz --------------------------------- #
    def _construir(self) -> None:
        raiz = ttk.Frame(self, padding=16)
        raiz.pack(fill="both", expand=True)
        raiz.columnconfigure(0, weight=3)
        raiz.columnconfigure(1, weight=2)
        raiz.rowconfigure(1, weight=1)

        ttk.Label(raiz, text="Detector de deserción estudiantil", style="Titulo.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        # ---- izquierda: formulario por pestañas
        izq = ttk.Frame(raiz)
        izq.grid(row=1, column=0, sticky="nsew", padx=(0, 16))
        izq.rowconfigure(0, weight=1)
        izq.columnconfigure(0, weight=1)
        libreta = ttk.Notebook(izq)
        libreta.grid(row=0, column=0, sticky="nsew")

        marcos = {}
        for g in GRUPOS:
            if any(grupo(c) == g for c in self.info["columnas"]):
                marcos[g] = ttk.Frame(libreta, padding=18)
                marcos[g].columnconfigure(1, weight=1)
                libreta.add(marcos[g], text=g)
        filas = dict.fromkeys(marcos, 0)
        for col in self.info["columnas"]:
            g = grupo(col)
            self._crear_campo(marcos[g], filas[g], col)
            filas[g] += 1

        barra = ttk.Frame(izq)
        barra.grid(row=1, column=0, sticky="ew", pady=(12, 0))
        ttk.Label(barra, text="Cargar ejemplo:").pack(side="left")
        for nombre in EJEMPLOS:
            ttk.Button(barra, text=nombre, command=lambda n=nombre: self._cargar_ejemplo(n)).pack(side="left", padx=6)
        ttk.Button(barra, text="Restablecer", command=self._restablecer).pack(side="left", padx=6)

        # ---- derecha: resultado
        der = ttk.LabelFrame(raiz, text=" Resultado ", padding=18)
        der.grid(row=1, column=1, sticky="nsew")
        der.columnconfigure(0, weight=1)

        self.btn = ttk.Button(der, text="Cargando modelo…", style="Accion.TButton", command=self.predecir,
                              state="disabled")
        self.btn.grid(row=0, column=0, sticky="ew")

        self.lbl_clase = ttk.Label(der, text="—", style="Grande.TLabel", anchor="center")
        self.lbl_clase.grid(row=1, column=0, sticky="ew", pady=(20, 4))
        self.lbl_alerta = ttk.Label(der, text="", style="Alerta.TLabel", anchor="center", justify="center",
                                    wraplength=430)
        self.lbl_alerta.grid(row=2, column=0, sticky="ew", pady=(0, 14))

        self.barras: dict[str, tuple[ttk.Progressbar, ttk.Label]] = {}
        for i, clase in enumerate(self.info["clases"]):
            fila = ttk.Frame(der)
            fila.grid(row=3 + i, column=0, sticky="ew", pady=5)
            fila.columnconfigure(1, weight=1)
            ttk.Label(fila, text=NOMBRE_CLASE.get(clase, clase), width=18,
                      foreground=COLOR_CLASE.get(clase, FG)).grid(row=0, column=0, sticky="w")
            pb = ttk.Progressbar(fila, maximum=100, style=f"{clase}.Horizontal.TProgressbar")
            pb.grid(row=0, column=1, sticky="ew", padx=8)
            lb = ttk.Label(fila, text="—", width=6, anchor="e")
            lb.grid(row=0, column=2)
            self.barras[clase] = (pb, lb)

        n = 3 + len(self.info["clases"])
        ttk.Separator(der).grid(row=n, column=0, sticky="ew", pady=14)
        self.umbral = tk.IntVar(value=30)
        self.lbl_umbral = ttk.Label(der, text="", wraplength=430, justify="left")
        self.lbl_umbral.grid(row=n + 1, column=0, sticky="w", pady=(0, 6))
        ttk.Scale(der, from_=10, to=90, orient="horizontal", variable=self.umbral,
                  command=lambda _=None: self._actualizar_umbral()).grid(row=n + 2, column=0, sticky="ew")
        self._actualizar_umbral()

        ttk.Separator(der).grid(row=n + 3, column=0, sticky="ew", pady=14)
        ttk.Label(der, text=self._texto_metricas(), style="Pequeno.TLabel", justify="left",
                  wraplength=430).grid(row=n + 4, column=0, sticky="w")

        self.estado = ttk.Label(raiz, text="Cargando el modelo (la primera vez tarda unos segundos)…",
                                style="Pequeno.TLabel")
        self.estado.grid(row=2, column=0, columnspan=2, sticky="w", pady=(12, 0))
        self._restablecer()

    def _crear_campo(self, padre: ttk.Frame, fila: int, col: str) -> None:
        tipo = self.info["tipos"][col]
        ttk.Label(padre, text=etiqueta(col)).grid(row=fila, column=0, sticky="w", pady=7, padx=(0, 14))
        var = tk.StringVar()
        mapa = None  # texto visible -> valor real
        if tipo == "binaria":
            cero, uno = OPCIONES_BINARIAS.get(col, ("No", "Sí"))
            mapa = {cero: 0, uno: 1}
            w = ttk.Combobox(padre, textvariable=var, values=[cero, uno], state="readonly", width=24,
                             font=F_NORMAL)
        elif tipo == "nominal":
            desc = DESCRIPCIONES.get(col, {})
            mapa = {(f"{c} · {desc[c]}" if c in desc else c): c for c in self.info["categorias"][col]}
            w = ttk.Combobox(padre, textvariable=var, values=list(mapa), state="readonly", width=60,
                             font=F_NORMAL)
        else:
            lo, hi = self.info["rangos"][col]
            decimal = not (float(lo).is_integer() and float(hi).is_integer()) or col.endswith("_grade")
            w = ttk.Spinbox(padre, textvariable=var, from_=lo, to=hi, increment=0.5 if decimal else 1, width=12,
                            font=F_NORMAL)
            ttk.Label(padre, text=f"rango {lo:g} a {hi:g}", style="Pequeno.TLabel").grid(
                row=fila, column=2, sticky="w", padx=(12, 0))
        w.grid(row=fila, column=1, sticky="w")
        self.campos[col] = {"var": var, "tipo": tipo, "mapa": mapa}

    def _texto_metricas(self) -> str:
        i = self.info
        cv, pr, ic = i.get("validacion_cruzada", {}), i.get("prueba", {}), i.get("prueba_ic95", {})
        r = ic.get("Recall Dropout")
        rango = f" (IC 95 %: {r[0]:.2f}–{r[1]:.2f})" if r else ""
        return (f"Modelo: {i.get('algoritmo', '?')} (Random Forest + SMOTE)\n"
                f"Recall de deserción en prueba: {pr.get('Recall Dropout', '?')}{rango}\n"
                f"F1 macro: CV {cv.get('F1 Macro', '?')} · prueba {pr.get('F1 Macro', '?')}\n"
                "La clase «Sigue matriculado» es la menos fiable (recall ≈ 45 %).\n"
                "Herramienta de apoyo: no reemplaza la valoración de un profesional.")

    # ---------------------------- valores ---------------------------------- #
    def _poner(self, col: str, valor) -> None:
        c = self.campos[col]
        if c["mapa"] is not None:
            for texto, real in c["mapa"].items():
                if str(real) == str(valor):
                    c["var"].set(texto)
                    return
            c["var"].set(next(iter(c["mapa"])))
        else:
            lo, hi = self.info["rangos"][col]
            c["var"].set(f"{min(max(float(valor), lo), hi):g}")

    def _restablecer(self) -> None:
        for col, c in self.campos.items():
            if col in DEFECTOS:
                self._poner(col, DEFECTOS[col])
            elif c["tipo"] == "binaria":
                self._poner(col, 0)
            elif c["tipo"] == "nominal":
                cats = self.info["categorias"][col]
                self._poner(col, "1" if "1" in cats else cats[0])
            else:
                self._poner(col, self.info["rangos"][col][0])

    def _cargar_ejemplo(self, nombre: str) -> None:
        self._restablecer()
        for col, valor in EJEMPLOS[nombre].items():
            if col in self.campos:
                self._poner(col, valor)

    def _leer_fila(self) -> tuple[dict, list[str]]:
        """Convierte el formulario en una fila cruda (como la que recibe el modelo)."""
        fila, fuera = {}, []
        for col in self.info["columnas"]:
            c = self.campos[col]
            texto = c["var"].get().strip()
            if c["mapa"] is not None:
                if texto not in c["mapa"]:
                    raise ValueError(f"Selecciona un valor para «{etiqueta(col)}».")
                real = c["mapa"][texto]
                fila[col] = str(real) if c["tipo"] == "nominal" else int(real)
            else:
                try:
                    num = float(texto.replace(",", "."))
                except ValueError:
                    raise ValueError(f"«{etiqueta(col)}» debe ser un número.") from None
                lo, hi = self.info["rangos"][col]
                # El Spinbox redondea a 1 decimal (18.875 -> 18.9): se tolera ese redondeo
                tol = 0.0 if float(lo).is_integer() and float(hi).is_integer() else 0.051
                if not (lo - tol <= num <= hi + tol):
                    fuera.append(f"{etiqueta(col)} = {num:g} (rango {lo:g} a {hi:g})")
                fila[col] = int(num) if float(lo).is_integer() and float(hi).is_integer() and num.is_integer() else num
        return fila, fuera

    # ---------------------------- modelo ----------------------------------- #
    def _cargar_modelo_en_segundo_plano(self) -> None:
        def tarea() -> None:
            try:
                from pycaret.classification import load_model  # import lento: fuera del hilo de la interfaz
                self._cola_carga["modelo"] = load_model(str(self.carpeta / self.nombre_modelo), verbose=False)
            except Exception as e:  # noqa: BLE001
                self._cola_carga["error"] = e

        threading.Thread(target=tarea, daemon=True).start()
        self._esperar_modelo()

    def _esperar_modelo(self) -> None:
        if "modelo" in self._cola_carga:
            self.modelo = self._cola_carga["modelo"]
            self.btn.config(text="Predecir", state="normal")
            self.estado.config(text=f"Modelo cargado: {self.nombre_modelo} · {datetime.now():%Y-%m-%d %H:%M}")
        elif "error" in self._cola_carga:
            self.btn.config(text="Modelo no disponible")
            self.estado.config(text="Error al cargar el modelo.")
            messagebox.showerror("Error al cargar el modelo", str(self._cola_carga["error"]))
        else:
            self.after(200, self._esperar_modelo)

    def predecir(self) -> None:
        import pandas as pd
        from pycaret.classification import predict_model

        try:
            fila, fuera = self._leer_fila()
        except ValueError as e:
            messagebox.showwarning("Revisa el formulario", str(e))
            return
        if fuera and not messagebox.askokcancel(
                "Valores fuera del rango de entrenamiento",
                "Estos valores no aparecen en los datos con que se entrenó el modelo; "
                "la predicción puede no ser fiable:\n\n- " + "\n- ".join(fuera) + "\n\n¿Predecir de todos modos?"):
            return

        datos = pd.DataFrame([fila], columns=self.info["columnas"])
        try:
            res = predict_model(self.modelo, data=datos, raw_score=True, verbose=False)
        except Exception as e:  # noqa: BLE001
            messagebox.showerror("Error al predecir", str(e))
            return

        probs = {c: float(res[f"prediction_score_{c}"].iloc[0]) for c in self.info["clases"]}
        clase = str(res["prediction_label"].iloc[0])
        self._mostrar(clase, probs)

    # ---------------------------- resultado -------------------------------- #
    def _actualizar_umbral(self) -> None:
        self.lbl_umbral.config(text=f"Umbral de alerta: marcar riesgo si P(deserción) ≥ {self.umbral.get()} %")
        if getattr(self, "_ultimas_probs", None):
            self._pintar_alerta()

    def _mostrar(self, clase: str, probs: dict[str, float]) -> None:
        self._ultimas_probs, self._ultima_clase = probs, clase
        self.lbl_clase.config(text=NOMBRE_CLASE.get(clase, clase), foreground=COLOR_CLASE.get(clase, FG))
        for c, (pb, lb) in self.barras.items():
            pb["value"] = probs[c] * 100
            lb.config(text=f"{probs[c] * 100:.0f} %")
        self._pintar_alerta()

    def _pintar_alerta(self) -> None:
        p = self._ultimas_probs.get("Dropout", 0.0) * 100
        if p >= self.umbral.get():
            texto = f"⚠ ALERTA: probabilidad de deserción {p:.0f} % (umbral {self.umbral.get()} %)"
            color = COLOR_CLASE["Dropout"]
        else:
            texto = f"Sin alerta: probabilidad de deserción {p:.0f} % (umbral {self.umbral.get()} %)"
            color = COLOR_SIN_ALERTA
        if self._ultima_clase == "Enrolled":
            texto += "\nOjo: «Sigue matriculado» es la clase menos fiable del modelo."
        self.lbl_alerta.config(text=texto, foreground=color)


def main() -> None:
    App().mainloop()


if __name__ == "__main__":
    main()
"""Carga el modelo de PyCaret y hace predicciones. No sabe nada de la interfaz.

Funciona igual en desarrollo (uv run app) y dentro del ejecutable de PyInstaller.
"""

import json
import os
import sys
from pathlib import Path

import pandas as pd

# Las 34 variables de entrada, en el mismo orden que usa el cuaderno de entrenamiento.
COLUMNAS = [
    "Marital_status", "Application_mode", "Application_order", "Course",
    "Daytime_attendance", "Previous_qualification", "Nationality",
    "Mothers_qualification", "Fathers_qualification", "Mothers_occupation",
    "Fathers_occupation", "Displaced", "Educational_special_needs", "Debtor",
    "Tuition_fees_up_to_date", "Gender", "Scholarship_holder", "Age_at_enrollment",
    "International", "CU1_credited", "CU1_enrolled", "CU1_evaluations",
    "CU1_approved", "CU1_grade", "CU1_no_evals", "CU2_credited", "CU2_enrolled",
    "CU2_evaluations", "CU2_approved", "CU2_grade", "CU2_no_evals",
    "Unemployment_rate", "Inflation_rate", "GDP",
]
CLASES = ["Dropout", "Enrolled", "Graduate"]
NOMBRE_MODELO = "modelo_desercion"  # PyCaret le agrega la extensión .pkl


def carpeta_base() -> Path:
    """Carpeta donde están los recursos (modelo/, assets/).

    - En el ejecutable, PyInstaller los descomprime en sys._MEIPASS.
    - En desarrollo, es la raíz del proyecto (dos carpetas arriba de este archivo).
    """
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[2]


CARPETA_MODELO = carpeta_base() / "modelo"
CARPETA_ASSETS = carpeta_base() / "assets"

# PyCaret escribe un archivo logs.log en la carpeta actual. Instalada en
# C:\Program Files no hay permiso de escritura, así que en el ejecutable lo
# mandamos a la carpeta del usuario: %LOCALAPPDATA%\ClasificadorDesertores\logs.log
if getattr(sys, "frozen", False) and "PYCARET_CUSTOM_LOGGING_PATH" not in os.environ:
    carpeta_logs = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "ClasificadorDesertores"
    carpeta_logs.mkdir(parents=True, exist_ok=True)
    os.environ["PYCARET_CUSTOM_LOGGING_PATH"] = str(carpeta_logs / "logs.log")

_modelo = None


def cargar_modelo():
    """Carga el modelo una sola vez (la primera vez tarda porque importa PyCaret)."""
    global _modelo
    if _modelo is None:
        ruta = CARPETA_MODELO / f"{NOMBRE_MODELO}.pkl"
        if not ruta.exists():
            raise FileNotFoundError(
                "No encontré el modelo. Ejecuta primero el cuaderno "
                "notebooks/Estudiantes_entrenamiento_pycaret.ipynb"
            )
        from pycaret.classification import load_model

        _modelo = load_model(str(ruta.with_suffix("")), verbose=False)
    return _modelo


def leer_metricas() -> dict:
    ruta = CARPETA_MODELO / "metricas.json"
    if ruta.exists():
        return json.loads(ruta.read_text(encoding="utf-8"))
    return {}


def predecir_estudiante(valores: dict):
    """Devuelve (clase, {clase: probabilidad}) para un estudiante.

    `valores` es un diccionario {nombre_de_columna: valor} con las 34 variables.
    Los tipos se toman de metricas.json: las nominales van como texto (igual que
    en el entrenamiento), las binarias y la ordinal como enteros y el resto como float.
    """
    from pycaret.classification import predict_model

    metricas = leer_metricas()
    if "tipos" not in metricas:
        raise RuntimeError(
            "metricas.json no tiene la clave 'tipos'. Vuelve a ejecutar en el cuaderno "
            "la celda que actualiza metricas.json."
        )
    tipos = metricas["tipos"]
    columnas = metricas.get("columnas", COLUMNAS)

    fila = {}
    for c in columnas:
        v = valores[c]
        if tipos[c] == "nominal":
            fila[c] = str(int(float(v)))      # códigos como texto: "17", no 17.0
        elif tipos[c] in ("binaria", "ordinal"):
            fila[c] = int(float(v))
        else:
            fila[c] = float(v)

    datos = pd.DataFrame([fila], columns=columnas)
    resultado = predict_model(cargar_modelo(), data=datos, raw_score=True, verbose=False)
    fila_res = resultado.iloc[0]

    clase = str(fila_res["prediction_label"])
    probabilidades = {
        col.removeprefix("prediction_score_"): float(fila_res[col])
        for col in resultado.columns
        if col.startswith("prediction_score_")
    }
    return clase, probabilidades

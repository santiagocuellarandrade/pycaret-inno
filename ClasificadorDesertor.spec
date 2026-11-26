# Receta de PyInstaller para crear el ejecutable de la app.
#
# Uso (desde la raíz del proyecto):   uv run pyinstaller ClasificadorDesertor.spec --noconfirm
# Resultado:                          dist/ClasificadorDesertor/ClasificadorDesertor.exe
#
# Usamos el modo "carpeta" (onedir) y no --onefile: con PyCaret el .exe único
# tarda mucho en abrir porque cada vez descomprime cientos de MB. Inno Setup
# luego empaqueta toda la carpeta en un solo instalador.

from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_data_files, copy_metadata

NOMBRE = "ClasificadorDesertor"
ICONO = Path("assets/icono.ico")

# Archivos que el ejecutable necesita: el modelo entrenado y el icono
datas = [("modelo", "modelo")]
if ICONO.exists():
    datas.append((str(ICONO), "assets"))
else:
    print(f"\n⚠️  No encontré {ICONO}: el ejecutable quedará con el icono por defecto.\n")

binaries = []
hiddenimports = []

# PyCaret carga muchos módulos de forma "dinámica" (PyInstaller no los ve solo):
# los incluimos todos, con sus archivos de datos.
for paquete in ["pycaret"]:
    d, b, h = collect_all(paquete)
    datas += d
    binaries += b
    hiddenimports += h

# Archivos de datos que algunas librerías leen al importarse
datas += collect_data_files("imblearn")       # imblearn/VERSION.txt
datas += collect_data_files("customtkinter")  # temas y fuentes de CustomTkinter

# PyCaret revisa las versiones instaladas de sus dependencias
for paquete in ["pycaret", "scikit-learn", "pandas", "numpy", "scipy", "joblib",
                "imbalanced-learn", "category-encoders", "lightgbm", "xgboost"]:
    try:
        datas += copy_metadata(paquete)
    except Exception:
        pass

a = Analysis(
    ["src/clasificador_desertores/app.py"],
    pathex=["src"],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    excludes=["ipykernel", "jupyter_client", "notebook", "jupyterlab"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=NOMBRE,
    console=False,  # sin ventana negra de consola (equivale a --windowed)
    icon=str(ICONO) if ICONO.exists() else None,
)

coll = COLLECT(exe, a.binaries, a.datas, name=NOMBRE)

# En Mac, además, empaquetamos la carpeta como una app .app
import sys  # noqa: E402

if sys.platform == "darwin":
    app = BUNDLE(coll, name=f"{NOMBRE}.app", bundle_identifier="co.edu.clasificadordesertor")

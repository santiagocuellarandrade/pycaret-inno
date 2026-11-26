# 🌸 De PyCaret a instalador de Windows: clasificador de flores Iris

Entrenamos un modelo con **PyCaret**, lo exportamos y lo usamos en una **app de escritorio
profesional** hecha con **CustomTkinter**. Al final la convertimos en un programa de Windows
de verdad: un `.exe` con **PyInstaller** y un instalador `Setup.exe` con **Inno Setup**.

```
 cuaderno (PyCaret) ──► modelo_iris.pkl ──► app (CustomTkinter) ──► .exe (PyInstaller) ──► Setup.exe (Inno Setup)
```

El entrenamiento es una **fase exploratoria**: se hace en un cuaderno de Jupyter, donde miramos
los datos, comparamos modelos, escogemos uno y lo exportamos. La app usa el modelo que exporte el cuaderno.

> 💡 **Idea clave:** el modelo (`core.py`) está separado de la interfaz (`app.py`).
> La app solo lee las medidas que escoge el usuario, llama a `predecir_especie()` y muestra el resultado.

---

## 🚀 Paso a paso desde cero

### Lo que necesitas

- **Windows 10 u 11** (64 bits).
- **uv** instalado. Para comprobarlo, abre PowerShell y escribe `uv --version`. Si no lo tienes:

  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

  Cierra PowerShell y ábrelo de nuevo después de instalarlo.
- **Inno Setup 6** (solo para el paso 9): descárgalo de <https://jrsoftware.org/isdl.php>.
- Los archivos que te entregó el profesor:
  - `requirements.txt`, `license.txt`, `ClasificadorIris.spec` y `construir.ps1`
  - los **3 archivos `.py`** de la carpeta `src/clasificador_desertores/`
  - la carpeta `notebooks/` (con `entrenamiento_pycaret.ipynb`)
  - la carpeta `instalador/` (con `ClasificadorIris.iss`)
  - (opcional) la carpeta `legacy/`
- **VS Code** con las extensiones *Python* y *Jupyter* (para el cuaderno).

No necesitas descargar Python desde python.org: uv se encarga de eso.

---

### Paso 0 · Instalar Python 3.10 con uv

```powershell
uv python install 3.10
```

> ⚠️ **¿Por qué 3.10 y no la última versión?** PyCaret 3.3 solo funciona con Python 3.9, 3.10 y 3.11.
> Con 3.12 o superior la instalación falla.

---

### Paso 1 · Crear el proyecto

Abre PowerShell en la carpeta donde quieras guardar el proyecto (por ejemplo, Documentos) y escribe:

```powershell
uv init clasificador-desertores --package --python 3.10
cd clasificador-desertores
```

`--package` hace que uv cree la carpeta `src/clasificador_desertores/`. **Todos los pasos siguientes
se hacen desde dentro de `clasificador-desertores`.**

> ⚠️ Escribe el nombre **exactamente igual**: `clasificador-desertores`. El código depende de que la
> carpeta se llame `src/clasificador_desertores` (con guion bajo).
>
> ⚠️ **Nunca** llames al proyecto `pycaret`: Python confundiría tu proyecto con la librería.

---

### Paso 2 · Instalar las librerías

Copia `requirements.txt` dentro de `clasificador-desertores/` (junto a `pyproject.toml`) y escribe:

```powershell
uv add -r requirements.txt
uv add --dev pyinstaller ipykernel
```

El primero instala PyCaret y CustomTkinter (tarda unos minutos: PyCaret es grande).
El segundo instala herramientas que solo se usan al desarrollar: PyInstaller (para crear el `.exe`)
e ipykernel (para usar el notebook en VS Code).

---

### Paso 3 · Copiar el código y los archivos

Copia los archivos a estas ubicaciones. Cuando te pregunte si quieres reemplazar `__init__.py`, responde **sí**:

```
clasificador-desertores/
├── ClasificadorIris.spec        ← receta de PyInstaller
├── construir.ps1                ← hace los pasos 8 y 9 de una vez
├── license.txt                  ← licencia que muestra el instalador
├── instalador/
│   └── ClasificadorIris.iss     ← receta de Inno Setup
├── notebooks/
│   └── entrenamiento_pycaret.ipynb   ← explora, entrena y exporta el modelo
└── src/clasificador_desertores/
    ├── __init__.py
    ├── core.py                  ← carga el modelo y predice
    └── app.py                   ← la app de escritorio
```

---

### Paso 4 · Registrar los comandos en `pyproject.toml`

Abre `pyproject.toml` y busca estas líneas que creó uv:

```toml
[project.scripts]
clasificador-desertores = "clasificador_desertores:main"
```

y **reemplázalas** por estas:

```toml
[project.scripts]
app = "clasificador_desertores.app:main"
```

Guarda el archivo. A la izquierda va el nombre del comando (`uv run app`) y a la derecha
la función de Python que ejecuta. Después escribe `uv sync` para que uv registre el cambio.

> ⚠️ Este es el paso que más se olvida. Si te sale `Failed to spawn: app`, revisa este paso.

---

### Paso 5 · Explorar, entrenar y exportar el modelo (cuaderno) 📓

1. Abre la carpeta `clasificador-desertores` en VS Code.
2. Abre `notebooks/entrenamiento_pycaret.ipynb`.
3. Arriba a la derecha, en **Select Kernel**, escoge el Python de `.venv`.
4. Ejecuta las celdas **en orden** (o *Run All*).

El cuaderno:

| Paso | Qué hace |
|---|---|
| 2–3 | Carga Iris y lo explora: conteos, estadísticas y gráficas por especie |
| 4 | `setup()`: separa 70 % entrenamiento / 30 % prueba |
| 5 | `compare_models()`: entrena unos 15 algoritmos y los ordena por accuracy |
| 6 | Mira los mejores: matriz de confusión, fronteras de decisión, `tune_model()` |
| 7 | ✋ **Tú escoges** el modelo a exportar (`modelo_elegido = ...`) |
| 8 | Lo evalúa con los datos de prueba |
| 9 | `finalize_model()` + `save_model()`: lo **exporta** a la carpeta `modelo/` |
| 10 | Lo carga como lo hace la app y prueba tres flores |

Al final aparece la carpeta `modelo/` en la raíz del proyecto con dos archivos:

- `modelo_iris.pkl` → el modelo exportado (el pipeline completo de PyCaret).
- `metricas.json` → algoritmo, accuracy y F1 en prueba, y rangos de las medidas (los muestra la app).

> 💡 El cuaderno importa `CARPETA_MODELO` y `NOMBRE_MODELO` desde `core.py`. Así el cuaderno
> guarda el modelo exactamente donde la app lo va a buscar, sin escribir rutas a mano.

---

### Paso 6 · Abrir la app 🎉

```powershell
uv run app
```

La ventana aparece de inmediato y abajo dice *"Cargando el modelo de PyCaret…"* durante unos
segundos (PyCaret es pesado y se carga en segundo plano para que la ventana no se congele).
Luego puedes:

- mover los controles o escribir las medidas: la predicción se actualiza sola,
- probar los ejemplos de la izquierda (setosa, versicolor, virginica),
- ver la probabilidad de cada especie,
- cambiar entre modo claro y oscuro.

---

### Paso 7 · Poner el icono

Crea un icono en formato `.ico` (por ejemplo en <https://www.icoconverter.com/> a partir de un PNG,
con los tamaños 16, 32, 48 y 256) y guárdalo exactamente aquí:

```
clasificador-desertores/assets/icono.ico
```

Lo usan tres cosas: la ventana de la app, el `.exe` y el instalador.

---

### Paso 8 · Crear el ejecutable con PyInstaller

```powershell
uv run pyinstaller ClasificadorIris.spec --noconfirm
```

Tarda unos minutos. El resultado queda en:

```
dist/ClasificadorIris/
├── ClasificadorIris.exe     ← doble clic para probar
└── _internal/               ← Python, PyCaret, el modelo... (no se toca)
```

Haz doble clic en `ClasificadorIris.exe` para comprobar que funciona **antes** de crear el instalador.

> **¿Por qué una carpeta y no un solo `.exe` (`--onefile`)?** Con `--onefile`, cada vez que abres
> el programa Windows descomprime cientos de MB de PyCaret en una carpeta temporal: tarda mucho
> en abrir. Con la carpeta abre rápido, e Inno Setup igual la empaqueta en un solo instalador.
>
> **¿Por qué un archivo `.spec` y no un comando largo?** PyCaret carga muchos módulos de forma
> "escondida" que PyInstaller no detecta solo. El `.spec` es un archivo de Python donde le decimos
> qué incluir; ábrelo, está comentado.

---

### Paso 9 · Crear el instalador con Inno Setup

1. Abre **Inno Setup Compiler**.
2. *File → Open* → `instalador/ClasificadorIris.iss`.
3. *Build → Compile* (o **Ctrl + F9**).

El instalador queda en `instalador/salida/ClasificadorIris_Setup_1.0.0.exe`. Ese único archivo es
el que compartes: cualquiera lo instala con doble clic, **sin tener Python ni uv**.
El instalador está en español, muestra la licencia, crea el acceso en el menú Inicio (y en el
escritorio si el usuario quiere) y aparece en *Agregar o quitar programas* para desinstalarlo.

> 💡 **Atajo:** cuando ya exportaste el modelo con el cuaderno, el script `construir.ps1` hace los
> pasos 8 y 9 seguidos:
>
> ```powershell
> powershell -ExecutionPolicy Bypass -File construir.ps1
> ```

> 🛡️ Al abrir el instalador en otro PC, Windows puede mostrar *"Windows protegió su PC"*. Es normal
> porque el programa no tiene firma digital (cuesta dinero): clic en **Más información → Ejecutar de todas formas**.

---

## 🔁 ¿Qué repetir cuando cambio algo?

| Cambié... | Repetir |
|---|---|
| Los datos o el modelo escogido en el cuaderno | Paso 5 (cuaderno) → 8 → 9 |
| Solo la interfaz (`app.py`) | Paso 8 → 9 |
| El icono, la licencia o la versión | Paso 8 → 9 |

Para una nueva versión cambia `MyAppVersion` en `instalador/ClasificadorIris.iss` y `APP_VERSION`
en `app.py`. **No** cambies el `AppId`: así Windows actualiza la versión anterior en vez de instalar otra copia.

---

## Así queda el proyecto al final

```
clasificador-desertores/
├── pyproject.toml              ← nombre, librerías y comandos del proyecto
├── uv.lock                     ← versiones exactas (lo crea uv, no se edita)
├── requirements.txt
├── .python-version             ← 3.10
├── .venv/                      ← entorno virtual (lo crea uv)
├── ClasificadorIris.spec       ← receta de PyInstaller
├── construir.ps1               ← construye todo de una vez
├── license.txt
├── assets/icono.ico            ← lo pones tú (paso 7)
├── notebooks/entrenamiento_pycaret.ipynb   ← fase exploratoria
├── modelo/                     ← lo exporta el cuaderno (paso 5)
│   ├── modelo_iris.pkl
│   └── metricas.json
├── src/clasificador_desertores/      ← el código
├── build/                      ← temporal de PyInstaller (se puede borrar)
├── dist/ClasificadorIris/      ← lo crea el paso 8
└── instalador/
    ├── ClasificadorIris.iss
    └── salida/ClasificadorIris_Setup_1.0.0.exe   ← lo crea el paso 9
```

---

## 🆘 Errores comunes

| Mensaje | Qué pasó | Solución |
|---|---|---|
| `Failed to spawn: app` | No se registró el comando | Revisa el **paso 4**, guarda `pyproject.toml` y ejecuta `uv sync` |
| `No encontré el modelo. Ejecuta primero el cuaderno…` | No se ha exportado el modelo | Ejecuta el cuaderno completo (**paso 5**), incluido el paso 9 del cuaderno |
| Cuaderno: `No module named 'pycaret'` o `'clasificador_desertores'` | VS Code usa otro Python | En **Select Kernel** escoge el de `.venv` |
| Cuaderno: `name 'top3' is not defined` (o similar) | Se ejecutó una celda sin las anteriores | *Restart* el kernel y *Run All* |
| `No solution found when resolving dependencies` al instalar PyCaret | El proyecto se creó con otro Python | Revisa que `.python-version` diga `3.10`. Si no, repite el **paso 1** con `--python 3.10` |
| `ModuleNotFoundError: No module named 'clasificador_desertores'` | El proyecto tiene otro nombre o los archivos están en otra carpeta | Revisa los **pasos 1 y 3** |
| El `.exe` no abre o se cierra sin decir nada | Falta algo dentro del ejecutable | Cambia `console=False` por `console=True` en el `.spec`, repite el paso 8 y abre el `.exe` desde PowerShell para ver el error |
| Inno Setup: `Source file ... does not exist` | No hiciste el paso 8, o falta `assets\icono.ico` | Paso 7 y paso 8 |
| Inno Setup: `Couldn't open include file "...Spanish.isl"` | Se instaló Inno Setup sin idiomas | Reinstala Inno Setup marcando los idiomas, o borra la línea `spanish` en `[Languages]` |

### Si estás en Mac

Todo funciona igual, salvo que el **paso 9 (Inno Setup) es solo para Windows**. Además:

- PyCaret usa LightGBM, que en Mac necesita una librería extra. Si `setup()` falla en el cuaderno con
  `Library not loaded: @rpath/libomp.dylib`, instálala con [Homebrew](https://brew.sh): `brew install libomp`.
- Para el paso 8 necesitas las herramientas de desarrollo: `xcode-select --install`. El resultado
  es `dist/ClasificadorIris.app`.
- Cada sistema operativo compila su propio ejecutable: en Mac **no** se puede crear el `.exe` de Windows.

---

## (Opcional) Ver la versión anterior: `legacy/`

La carpeta `legacy/` tiene la primera versión: Tkinter clásico, la ruta del modelo escrita a mano
(`/Users/raldo/Desktop/...`) y PyInstaller con `--onefile`. Sirve para comparar el antes y el después:

| Antes (`legacy/`) | Ahora |
|---|---|
| Rutas absolutas: solo funcionaba en un PC | Rutas relativas: funciona en cualquier PC |
| Etiquetas `0, 1, 2` | Nombres de especie |
| Solo la clase predicha | Clase + probabilidad de cada especie |
| La ventana se congela mientras carga PyCaret | El modelo carga en segundo plano |
| Tkinter clásico | CustomTkinter, modo claro/oscuro |
| `--onefile` (abre lento) | Carpeta + instalador de Inno Setup |

---

## Comandos útiles de uv

| Comando | Para qué sirve |
|---|---|
| `uv python install 3.10` | Instala Python 3.10 |
| `uv add customtkinter` | Instala una librería y la anota en `pyproject.toml` |
| `uv add -r requirements.txt` | Instala todas las librerías de un archivo |
| `uv add --dev pyinstaller` | Instala una librería que solo se usa al desarrollar |
| `uv remove customtkinter` | Desinstala una librería |
| `uv sync` | Deja el entorno igual a lo que dice `uv.lock` (útil al recibir un proyecto ya hecho) |
| `uv run <comando>` | Ejecuta algo dentro del entorno del proyecto, sin activarlo a mano |

---

## Ideas de ejercicios

1. En el cuaderno, exporta otro modelo (`modelo_elegido = arbol` o `ajustado`), abre la app y compara las probabilidades.
2. Agrega un botón **"Guardar resultado"** que escriba la predicción en un archivo CSV.
3. Cambia los colores de cada especie en el diccionario `ESPECIES` de `app.py`.
4. Agrega una pestaña que cargue un CSV con muchas flores y las clasifique todas (`predict_model` acepta un DataFrame completo).
5. Adapta todo a otro dataset de clasificación (vinos, cáncer de mama, Titanic…): cambia la carga de datos del cuaderno, `COLUMNAS` en `core.py` y las etiquetas de la app.

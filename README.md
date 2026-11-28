# 🎓 De PyCaret a instalador de Windows: Clasificador de deserción estudiantil

Entrenamos un modelo con **PyCaret** para predecir si un estudiante universitario va a **desertar**,
seguirá **matriculado** o se **graduará**. Lo exportamos y lo usamos en una **app de escritorio
profesional** hecha con **CustomTkinter**. Al final la convertimos en un programa de Windows
de verdad: un `.exe` con **PyInstaller** y un instalador `Setup.exe` con **Inno Setup**.

```
 cuaderno (PyCaret) ──► modelo_desercion.pkl ──► app (CustomTkinter) ──► .exe (PyInstaller) ──► Setup.exe (Inno Setup)
```

El entrenamiento es una **fase exploratoria**: se hace en un cuaderno de Jupyter, donde miramos
los datos, comparamos preprocesamientos y modelos, escogemos uno, calibramos sus probabilidades y lo exportamos.
La app usa el modelo que exporte el cuaderno.

> 💡 **Idea clave:** el modelo (`core.py`) está separado de la interfaz (`app.py`).
> La app solo lee los datos del estudiante que escribe el usuario, llama a `predecir_estudiante()` y muestra
> la clase más probable y la probabilidad de cada resultado.

---

## 📊 El problema y los datos

- **Tarea:** clasificación multiclase. Para cada estudiante se predice una de tres clases:
  `Dropout` (deserta), `Enrolled` (sigue matriculado) o `Graduate` (se gradúa) al final de la duración normal del programa.
- **Datos:** dataset público de Realinho et al. (*Predict students' dropout and academic success*, repositorio UCI, id 697):
  **4.424 estudiantes** de un instituto politécnico de Portugal y **34 variables de entrada** (demográficas,
  socioeconómicas, académicas de ingreso, rendimiento del 1.er y 2.º semestre, y macroeconómicas).
- **Distribución de la clase objetivo:** Graduate 49,9 %, Dropout 32,1 %, Enrolled 17,9 %. Está **desbalanceada**,
  por eso se usa **SMOTE** (dentro de cada fold de la validación cruzada, para no filtrar datos) y métricas como
  macro F1, balanced accuracy y *recall* de Dropout (la clase que un sistema de alerta temprana no puede dejar pasar).
- **Modelo final:** Random Forest + SMOTE + calibración sigmoide de probabilidades.
  En el 20 % de prueba (885 estudiantes): macro F1 ≈ 0,715 y *recall* de Dropout ≈ 0,764.

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
  - `requirements.txt`, `license.txt`, `ClasificadorDesertor.spec` y `construir.ps1`
  - los **3 archivos `.py`** de la carpeta `src/clasificador_desertores/`
  - la carpeta `notebooks/` (con `Estudiantes_entrenamiento_pycaret.ipynb`)
  - la carpeta `instalador/` (con `ClasificadorDesertor.iss`)
  - (opcional) la carpeta `legacy/`
- **VS Code** con las extensiones *Python* y *Jupyter* (para el cuaderno).
- **Conexión a internet** la primera vez que ejecutes el cuaderno (descarga el dataset del repositorio UCI).

No necesitas descargar Python desde python.org: uv se encarga de eso.

---

### Paso 0 · Instalar Python 3.10 con uv

```powershell
uv python install 3.10
```

---

### Paso 1 · Obtener el proyecto

**Opción A (recomendada): clonar el repositorio.** Ya trae el código, el cuaderno, el modelo y el icono:

```powershell
git clone https://github.com/santiagocuellarandrade/pycaret-inno.git
cd pycaret-inno
uv sync
```

`uv sync` crea la carpeta `.venv` e instala todas las librerías. Con esto puedes saltar al **paso 5** (o al 6 si
no quieres reentrenar, porque `modelo/` ya viene con el modelo exportado).

**Opción B: crear el proyecto desde cero.**

```powershell
uv init pycaret-inno --package --name clasificador-desertores --python 3.10
cd pycaret-inno
```

- `pycaret-inno` es la **carpeta** del proyecto; todos los pasos siguientes se hacen desde dentro de ella.
- `--package` crea la carpeta `src/`, y `--name clasificador-desertores` hace que el paquete de Python se llame
  `clasificador_desertores`, que es el nombre que usa el código.

---

### Paso 2 · Instalar las librerías

(Solo en la opción B; con la opción A ya lo hizo `uv sync`.) Copia `requirements.txt` dentro de `pycaret-inno/` (junto a `pyproject.toml`) y escribe:

```powershell
uv add -r requirements.txt
uv add --dev pyinstaller ipykernel
```

El primero instala PyCaret, CustomTkinter, seaborn y ucimlrepo (tarda unos minutos: PyCaret es grande).
El segundo instala herramientas que solo se usan al desarrollar: PyInstaller (para crear el `.exe`)
e ipykernel (para usar el notebook en VS Code).

---

### Paso 3 · Copiar el código y los archivos

(Solo en la opción B.) Copia los archivos a estas ubicaciones. Cuando te pregunte si quieres reemplazar `__init__.py`, responde **sí**:

```
pycaret-inno/
├── ClasificadorDesertor.spec    ← receta de PyInstaller
├── construir.ps1                ← hace los pasos 8 y 9 de una vez
├── license.txt                  ← licencia que muestra el instalador
├── instalador/
│   └── ClasificadorDesertor.iss     ← receta de Inno Setup
├── notebooks/
│   └── Estudiantes_entrenamiento_pycaret.ipynb   ← explora, entrena, calibra y exporta el modelo
└── src/clasificador_desertores/
    ├── __init__.py
    ├── core.py                  ← carga el modelo y predice
    └── app.py                   ← la app de escritorio
```

---

### Paso 4 · Registrar los comandos en `pyproject.toml`

(Solo en la opción B; en el repositorio ya está hecho.)

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
la función de Python que ejecuta. Además, agrega estas líneas para que uv use el paquete correcto:

```toml
[tool.uv.build-backend]
module-name = "clasificador_desertores"
```

Después escribe `uv sync` para que uv registre el cambio.

---

### Paso 5 · Explorar, entrenar y exportar el modelo (cuaderno) 📓

1. Abre la carpeta `pycaret-inno` en VS Code.
2. Abre `notebooks/Estudiantes_entrenamiento_pycaret.ipynb`.
3. Arriba a la derecha, en **Select Kernel**, escoge el Python de `.venv`.
4. Ejecuta las celdas **en orden** (o *Run All*).

El cuaderno:

| Paso | Qué hace |
|---|---|
| 1 | Importa las librerías |
| 2 | Descarga el dataset (UCI id 697), estandariza los nombres de columnas, quita `Previous_qualification_grade` y `Admission_grade` y verifica nulos y duplicados |
| 3 | Explora los datos: distribución de la clase objetivo, estadísticas, promedios por clase y gráficas |
| 4 | Preprocesamiento y partición 80 % entrenamiento / 20 % prueba; compara variantes (estandarización, Yeo-Johnson, PCA, SMOTE) |
| 5 | `compare_models()` y tabla de decisión con validación cruzada y SMOTE dentro de cada fold |
| 6 | Explora los mejores modelos: hiperparámetros, matriz de confusión, ajuste y calibración de probabilidades |
| 7 | ✋ **Escoges** el modelo a exportar (`modelo_elegido = ...`; el proyecto usa Random Forest) |
| 8 | Evalúa con los datos de prueba: métricas e intervalos de confianza (bootstrap) |
| 9 | **Exporta** el modelo a la carpeta `modelo/` y completa `metricas.json` |
| 10 | Carga el modelo como lo hace la app y prueba tres estudiantes |

Al final del cuaderno hay un mensaje **"Listo. Ahora abre la app en la terminal"**.

Al final aparece la carpeta `modelo/` en la raíz del proyecto con dos archivos:

- `modelo_desercion.pkl` → el modelo exportado (el pipeline completo de PyCaret: preprocesamiento + Random Forest + calibración).
- `metricas.json` → algoritmo, métricas de validación cruzada y de prueba (con sus intervalos de confianza), las 34 columnas de entrada, las clases, el tipo de cada variable, las categorías de las nominales y el rango de cada variable (los usa la app).

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

- llenar los datos del estudiante en las **seis pestañas** (1.er semestre, 2.º semestre, Ingreso,
  Perfil personal, Situación económica y Contexto del país); cada campo muestra su rango válido,
- cargar los **ejemplos** de abajo (perfil de riesgo bajo y de riesgo alto) para probar rápido,
- presionar **Predecir** y ver en el panel derecho la clase más probable y la probabilidad de cada resultado
  (Deserción, Sigue matriculado y Graduación),
- ajustar el **umbral de alerta** (30 % por defecto): la app avisa cuando la probabilidad de deserción lo supera,
- consultar las métricas del modelo y la advertencia de que la clase *Sigue matriculado* es la menos confiable.

---

### Paso 7 · Poner el icono

Crea un icono en formato `.ico` (por ejemplo en <https://www.icoconverter.com/> a partir de un PNG,
con los tamaños 16, 32, 48 y 256) y guárdalo exactamente aquí:

```
pycaret-inno/assets/icono.ico
```

Lo usan tres cosas: la ventana de la app, el `.exe` y el instalador.

---

### Paso 8 · Crear el ejecutable con PyInstaller

```powershell
uv run pyinstaller ClasificadorDesertor.spec --noconfirm
```

Tarda unos minutos. El resultado queda en:

```
dist/ClasificadorDesertor/
├── ClasificadorDesertor.exe  ← doble clic para probar
└── _internal/               ← Python, PyCaret, el modelo... (no se toca)
```

Haz doble clic en `ClasificadorDesertor.exe` para comprobar que funciona **antes** de crear el instalador.

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
2. *File → Open* → `instalador/ClasificadorDesertor.iss`.
3. *Build → Compile* (o **Ctrl + F9**).

El instalador queda en `instalador/salida/ClasificadorDesertor_Setup_1.0.0.exe`. Ese único archivo es
el que compartes: cualquiera lo instala con doble clic, **sin tener Python ni uv**.
El instalador está en español, muestra la licencia, crea el acceso en el menú Inicio (y en el
escritorio si el usuario quiere) y aparece en *Agregar o quitar programas* para desinstalarlo.

> 💡 **Atajo:** cuando ya exportaste el modelo con el cuaderno, el script `construir.ps1` hace los
> pasos 8 y 9 seguidos:
>
> ```powershell
> powershell -ExecutionPolicy Bypass -File construir.ps1
> ```

---

## 🔁 ¿Qué repetir cuando cambio algo?

| Cambié... | Repetir |
|---|---|
| Los datos, el preprocesamiento o el modelo escogido en el cuaderno | Paso 5 (cuaderno) → 8 → 9 |
| Solo la interfaz (`app.py`) | Paso 8 → 9 |
| El icono, la licencia o la versión | Paso 8 → 9 |

Para una nueva versión cambia `MyAppVersion` en `instalador/ClasificadorDesertor.iss` y `APP_VERSION`
en `app.py`. **No** cambies el `AppId`: así Windows actualiza la versión anterior en vez de instalar otra copia.

---

## Así queda el proyecto al final

```
pycaret-inno/
├── pyproject.toml              ← nombre, librerías y comandos del proyecto
├── uv.lock                     ← versiones exactas (lo crea uv, no se edita)
├── requirements.txt
├── requirements-mac.txt        ← pasos extra para Mac (Homebrew + libomp)
├── .python-version             ← 3.10
├── .venv/                      ← entorno virtual (lo crea uv)
├── ClasificadorDesertor.spec   ← receta de PyInstaller
├── construir.ps1               ← construye todo de una vez
├── license.txt
├── assets/icono.ico            ← lo pones tú (paso 7)
├── notebooks/Estudiantes_entrenamiento_pycaret.ipynb   ← fase exploratoria
├── modelo/                     ← lo exporta el cuaderno (paso 5)
│   ├── modelo_desercion.pkl
│   └── metricas.json
├── src/clasificador_desertores/      ← el código
├── build/                      ← temporal de PyInstaller (se puede borrar)
├── dist/ClasificadorDesertor/  ← lo crea el paso 8
└── instalador/
    ├── ClasificadorDesertor.iss
    └── salida/ClasificadorDesertor_Setup_1.0.0.exe ← lo crea el paso 9
```

---

## 🆘 Errores comunes

| Mensaje | Qué pasó | Solución |
|---|---|---|
| `Failed to spawn: app` | No se registró el comando | Revisa el **paso 4**, guarda `pyproject.toml` y ejecuta `uv sync` |
| `No encontré el modelo. Ejecuta primero el cuaderno…` | No se ha exportado el modelo | Ejecuta el cuaderno completo (**paso 5**), incluido el paso de exportar |
| Cuaderno: `No module named 'pycaret'` o `'clasificador_desertores'` | VS Code usa otro Python | En **Select Kernel** escoge el de `.venv` |
| Cuaderno: no puede descargar el dataset | Sin internet o el repositorio UCI no responde | Revisa tu conexión y vuelve a ejecutar la celda de carga |
| Cuaderno: `name 'top3' is not defined` (o similar) | Se ejecutó una celda sin las anteriores | *Restart* el kernel y *Run All* |
| La columna AUC de `compare_models()` sale en `0.000` | Falla conocida de PyCaret al calcular el AUC multiclase | No es un error del modelo: ignora esa columna (el cuaderno recalcula el AUC con scikit-learn) |
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
  es `dist/ClasificadorDesertor.app`.
- Cada sistema operativo compila su propio ejecutable: en Mac **no** se puede crear el `.exe` de Windows.

---

## (Opcional) Ver la versión anterior: `legacy/`

La carpeta `legacy/` tiene la primera versión: Tkinter clásico, la ruta del modelo escrita a mano
(`/Users/raldo/Desktop/...`) y PyInstaller con `--onefile`. Sirve para comparar el antes y el después:

| Antes (`legacy/`) | Ahora |
|---|---|
| Rutas absolutas: solo funcionaba en un PC | Rutas relativas: funciona en cualquier PC |
| Etiquetas numéricas (`0, 1, 2`) | Nombres de clase (Deserción, Sigue matriculado, Graduación) |
| Solo la clase predicha | Clase + probabilidad de cada resultado + alerta con umbral ajustable |
| La ventana se congela mientras carga PyCaret | El modelo carga en segundo plano |
| Tkinter clásico | CustomTkinter, con los campos organizados en pestañas |
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

1. En el cuaderno, exporta otro modelo (por ejemplo Gradient Boosting o el Random Forest ajustado con `tune_model()`), abre la app y compara las probabilidades.
2. Cambia el **umbral de alerta** de la app (por ejemplo de 30 % a 40 %) y observa cuántos estudiantes de ejemplo pasan a estar en alerta: más umbral = menos falsas alarmas pero más desertores que se escapan.
3. Agrega un botón **"Guardar resultado"** que escriba la predicción en un archivo CSV.
4. Agrega una pestaña que cargue un CSV con muchos estudiantes y los clasifique todos (`predict_model` acepta un DataFrame completo).
5. Prueba `SMOTENC`, que maneja las variables nominales de forma nativa, y compara con SMOTE aplicado sobre variables ya codificadas con One-Hot.
6. Exporta un segundo modelo **sin las variables del 2.º semestre** para dar una alerta al final del primer semestre, y mide cuánto baja el macro F1.
7. Adapta todo a otro dataset de clasificación (vinos, cáncer de mama, Titanic…): cambia la carga de datos del cuaderno, `COLUMNAS` en `core.py` y las etiquetas de la app.
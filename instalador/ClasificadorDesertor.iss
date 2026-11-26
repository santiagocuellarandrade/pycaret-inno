; Instalador de Windows para el Clasificador Desertor (PyCaret + CustomTkinter)
;
; Requisitos antes de compilar:
;   1. Haber exportado el modelo:     notebooks\entrenamiento_pycaret.ipynb
;   2. Haber creado el ejecutable:    uv run pyinstaller ClasificadorDesertor.spec --noconfirm
;   3. Tener el icono en:             assets\icono.ico
;
; Luego abre este archivo con Inno Setup y presiona Compile (Ctrl + F9).
; El instalador queda en: instalador\salida\ClasificadorDesertor_Setup_1.0.0.exe
;
; Todas las rutas son RELATIVAS a la raíz del proyecto (ver SourceDir),
; así que funciona en cualquier computador sin cambiar nada.

#define MyAppName "ClasificadorDesertor"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Universidad Autónoma de Occidente"
#define MyAppURL "https://www.uao.edu.co/"
#define MyAppExeName "ClasificadorDesertor.exe"
#define MyAppFolder "ClasificadorDesertor"

[Setup]
; AppId identifica la app en Windows. Si haces OTRA app, genera un GUID nuevo
; (menú Tools > Generate GUID). Si solo cambias la versión, déjalo igual.
AppId={{841C0D86-BD51-4CE5-B3E1-80C838D9F59A}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Las rutas de abajo se leen desde la raíz del proyecto (una carpeta arriba)
SourceDir=..
OutputDir=instalador\salida
OutputBaseFilename=ClasificadorDesertor_Setup_{#MyAppVersion}

DefaultDirName={autopf}\{#MyAppFolder}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
; Permite instalar "solo para mí" sin ser administrador (útil en salas de cómputo)
PrivilegesRequiredOverridesAllowed=dialog

LicenseFile=license.txt
SetupIconFile=assets\icono.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}

ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Toda la carpeta que creó PyInstaller (el .exe + _internal\ con Python, PyCaret y el modelo)
Source: "dist\{#MyAppFolder}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Borra el archivo de registro (logs.log) que PyCaret crea en la carpeta del usuario
Type: filesandordirs; Name: "{localappdata}\ClasificadorDesertor"

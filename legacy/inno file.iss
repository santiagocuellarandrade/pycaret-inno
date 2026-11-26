; Script generado por el Asistente de Inno Setup y modificado para el Clasificador Iris con PyCaret

#define MyAppName "Iris_Classifier"
#define MyAppVersion "1.0"
#define MyAppPublisher "Tu Nombre o Empresa"
#define MyAppURL "https://www.ejemplo.com/"
#define MyAppExeName "Iris_Classifier.exe"

[Setup]
AppId={{BAEE7D5E-DD66-4D36-B1B4-DE0451D5E729}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes
LicenseFile=D:\OneDrive - CGIAR\Desktop\Clase_4_ML\Ejemplo TKinter\license.txt
OutputDir=D:\OneDrive - CGIAR\Desktop\Clase_4_ML\Ejemplo TKinter\app
OutputBaseFilename=iris_classifier_setup
SetupIconFile=D:\OneDrive - CGIAR\Desktop\Clase_4_ML\Ejemplo TKinter\Logo\logo.ico
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Ejecutable PyInstaller (debe estar en dist/)
Source: "D:\OneDrive - CGIAR\Desktop\Clase_4_ML\Ejemplo TKinter\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Modelo entrenado (en carpeta 'modelo')
Source: "D:\OneDrive - CGIAR\Desktop\Clase_4_ML\Ejemplo TKinter\modelo\best_iris_classifier.pkl"; DestDir: "{app}\modelo"; Flags: ignoreversion

; Si tienes figuras o recursos, puedes añadirlos aquí:
; Source: "D:\ruta\completa\figures\*"; DestDir: "{app}\figures"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Lanzar {#MyAppName}"; Flags: nowait postinstall skipifsilent

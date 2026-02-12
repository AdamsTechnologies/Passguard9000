#define MyAppName "Passguard"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "PassGuard Industries"
#define MyAppUrl "coming soon"
#define MyAppExeName "Passguard.exe"

; PassGuard Installer Script
[Setup]
;SignTool=passguardsigntool
Uninstallable=yes
AppId={}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppUrl}
AppSupportURL={#MyAppUrl}
AppUpdatesURL={#MyAppUrl}
DefaultDirName={userpf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputBaseFilename=PassGuardInstaller
SetupIconFile=.\passguardInstallerIcon.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
LicenseFile=LICENSE.PASSGUARD

[Files]
; The {app} constant refers to the installation directory chosen by the user
; Recursively copy all files from dist/passguard to {app}
Source: "dist\passguard.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: ".\logoappicon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Create a Start Menu shortcut
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename:"{app}\logoappicon.ico"
;desktop shortcut
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename:"{app}\logoappicon.ico"; Tasks: desktopicon

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

;[InstallDelete]
;Type: filesandordirs; Name: "{app}"

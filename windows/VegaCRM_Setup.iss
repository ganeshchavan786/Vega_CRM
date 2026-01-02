; VEGA CRM - Inno Setup Installer Script
; Professional Windows Installer
; Download Inno Setup from: https://jrsoftware.org/isinfo.php

#define MyAppName "VEGA CRM"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "VEGA CRM"
#define MyAppURL "https://github.com/ganeshchavan786/Vega_CRM"
#define MyAppExeName "VegaCRM.exe"

[Setup]
; Application Info
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Installation Settings - Install in LocalAppData (no admin required)
DefaultDirName={localappdata}\Programs\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=..\LICENSE
OutputDir=..\installer
OutputBaseFilename=VegaCRM-Setup-{#MyAppVersion}
; SetupIconFile=vega_icon.ico  ; Uncomment if you have custom icon
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern

; Privileges - No admin required (installs per-user)
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Appearance (uncomment if you have custom images)
; WizardImageFile=wizard_image.bmp
; WizardSmallImageFile=wizard_small.bmp

; Uninstaller
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce
Name: "startupicon"; Description: "Start VEGA CRM when Windows starts"; GroupDescription: "Startup Options:"; Flags: checkedonce

[Files]
; Main Application
Source: "..\dist\VegaCRM.exe"; DestDir: "{app}"; Flags: ignoreversion

; Data Directory (created empty during install)

; Documentation
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}"; DestName: "README.txt"; Flags: ignoreversion

[Dirs]
Name: "{app}\data"; Permissions: users-full
Name: "{app}\logs"; Permissions: users-full

[Icons]
; Start Menu
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Desktop Icon
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

; Startup
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startupicon

[Run]
; Run after installation
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
Filename: "http://localhost:8101"; Description: "Open VEGA CRM in Browser"; Flags: shellexec postinstall skipifsilent unchecked

[UninstallDelete]
; Clean up on uninstall
Type: filesandordirs; Name: "{app}\logs"
Type: dirifempty; Name: "{app}"

[Code]
// Custom code for installation

function InitializeSetup(): Boolean;
begin
  Result := True;
  // Check if already running
  if CheckForMutexes('VegaCRMMutex') then
  begin
    MsgBox('VEGA CRM is currently running. Please close it before installing.', mbError, MB_OK);
    Result := False;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    // Create firewall rule for port 8000
    Exec('netsh', 'advfirewall firewall add rule name="VEGA CRM" dir=in action=allow protocol=TCP localport=8101', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  ResultCode: Integer;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    // Remove firewall rule
    Exec('netsh', 'advfirewall firewall delete rule name="VEGA CRM"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    
    // Ask to delete data
    if MsgBox('Do you want to delete all VEGA CRM data (database, logs)?', mbConfirmation, MB_YESNO) = IDYES then
    begin
      DelTree(ExpandConstant('{app}\data'), True, True, True);
    end;
  end;
end;

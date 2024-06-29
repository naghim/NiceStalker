!include "MUI2.nsh"

!define MUI_ICON "nicestalker/resources/nightstalker.ico"

;--------------------------------
;General

  ;Name and file
  Name "NiceStalker"
  OutFile "NiceStalkerInstaller.exe"
  Unicode True

  ;Default installation folder
  InstallDir "$LOCALAPPDATA\NiceStalker"

  ;Get installation folder from registry if available
  InstallDirRegKey HKCU "Software\NiceStalker" ""

  ;Request application privileges for Windows Vista
  RequestExecutionLevel user

;--------------------------------
;Interface Settings

  !define MUI_ABORTWARNING

;--------------------------------
;Pages

  !insertmacro MUI_PAGE_WELCOME
  !insertmacro MUI_PAGE_COMPONENTS
  !insertmacro MUI_PAGE_DIRECTORY
  !insertmacro MUI_PAGE_INSTFILES
  !insertmacro MUI_PAGE_FINISH

  !insertmacro MUI_UNPAGE_WELCOME
  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES
  !insertmacro MUI_UNPAGE_FINISH

;--------------------------------
;Languages

  !insertmacro MUI_LANGUAGE "English"

;--------------------------------
;Installer Sections

Section
  SetOutPath "$INSTDIR"
  File "NiceStalker.exe"
  WriteRegStr HKCU "Software\NiceStalker" "" $INSTDIR
  WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd

Section "Desktop Shortcut"
CreateShortcut "$Desktop\$(^Name).lnk" "$InstDir\NiceStalker.exe"
SectionEnd

Section "Start Menu Shortcut"
CreateShortcut "$SMPrograms\$(^Name).lnk" "$InstDir\NiceStalker.exe"
SectionEnd

;--------------------------------
;Uninstaller Section

Section "Uninstall"

  ;ADD YOUR OWN FILES HERE...
  Delete "$INSTDIR\NiceStalker.exe"

  Delete "$INSTDIR\Uninstall.exe"

  RMDir "$INSTDIR"

  DeleteRegKey /ifempty HKCU "Software\NiceStalker"

SectionEnd

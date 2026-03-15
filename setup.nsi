Name "二次供水系统"
OutFile "water-system-setup.exe"
InstallDir "$PROGRAMFILES\二次供水系统"
RequestExecutionLevel admin

Page directory
Page instfiles

Section
  SetOutPath "$INSTDIR"
  File /r "water-system-windows-green\*.*"
  CreateShortCut "$DESKTOP\二次供水系统.lnk" "$INSTDIR\启动系统.bat"
  CreateShortCut "$SMPROGRAMS\二次供水系统.lnk" "$INSTDIR\启动系统.bat"
  WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

Section "Uninstall"
  RMDir /r "$INSTDIR"
  Delete "$DESKTOP\二次供水系统.lnk"
  Delete "$SMPROGRAMS\二次供水系统.lnk"
SectionEnd

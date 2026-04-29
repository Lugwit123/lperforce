@echo off
cls
REM Build l_tray package using enhanced rez build
cd /d "%~dp0"
call %wuwo_path%\wuwo.bat rez build -i 


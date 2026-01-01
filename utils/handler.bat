@echo off
setlocal ENABLEDELAYEDEXPANSION

REM --------------------------------------------
REM Resolve project root (parent of utils)
REM --------------------------------------------
set "ROOT=%~dp0.."
pushd "%ROOT%" >nul

REM --------------------------------------------
REM Detect Blender (all drives)
REM --------------------------------------------
set "BLENDER="

for %%D in (C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
    if exist %%D:\ (
        if not defined BLENDER if exist "%%D:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe" (
            set "BLENDER=%%D:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe"
        )
        if not defined BLENDER if exist "%%D:\Program Files\Blender Foundation\Blender\blender.exe" (
            set "BLENDER=%%D:\Program Files\Blender Foundation\Blender\blender.exe"
        )
        if not defined BLENDER if exist "%%D:\Program Files (x86)\Blender Foundation\Blender\blender.exe" (
            set "BLENDER=%%D:\Program Files (x86)\Blender Foundation\Blender\blender.exe"
        )
    )
)

REM PATH fallback
if not defined BLENDER (
    where blender >nul 2>&1 && set "BLENDER=blender"
)

REM Prompt user if still not found
if not defined BLENDER (
    echo.
    echo Blender was not found automatically.
    echo Paste using right-click or type the full path to blender.exe and press Enter:
    echo.

    set /p USERBLENDER=Blender path: 
    set "USERBLENDER=%USERBLENDER:"=%"

    if not exist "%USERBLENDER%" (
        echo ERROR: File not found.
        pause
        exit /b 1
    )
    set "BLENDER=%USERBLENDER%"
)

REM ECHO START
echo Original Blender GUI Script: https://github.com/LazySpongie/Project-Zomboid-GLTF-Export-Preset
echo Blender Installation: %BLENDER%
echo Supported Blender Versions: 4.5 - 5.x
echo.

REM --------------------------------------------
REM Paths (ROOT-based)
REM --------------------------------------------
set "SCRIPT=%ROOT%\utils\pz_fbx_to_glb.py"
set "INPUT=%ROOT%\input"
set "OUTPUT=%ROOT%\output"

if not exist "%OUTPUT%" mkdir "%OUTPUT%"

REM --------------------------------------------
REM Convert FBX -> GLB
REM --------------------------------------------
set FOUND=0
for %%F in ("%INPUT%\*.fbx") do (
    set FOUND=1
    echo Converting %%~nxF to %%~nF.glb
    REM "%BLENDER%" -b -P "%SCRIPT%" -- "%%F" "%OUTPUT%\%%~nF.glb"
	REM "%BLENDER%" -b --log-level 0 -P "%SCRIPT%" -- "%%F" "%OUTPUT%\%%~nF.glb"
	"%BLENDER%" -b -P "%SCRIPT%" -- "%%F" "%ROOT%\output\%%~nF.glb" ^
  2>&1 | findstr /V /C:"INFO Draco mesh compression is available"

)

if %FOUND%==0 (
    echo No FBX files found in:
    echo %INPUT%
)

popd >nul
echo.
pause
echo.
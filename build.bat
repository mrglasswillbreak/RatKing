@echo off
REM Build RatKing.exe with PyInstaller. Run as Administrator if you want scheduled task creation to succeed.

python -m pip install --upgrade pip
pip install -r requirements.txt

REM Remove previous build artifacts
if exist build rd /s /q build
if exist dist rd /s /q dist
if exist RatKing.spec del /q RatKing.spec





pause
necho Build finished. Executable: dist\RatKing.exepyinstaller --noconfirm --onefile --noconsole --name RatKing RatKing.pynREM Create one-file executable (no console)
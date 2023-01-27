@echo off
py -m pip install pyinstaller
pyinstaller --onefile Mixie.py
echo BUILD COMPLETE
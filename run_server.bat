@echo off
title SERVER ANTRIAN DESK

echo MENJALANKAN SERVER ANTRIAN

REM pindah ke folder tempat file .bat berada
cd /d %~dp0

REM cek python
python --version
if errorlevel 1 (
    echo ERROR: Python belum terinstall atau belum masuk PATH
    echo Silakan install Python dan centang "Add Python to PATH"
    pause
    exit
)

REM buat virtual environment jika belum ada
if not exist venv (
    echo Membuat virtual environment...
    python -m venv venv
)

REM aktifkan virtualenv
call venv\Scripts\activate

REM install dependency
echo Menginstall dependency...
pip install -r requirements.txt

REM jalankan aplikasi
echo Menjalankan aplikasi...
python app.py

pause

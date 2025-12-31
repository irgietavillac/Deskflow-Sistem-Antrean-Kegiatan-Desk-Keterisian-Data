@echo off
title SERVER ANTRIAN DESK

echo MENJALANKAN SERVER ANTRIAN

cd /d %~dp0

REM cek python
python --version
if errorlevel 1 (
    echo ERROR: Python belum terinstall atau belum masuk PATH
    pause
    exit
)

REM buat venv
if not exist venv (
    echo Membuat virtual environment...
    python -m venv venv
)

REM aktifkan venv
call venv\Scripts\activate

REM upgrade pip
python -m pip install --upgrade pip

REM install dependency 
pip install -r requirements.txt

REM jalankan aplikasi
python app.py

pause

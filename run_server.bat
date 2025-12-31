@echo off
title SERVER ANTRIAN DESK

REM pindah ke folder project
cd /d C:\antrian

REM aktifkan virtualenv (kalau pakai)
call venv\Scripts\activate

REM jalankan flask
python app.py

pause

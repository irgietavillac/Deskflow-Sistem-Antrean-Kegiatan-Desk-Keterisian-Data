Requirements

1. Sistem & Perangkat Lunak
Windows OS (direkomendasikan, karena menggunakan run_server.bat)
Python 3.9+
Git

2. Database: PostgreSQL
   
3. Struktur Tabel Database:
CREATE TABLE petugas (
    id SERIAL PRIMARY KEY,
    nama TEXT UNIQUE,
    aktif BOOLEAN DEFAULT TRUE
);

CREATE TABLE instansi (
    id SERIAL PRIMARY KEY,
    nama TEXT UNIQUE,
    aktif BOOLEAN DEFAULT TRUE
);

4. Library Python
Flask
psycopg2 / psycopg2-binary
library pendukung lain sesuai requirements.txt

5. Konfigurasi koneksi database sesuaikan pada app.py

Cara Menjalankan Aplikasi

1. Download atau clone seluruh folder dan file pada repository ini.
2. Pastikan database PostgreSQL sudah tersedia beserta tabel instansi dan petugas.
3. Jalankan file run_server.bat.
4. Klik (CTRL+Click) link hosting yang muncul pada terminal untuk mengakses aplikasi.

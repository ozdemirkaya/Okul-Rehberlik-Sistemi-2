import flet as ft
from datetime import datetime
import sqlite3
import os

# ------------------ VERİTABANI ------------------

conn = sqlite3.connect("rehberlik.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS ogrenciler (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ad TEXT,
    no TEXT UNIQUE,
    sinif TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS notlar (
    id TEXT,
    ogrenci_no TEXT,
    kat TEXT,
    not_metni TEXT,
    tarih TEXT
)
""")

conn.commit()


# ------------------ UYGULAMA ------------------

def main(page: ft.Page):
    page.title = "Rehberlik"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO

    # ---------- INPUTLAR ----------
    ad_in = ft.TextField(label="Öğrenci Ad Soyad")
    sinif_in = ft.TextField(label="Sınıf")
    no_in = ft.TextField(label="Okul No")

    ogrenci_secici = ft.Dropdown(label="Öğrenci Seçin", expand=True)

    kat_in = ft.Dropdown(
        label="Görüşme Tipi",
        options=

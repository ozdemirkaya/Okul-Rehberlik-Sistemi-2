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
        options=[
            ft.dropdown.Option("Öğrenci"),
            ft.dropdown.Option("Veli"),
            ft.dropdown.Option("Öğretmen"),
        ],
        value="Öğrenci"
    )

    tarih_in = ft.TextField(
        label="Tarih",
        value=datetime.now().strftime("%d-%m-%Y")
    )

    not_txt = ft.TextField(label="Not", multiline=True, min_lines=3)
    not_listesi = ft.Column(spacing=10)

    # ---------- FONKSİYONLAR ----------

    def dropdown_doldur(e=None):
        ogrenci_secici.options = []

        cursor.execute("SELECT ad, no, sinif FROM ogrenciler")
        ogrenciler = cursor.fetchall()

        for ad, no, sinif in ogrenciler:
            ogrenci_secici.options.append(
                ft.dropdown.Option(
                    key=str(no),
                    text=f"{ad} ({sinif})"
                )
            )

        page.update()

    duzenlenen_id = ft.Text(value="", visible=False)

def notu_guncelle(e):
    if duzenlenen_id.value and not_txt.value:
        cursor.execute(
            "UPDATE notlar SET not_metni=? WHERE id=?",
            (not_txt.value, duzenlenen_id.value)
        )
        conn.commit()

        not_txt.value = ""
        duzenlenen_id.value = ""
        duzenle_btn.visible = False
        kaydet_btn.visible = True

        notlari_getir(None)
        page.update()


    def ogrenci_kaydet(e):
        if ad_in.value and no_in.value:
            try:
                cursor.execute(
                    "INSERT INTO ogrenciler (ad, no, sinif) VALUES (?, ?, ?)",
                    (ad_in.value, no_in.value, sinif_in.value)
                )
                conn.commit()

                ad_in.value = ""
                no_in.value = ""
                sinif_in.value = ""

                dropdown_doldur()

                page.snack_bar = ft.SnackBar(ft.Text("Başarıyla Kaydedildi!"))
                page.snack_bar.open = True
                page.update()

            except sqlite3.IntegrityError:
                page.snack_bar = ft.SnackBar(ft.Text("Bu okul numarası zaten kayıtlı!"))
                page.snack_bar.open = True
                page.update()

    def notu_kaydet(e):
        if ogrenci_secici.value and not_txt.value:

            cursor.execute(
                "INSERT INTO notlar VALUES (?, ?, ?, ?, ?)",
                (
                    str(datetime.now().timestamp()),
                    ogrenci_secici.value,
                    kat_in.value,
                    not_txt.value,
                    tarih_in.value
                )
            )
            conn.commit()

            not_txt.value = ""
            notlari_getir(None)
            page.update()

    def notlari_getir(e):
    not_listesi.controls.clear()

    if not ogrenci_secici.value:
        return

    cursor.execute(
        "SELECT * FROM notlar WHERE ogrenci_no=? ORDER BY id DESC",
        (ogrenci_secici.value,)
    )

    notlar = cursor.fetchall()

    for satir in notlar:
        not_id = satir[0]
        gorusme_tipi = satir[2]
        metin = satir[3]
        tarih = satir[4]

        def sil_click(e, nid=not_id):
            cursor.execute("DELETE FROM notlar WHERE id=?", (nid,))
            conn.commit()
            notlari_getir(None)

        def duzenle_click(e, nid=not_id, eski_metin=metin):
            not_txt.value = eski_metin
            duzenlenen_id.value = nid
            duzenle_btn.visible = True
            kaydet_btn.visible = False
            page.update()

        not_listesi.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Text(f"{tarih} | {gorusme_tipi}", weight="bold"),
                    ft.Text(metin),
                    ft.Row([
                        ft.TextButton("Düzenle", on_click=duzenle_click),
                        ft.TextButton("Sil", on_click=sil_click)
                    ])
                ]),
                padding=10,
                bgcolor="#eeeeee",
                border_radius=10
            )
        )

    page.update()


    # ---------- EKRANLAR ----------

    kayit_ekrani = ft.Column([
        ft.Text("Öğrenci Kaydı", size=20, weight="bold"),
        ad_in,
        sinif_in,
        no_in,
        ft.ElevatedButton("Öğrenciyi Kaydet", on_click=ogrenci_kaydet),
        ft.Divider()
    ])

   not_ekrani = ft.Column([
    ft.Text("Görüşme Notları", size=20, weight="bold"),
    ft.Row([
        ogrenci_secici,
        ft.ElevatedButton("Tazele", on_click=dropdown_doldur)
    ]),
    ft.ElevatedButton("Notları Getir", on_click=notlari_getir),
    tarih_in,
    kat_in,
    not_txt,

    kaydet_btn,
    duzenle_btn,
    duzenlenen_id,

    not_listesi
], visible=False)


    def ekran_degistir(e):
        kayit_ekrani.visible = not kayit_ekrani.visible
        not_ekrani.visible = not not_ekrani.visible

        btn_nav.text = "Öğrenci Paneli" if not_ekrani.visible else "Not İşlemlerine Geç"

        dropdown_doldur()
        page.update()

    btn_nav = ft.OutlinedButton("Not İşlemlerine Geç", on_click=ekran_degistir)

    page.add(
        ft.Container(
            content=ft.Text("REHBERLİK PANELİ", color="white", size=22),
            bgcolor="blue",
            padding=15
        ),
        btn_nav,
        kayit_ekrani,
        not_ekrani
    )

    dropdown_doldur()


if __name__ == "__main__":
    ft.app(target=main)


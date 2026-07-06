import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 1. Konfigurasi Google Sheets (Gunakan metode Service Account agar lebih aman)
# Pastikan file credentials.json ada di folder proyek Anda di GitHub
def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    return gspread.authorize(creds)

# 2. Fungsi untuk membaca database dari Google Sheets
@st.cache_data(ttl=60)
def load_data(sheet_name):
    client = get_gspread_client()
    sheet = client.open("Database_PT_Tangguh")
    ws = sheet.worksheet(sheet_name)
    return pd.DataFrame(ws.get_all_records())

# 3. Contoh Penggunaan di Menu (Sudah diperbaiki dari IndexError)
st.title("✨ Portal PT Tangguh ✨")
menu = st.sidebar.selectbox("Menu:", ["Absensi", "Kelola Lokasi Klien"])

if menu == "Kelola Lokasi Klien":
    try:
        # Membaca data dari tab 'LokasiKlien' (Pastikan tab ini ada di Sheet Anda)
        df_lokasi = load_data("LokasiKlien") 
        st.dataframe(df_lokasi)
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}. Pastikan tab 'LokasiKlien' ada di Google Sheets Anda.")

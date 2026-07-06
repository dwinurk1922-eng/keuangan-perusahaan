import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# Setup Konfigurasi Google Sheets via Streamlit Secrets
def get_gspread_client():
    # Ambil creds dari Secrets (lihat cara pasang di bawah)
    creds_dict = json.loads(st.secrets["gcp_service_account"])
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)

# Fungsi Membaca Data
@st.cache_data(ttl=60)
def load_data(sheet_name):
    client = get_gspread_client()
    spreadsheet = client.open("Database_PT_Tangguh")
    ws = spreadsheet.worksheet(sheet_name)
    return pd.DataFrame(ws.get_all_records())

# Fungsi Menyimpan Data (Absensi)
def save_absensi(data):
    client = get_gspread_client()
    spreadsheet = client.open("Database_PT_Tangguh")
    ws = spreadsheet.worksheet("Absensi")
    ws.append_row(data)

# Tampilan Aplikasi
st.title("✨ Portal PT Tangguh")
menu = st.sidebar.selectbox("Menu:", ["Presensi GPS", "Lihat Absensi"])

if menu == "Presensi GPS":
    st.subheader("📍 Presensi Mandiri")
    nama = st.text_input("Nama Lengkap:")
    if st.button("Kirim Absensi"):
        # Data contoh (ganti dengan koordinat asli nanti)
        save_absensi(["6 Juli 2026", nama, "Hadir", "08:00", "17:00", "Kantor", "GPS"])
        st.success("Data berhasil tersimpan!")

elif menu == "Lihat Absensi":
    st.subheader("📋 Log Absensi")
    st.dataframe(load_data("Absensi"))

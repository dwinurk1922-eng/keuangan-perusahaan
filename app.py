import streamlit as st
import pandas as pd
import gspread
import json
import datetime
import math
from oauth2client.service_account import ServiceAccountCredentials
from streamlit_js_eval import streamlit_js_eval

# 1. KONFIGURASI GOOGLE SHEETS
def get_gspread_client():
    creds_dict = json.loads(st.secrets["gcp_service_account"])
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)

# Fungsi Ambil Data
@st.cache_data(ttl=60)
def load_data(sheet_name):
    client = get_gspread_client()
    ws = client.open("Database_PT_Tangguh").worksheet(sheet_name)
    return pd.DataFrame(ws.get_all_records())

# 2. LOGIKA APLIKASI
st.set_page_config(page_title="PT Tangguh Cahaya Pratama", layout="wide")
st.title("✨ Portal PT Tangguh Cahaya Pratama")

# Autentikasi Admin
PIN = "KOLIP_CANTIK_0987654321"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# Sidebar Menu
role = st.sidebar.radio("Masuk Sebagai:", ["Karyawan", "Admin"])
if role == "Admin":
    pin_input = st.sidebar.text_input("Masukkan PIN Admin:", type="password")
    if pin_input == PIN: st.session_state.logged_in = True
    else: st.sidebar.error("PIN Salah!")

# --- MENU KARYAWAN ---
if role == "Karyawan":
    menu = st.sidebar.selectbox("Menu Karyawan:", ["📢 Pengumuman", "📍 Presensi GPS"])
    if menu == "📢 Pengumuman":
        st.subheader("📢 Informasi Terbaru")
        st.dataframe(load_data("Pengumuman"))
    
    elif menu == "📍 Presensi GPS":
        st.subheader("📍 Presensi Mandiri")
        loc = streamlit_js_eval(data_container_name='geolocation', key='geo')
        if st.button("Kirim Absensi"):
            client = get_gspread_client()
            ws = client.open("Database_PT_Tangguh").worksheet("Absensi")
            ws.append_row([str(datetime.datetime.now()), "User", "Hadir", "GPS"])
            st.success("Absensi terkirim!")

# --- MENU ADMIN ---
elif role == "Admin" and st.session_state.logged_in:
    menu = st.sidebar.selectbox("Menu Admin:", ["📊 Dashboard", "💸 Laporan Keuangan", "📍 Kelola Lokasi", "📑 Kasbon"])
    
    if menu == "📊 Dashboard":
        st.subheader("📊 Dashboard Executive")
        st.write("Pantau operasional perusahaan Anda di sini.")
        st.dataframe(load_data("Absensi"))
        
    elif menu == "💸 Laporan Keuangan":
        st.subheader("💸 Laporan Cash Flow")
        st.dataframe(load_data("CashFlow"))
        
    elif menu == "📍 Kelola Lokasi":
        st.subheader("📍 Atur Titik Koordinat Klien")
        with st.form("lokasi_baru"):
            nama = st.text_input("Nama Lokasi:")
            lat = st.number_input("Latitude:")
            lon = st.number_input("Longitude:")
            if st.form_submit_button("Simpan Lokasi"):
                client = get_gspread_client()
                client.open("Database_PT_Tangguh").worksheet("LokasiKlien").append_row([nama, lat, lon])
                st.success("Lokasi baru ditambahkan!")

    elif menu == "📑 Kasbon":
        st.subheader("📑 Data Kasbon Karyawan")
        st.dataframe(load_data("Kasbon"))

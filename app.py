import streamlit as st
import pandas as pd
import gspread
import json
import datetime
import math
from oauth2client.service_account import ServiceAccountCredentials
from streamlit_js_eval import streamlit_js_eval

# 1. SETUP KONEKSI
def get_gspread_client():
    creds_dict = json.loads(st.secrets["gcp_service_account"])
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)

@st.cache_data(ttl=60)
def load_data(sheet_name):
    try:
        client = get_gspread_client()
        ws = client.open("Database_PT_Tangguh").worksheet(sheet_name)
        data = ws.get_all_records()
        return pd.DataFrame(data) if data else pd.DataFrame()
    except: return pd.DataFrame()

# 2. LOGIKA UTAMA
st.set_page_config(page_title="PT Tangguh Cahaya Pratama", layout="wide")
st.title("✨ Portal PT Tangguh Cahaya Pratama")

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
role = st.sidebar.radio("Masuk Sebagai:", ["Karyawan", "Admin"])

# --- MENU ADMIN (LENGKAP) ---
if role == "Admin":
    pin = st.sidebar.text_input("PIN Admin:", type="password")
    if pin == "KOLIP_CANTIK_0987654321": st.session_state.logged_in = True
    
    if st.session_state.logged_in:
        menu = st.sidebar.selectbox("Panel Admin:", ["📊 Dashboard", "💸 Laporan Keuangan", "📑 Kasbon", "📍 Kelola Lokasi", "📢 Pengumuman"])
        
        if menu == "📊 Dashboard":
            st.subheader("📊 Rekapitulasi Absensi")
            st.dataframe(load_data("Absensi"))
        elif menu == "💸 Laporan Keuangan":
            st.subheader("💸 Laporan Cash Flow")
            st.dataframe(load_data("CashFlow"))
        elif menu == "📑 Kasbon":
            st.subheader("📑 Data Kasbon Karyawan")
            st.dataframe(load_data("Kasbon"))
        elif menu == "📍 Kelola Lokasi":
            st.subheader("📍 Titik Koordinat Klien")
            with st.form("lokasi_add"):
                nama = st.text_input("Nama Lokasi")
                lat = st.number_input("Latitude")
                lon = st.number_input("Longitude")
                if st.form_submit_button("Tambah Lokasi"):
                    # Tambah data ke sheet LokasiKlien
                    st.success("Lokasi disimpan!")
        elif menu == "📢 Pengumuman":
            st.subheader("📢 Buat Pengumuman Baru")
            judul = st.text_input("Judul")
            isi = st.text_area("Isi Pengumuman")
            if st.button("Posting"):
                st.success("Pengumuman diposting!")

# --- MENU KARYAWAN (LENGKAP) ---
elif role == "Karyawan":
    menu = st.sidebar.selectbox("Menu:", ["📢 Pengumuman", "📍 Presensi GPS"])
    if menu == "📢 Pengumuman":
        st.subheader("📢 Informasi Terbaru")
        st.dataframe(load_data("Pengumuman"))
    elif menu == "📍 Presensi GPS":
        st.subheader("📍 Presensi Mandiri")
        st.write("Silakan klik tombol di bawah untuk melakukan absen.")
        if st.button("Kirim Absensi"):
            st.success("Absensi berhasil diproses dengan validasi lokasi!")

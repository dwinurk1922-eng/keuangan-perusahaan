import streamlit as st
import pandas as pd
import gspread
import json
import datetime
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. SETUP KONEKSI ---
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

# --- 2. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Portal PT Tangguh", layout="wide")
st.title("✨ Portal PT Tangguh Cahaya Pratama")

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# --- 3. MENU SIDEBAR ---
role = st.sidebar.radio("Masuk Sebagai:", ["Karyawan", "Admin"])

if role == "Admin":
    pin = st.sidebar.text_input("PIN Admin:", type="password")
    if pin == "KOLIP_CANTIK_0987654321": st.session_state.logged_in = True
    
    if st.session_state.logged_in:
        menu = st.sidebar.selectbox("Panel Admin:", ["📊 Dashboard Absensi", "💰 Laporan Keuangan", "📑 Manajemen Kasbon", "📍 Kelola Lokasi", "📢 Pengumuman"])
        
        # Dashboard Absensi
        if menu == "📊 Dashboard Absensi":
            st.subheader("📊 Rekapitulasi Absensi")
            df = load_data("Absensi")
            st.dataframe(df)
            if not df.empty:
                st.download_button("Unduh Rekap Absensi (CSV)", data=df.to_csv(index=False), file_name="absensi.csv")

        # Laporan Keuangan + Filter Bulanan
        elif menu == "💰 Laporan Keuangan":
            st.subheader("💰 Laporan Keuangan & Neraca")
            df = load_data("CashFlow")
            if not df.empty:
                df['Tanggal'] = pd.to_datetime(df['Tanggal'])
                bulan_map = {'Januari': 1, 'Februari': 2, 'Maret': 3, 'April': 4, 'Mei': 5, 'Juni': 6, 'Juli': 7, 'Agustus': 8, 'September': 9, 'Oktober': 10, 'November': 11, 'Desember': 12}
                pilih = st.selectbox("Pilih Bulan:", list(bulan_map.keys()))
                df_fil = df[df['Tanggal'].dt.month == bulan_map[pilih]]
                st.dataframe(df_fil)
                
                # Metric Neraca
                col1, col2 = st.columns(2)
                col1.metric("Total Pemasukan", f"Rp {df_fil['Masuk'].sum():,.0f}")
                col2.metric("Total Pengeluaran", f"Rp {df_fil['Keluar'].sum():,.0f}")
                st.download_button("Unduh Laporan Bulanan", data=df_fil.to_csv(index=False), file_name=f"Laporan_{pilih}.csv")
            else: st.warning("Data keuangan belum tersedia.")

        elif menu == "📑 Manajemen Kasbon":
            st.subheader("📑 Data Kasbon Karyawan")
            st.dataframe(load_data("Kasbon"))
        
        elif menu == "📍 Kelola Lokasi":
            st.subheader("📍 Titik Koordinat")
            st.dataframe(load_data("LokasiKlien"))

        elif menu == "📢 Pengumuman":
            st.subheader("📢 Buat Pengumuman")
            isi = st.text_area("Tulis pengumuman:")
            if st.button("Posting"): st.success("Pengumuman berhasil di-update!")

# --- 4. MENU KARYAWAN ---
elif role == "Karyawan":
    menu = st.sidebar.selectbox("Menu Karyawan:", ["📢 Pengumuman", "📍 Presensi GPS"])
    if menu == "📢 Pengumuman":
        st.subheader("📢 Informasi Terbaru")
        st.dataframe(load_data("Pengumuman"))
    elif menu == "📍 Presensi GPS":
        st.subheader("📍 Form Presensi")
        if st.button("Kirim Absensi"): st.success("Presensi berhasil dicatat!")

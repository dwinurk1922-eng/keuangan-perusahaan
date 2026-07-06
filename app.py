import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from streamlit_js_eval import streamlit_js_eval

# KONFIGURASI
st.set_page_config(page_title="Portal PT Tangguh", layout="wide")
st.title("✨ Portal PT Tangguh Cahaya Pratama")

# Koneksi ke Google Sheets (Pastikan Sheet sudah di-Share "Anyone with the link")
conn = st.connection("gsheets", type=GSheetsConnection)
URL = "https://docs.google.com/spreadsheets/d/URL_GOOGLE_SHEET_ANDA_DI_SINI/edit"

def load_data(sheet_name):
    return conn.read(spreadsheet=URL, worksheet=sheet_name)

# MENU UTAMA
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
role = st.sidebar.radio("Masuk Sebagai:", ["Karyawan", "Admin"])

# PANEL ADMIN
if role == "Admin":
    pin = st.sidebar.text_input("PIN Admin:", type="password")
    if pin == "KOLIP_CANTIK_0987654321": st.session_state.logged_in = True
    
    if st.session_state.logged_in:
        menu = st.sidebar.selectbox("Panel Admin:", ["Dashboard Absensi", "Laporan Keuangan", "Manajemen Kasbon", "Kelola Lokasi", "Pengumuman"])
        
        if menu == "Dashboard Absensi":
            st.subheader("📊 Rekapitulasi Absensi")
            df = load_data("Absensi")
            st.dataframe(df)
            st.download_button("Unduh CSV", data=df.to_csv(index=False), file_name="absensi.csv")
            
        elif menu == "Laporan Keuangan":
            st.subheader("💰 Laporan Keuangan Bulanan")
            df = load_data("CashFlow")
            if not df.empty:
                df['Tanggal'] = pd.to_datetime(df['Tanggal'])
                bulan = st.selectbox("Pilih Bulan:", ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"])
                bulan_idx = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"].index(bulan) + 1
                df_fil = df[df['Tanggal'].dt.month == bulan_idx]
                st.dataframe(df_fil)
                col1, col2 = st.columns(2)
                col1.metric("Pemasukan", f"Rp {df_fil['Masuk'].sum():,.0f}")
                col2.metric("Pengeluaran", f"Rp {df_fil['Keluar'].sum():,.0f}")
                st.download_button("Unduh Laporan", data=df_fil.to_csv(index=False), file_name=f"Laporan_{bulan}.csv")

        elif menu == "Manajemen Kasbon":
            st.subheader("📑 Data Kasbon")
            st.dataframe(load_data("Kasbon"))

# PANEL KARYAWAN
elif role == "Karyawan":
    menu = st.sidebar.selectbox("Menu Karyawan:", ["📢 Pengumuman", "📍 Presensi GPS"])
    if menu == "📢 Pengumuman":
        st.subheader("📢 Informasi Terbaru")
        st.dataframe(load_data("Pengumuman"))
    elif menu == "📍 Presensi GPS":
        st.subheader("📍 Presensi Mandiri")
        if st.button("Kirim Absensi"):
            st.success("Absensi berhasil dicatat!")

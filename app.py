import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Portal PT Tangguh", layout="wide")
st.title("✨ Portal PT Tangguh Cahaya Pratama")

# 2. KONEKSI KE GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)
URL = "https://docs.google.com/spreadsheets/d/1fUFRm_NGfMIz2alyJLuJSobuZk34rph3q-ahsO2bMLA/edit?usp=sharing"

def load_data(sheet_name):
    try:
        return conn.read(spreadsheet=URL, worksheet=sheet_name)
    except Exception as e:
        st.error(f"Gagal memuat sheet '{sheet_name}': {e}")
        return pd.DataFrame()

# 3. LOGIKA MENU
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
            st.dataframe(load_data("Absensi"))
            
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
                col1.metric("Pemasukan", f"Rp {df_fil['Masuk (Rp)'].sum():,.0f}")
                col2.metric("Pengeluaran", f"Rp {df_fil['Keluar (Rp)'].sum():,.0f}")
                st.download_button("Unduh Laporan", data=df_fil.to_csv(index=False), file_name=f"Laporan_{bulan}.csv")
            else: st.info("Data keuangan belum tersedia.")

        elif menu == "Manajemen Kasbon":
            st.subheader("📑 Data Kasbon")
            st.dataframe(load_data("Kasbon"))
            
        elif menu == "Kelola Lokasi":
            st.subheader("📍 Titik Koordinat")
            st.dataframe(load_data("LokasiKlien"))
            
        elif menu == "Pengumuman":
            st.subheader("📢 Pengumuman")
            st.dataframe(load_data("Pengumuman"))

# PANEL KARYAWAN
elif role == "Karyawan":
    menu = st.sidebar.selectbox("Menu Karyawan:", ["📢 Pengumuman", "📍 Presensi GPS"])
    if menu == "📢 Pengumuman":
        st.dataframe(load_data("Pengumuman"))
    elif menu == "📍 Presensi GPS":
        st.subheader("📍 Presensi Mandiri")
        if st.button("Kirim Absensi"):
            st.success("Absensi berhasil dicatat!")

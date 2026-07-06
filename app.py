import streamlit as st
import pandas as pd
import gspread
import json
import datetime
from oauth2client.service_account import ServiceAccountCredentials
from streamlit_js_eval import streamlit_js_eval

# 1. SETUP KONEKSI GOOGLE SHEETS
def get_gspread_client():
    # Mengambil kredensial dari Secrets Streamlit
    creds_dict = json.loads(st.secrets["gcp_service_account"])
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)

# 2. FUNGSI MEMBACA DATA (Tahan Banting)
@st.cache_data(ttl=60)
def load_data(sheet_name):
    try:
        client = get_gspread_client()
        ws = client.open("Database_PT_Tangguh").worksheet(sheet_name)
        data = ws.get_all_records()
        return pd.DataFrame(data) if data else pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

# 3. SETUP HALAMAN
st.set_page_config(page_title="PT Tangguh Cahaya Pratama", layout="wide")
st.title("✨ Portal PT Tangguh Cahaya Pratama")

# Autentikasi Admin
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
role = st.sidebar.radio("Masuk Sebagai:", ["Karyawan", "Admin"])

if role == "Admin":
    pin = st.sidebar.text_input("PIN Admin:", type="password")
    if pin == "KOLIP_CANTIK_0987654321": st.session_state.logged_in = True
    else: st.sidebar.warning("Masukkan PIN yang benar")

# --- KONTEN APLIKASI ---
if role == "Karyawan":
    menu = st.sidebar.selectbox("Menu:", ["📢 Pengumuman", "📍 Presensi GPS"])
    if menu == "📢 Pengumuman":
        st.subheader("📢 Pengumuman Perusahaan")
        df = load_data("Pengumuman")
        st.dataframe(df) if not df.empty else st.info("Tidak ada pengumuman.")
    
    elif menu == "📍 Presensi GPS":
        st.subheader("📍 Presensi Mandiri")
        if st.button("Kirim Absensi"):
            try:
                client = get_gspread_client()
                ws = client.open("Database_PT_Tangguh").worksheet("Absensi")
                ws.append_row([str(datetime.datetime.now()), "Karyawan", "Hadir", "Kantor", "GPS"])
                st.success("Berhasil Absen!")
            except:
                st.error("Gagal terhubung ke Database.")

elif role == "Admin" and st.session_state.logged_in:
    menu = st.sidebar.selectbox("Panel Admin:", ["📊 Dashboard", "💸 Keuangan", "📍 Lokasi", "📑 Kasbon"])
    
    if menu == "📊 Dashboard":
        st.subheader("📊 Rekap Absensi")
        st.dataframe(load_data("Absensi"))
    elif menu == "💸 Keuangan":
        st.subheader("💸 Laporan Cash Flow")
        st.dataframe(load_data("CashFlow"))
    elif menu == "📍 Lokasi":
        st.subheader("📍 Atur Titik Koordinat")
        with st.form("lokasi"):
            nama = st.text_input("Nama Lokasi")
            if st.form_submit_button("Simpan"):
                client = get_gspread_client()
                client.open("Database_PT_Tangguh").worksheet("LokasiKlien").append_row([nama])
                st.success("Data tersimpan!")
    elif menu == "📑 Kasbon":
        st.subheader("📑 Data Kasbon")
        st.dataframe(load_data("Kasbon"))

else:
    st.info("Silakan login sebagai Admin untuk melihat panel kontrol.")

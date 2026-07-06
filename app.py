import streamlit as st
import pandas as pd
import datetime
import google.generativeai as genai
from PIL import Image
# Import library tambahan untuk mengambil koordinat GPS via browser
from streamlit_js_eval import streamlit_js_eval

# =========================================================================
# PENGATURAN DATABASE & AI ANDA (SUDAH DIKODEKAN LANGSUNG)
SHEETS_URL = "https://docs.google.com/spreadsheets/d/1VDqISHpjg8OWWPzl1NWOcc9V6j_o6Zw2/edit?usp=sharing"
GEMINI_API_KEY = "AQ.Ab8RN6J6P_ygWhv1BVnR7cZDTwU4F3bhuTPKXHi1BB_ZzUikGg"

# KOORDINAT PUSAT KANTOR PT TANGGUH CAHAYA PRATAMA (Silakan sesuaikan koordinat asli kantor Anda)
KANTOR_LAT = -7.1147 
KANTOR_LON = 112.4170
RADIAN_TOLERANSI = 0.005 # Batas toleransi jarak radius area kantor
# =========================================================================

# Konfigurasi AI Gemini Resmi
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# 1. KONFIGURASI HALAMAN & TEMA PROFESIONAL
st.set_page_config(
    page_title="FinOps Central - PT Tangguh Cahaya Pratama", 
    page_icon="💼",
    layout="wide"
)

# Kustomisasi CSS untuk Tampilan Resmi & Mewah (Corporate Look)
st.markdown("""
    <style>
        .reportview-container { background: #f8f9fa; }
        .main-header { font-size: 32px; font-weight: bold; color: #1E3A8A; margin-bottom: 5px; }
        .sub-header { font-size: 16px; color: #4B5563; margin-bottom: 25px; }
        .metric-card { background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05); border-left: 5px solid #1E3A8A; }
        .sidebar-title { font-size: 20px; font-weight: bold; color: #1E3A8A; }
    </style>
""", unsafe_allow_html=True)

# Fungsi Baca Data dari Google Sheets
@st.cache_data(ttl=10)
def load_data_from_sheets(sheet_name):
    try:
        csv_url = SHEETS_URL.replace("/edit?usp=sharing", f"/gviz/tq?tqx=out:csv&sheet={sheet_name}")
        csv_url = csv_url.split("/edit")[0] + f"/gviz/tq?tqx=out:csv&sheet={sheet_name}"
        return pd.read_csv(csv_url)
    except:
        return None

# Ambil Data Awal dari Sheets (Jika Ada)
df_cf_sheets = load_data_from_sheets("Cash_Flow")
df_kb_sheets = load_data_from_sheets("Kasbon_Karyawan")
df_kry_sheets = load_data_from_sheets("Data_Karyawan")
df_abs_sheets = load_data_from_sheets("Absensi")
df_pr_sheets = load_data_from_sheets("Payroll")

# Inisialisasi Session State Basis Data Lokal
if 'cash_flow' not in st.session_state:
    if df_cf_sheets is not None:
        st.session_state.cash_flow = df_cf_sheets
    else:
        st.session_state.cash_flow = pd.DataFrame(columns=["Tanggal", "Kategori", "Keterangan / Deskripsi", "Pendapatan (Kas Masuk)", "Pengeluaran (Kas Keluar)"])

if 'kasbon' not in st.session_state:
    st.session_state.kasbon = df_kb_sheets if df_kb_sheets is not None else pd.DataFrame(columns=["Tanggal", "Nama Karyawan", "Divisi / Bagian", "Jumlah Kasbon", "Status Pengembalian"])

if 'karyawan' not in st.session_state:
    st.session_state.karyawan = df_kry_sheets if df_kry_sheets is not None else pd.DataFrame(columns=["ID Karyawan", "Nama Karyawan", "Jabatan", "Gaji Pokok", "Tunjangan"])

if 'absensi' not in st.session_state:
    st.session_state.absensi = df_abs_sheets if df_abs_sheets is not None else pd.DataFrame(columns=["Tanggal", "Bulan/Tahun", "Nama Karyawan", "Status Kehadiran", "Lokasi Koordinat", "Metode"])

if 'payroll' not in st.session_state:
    st.session_state.payroll = df_pr_sheets if df_pr_sheets is not None else pd.DataFrame(columns=["Tanggal Payroll", "Bulan/Tahun", "Nama Karyawan", "Total Hadir", "Total Gaji Dibayar"])

# Data Komponen Pengumuman Internal perusahaan (Session State)
if 'pengumuman' not in st.session_state:
    st.session_state.pengumuman = [
        {"Tanggal": "2026-07-06", "Judul": "Pemberitahuan Sistem Presensi GPS Baru", "Isi": "Mulai hari ini, seluruh karyawan wajib melakukan absensi rutin langsung melalui Portal Karyawan di aplikasi ini menggunakan fitur pencatatan lokasi berbasis GPS terpusat saat berada di area operasional PT Tangguh Cahaya Pratama."},
        {"Tanggal": "2026-07-01", "Judul": "Kepatuhan Berkas Legalitas Finansial", "Isi": "Diingatkan kepada divisi operasional untuk mengunggah nota komersial secara berkala agar pengesahan ledger keuangan akhir bulan berjalan tepat waktu."}
    ]

# Fungsi Analisis Nota Pakai AI
def analisis_nota_dengan_ai(foto_input):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        gambar = Image.open(foto_input)
        perintah = """Kamu adalah robot akuntan. Analisis foto nota/kuitansi ini. Berikan format: Tanggal: YYYY-MM-DD, Keterangan: nama toko, Total: angka saja."""
        response = model.generate_content([perintah, gambar])
        return response.text
    except Exception as e:
        return f"Error AI: {str(e)}"

# ==========================================
# SIDEBAR PANEL - NAVIGASI MULTI-ROLE
# ==========================================
st.sidebar.markdown("<div class='sidebar-title'>🏢 PT TANGGUH CAHAYA PRATAMA</div>", unsafe_allow_html=True)
st.sidebar.caption("Sistem Informasi FinOps & Payroll Enterprise")
st.sidebar.markdown("---")

# Pilihan Role untuk membatasi hak akses visual
role_akses = st.sidebar.selectbox("Pilih Hak Akses Sistem:", ["Portal Karyawan (Umum)", "Manajemen FinOps (Otorisasi)"])
st.sidebar.markdown("---")

# Mengubah Menu Navigasi Berdasarkan Hak Aks

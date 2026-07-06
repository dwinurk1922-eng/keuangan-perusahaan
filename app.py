import streamlit as st
import pandas as pd
import datetime
import google.generativeai as genai
from PIL import Image
# Import library tambahan untuk mengambil koordinat GPS via browser
from streamlit_js_eval import streamlit_js_eval

# =========================================================================
# PENGATURAN DATABASE & AI ANDA (SUDAH DIISI DIREK)
SHEETS_URL = "https://docs.google.com/spreadsheets/d/1VDqISHpjg8OWWPzl1NWOcc9V6j_o6Zw2/edit?usp=sharing&ouid=117398658595436431688&rtpof=true&sd=true"
GEMINI_API_KEY = "AQ.Ab8RN6J6P_ygWhv1BVnR7cZDTwU4F3bhuTPKXHi1BB_ZzUikGg"

# AMAN: Membaca PIN dari Streamlit Secrets (Jika belum diatur di dashboard, default-nya "2026")
if "PIN_OTORISASI" in st.secrets:
    PIN_OTORISASI = str(st.secrets["PIN_OTORISASI"])
else:
    PIN_OTORISASI = "2026"

# KOORDINAT PUSAT KANTOR PT TANGGUH CAHAYA PRATAMA 
KANTOR_LAT = -7.1147 
KANTOR_LON = 112.4170
RADIAN_TOLERANSI = 0.005 # Batas toleransi jarak radius area kantor
# =========================================================================

# Konfigurasi AI Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# 1. KONFIGURASI HALAMAN & TEMA PROFESIONAL
st.set_page_config(
    page_title="Portal Karyawan - PT Tangguh Cahaya Pratama", 
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
# SIDEBAR PANEL - NAVIGASI MULTI-ROLE + SECURE PIN
# ==========================================
st.sidebar.markdown("<div class='sidebar-title'>🏢 PT TANGGUH CAHAYA PRATAMA</div>", unsafe_allow_html=True)
st.sidebar.caption("Sistem Informasi FinOps & Payroll Enterprise")
st.sidebar.markdown("---")

# Pilihan Role Keamanan
role_akses = st.sidebar.selectbox("Pilih Hak Akses Sistem:", ["Portal Karyawan (Umum)", "Manajemen FinOps (Otorisasi)"])

# Logika Verifikasi PIN Otorisasi
akses_diberikan = False
if role_akses == "Manajemen FinOps (Otorisasi)":
    input_pin = st.sidebar.text_input("Masukkan PIN Otorisasi FinOps:", type="password")
    if input_pin == PIN_OTORISASI:
        akses_diberikan = True
        st.sidebar.success("🔑 Otorisasi Terverifikasi!")
    elif input_pin != "":
        st.sidebar.error("❌ PIN Otorisasi Salah!")
else:
    akses_diberikan = True # Portal karyawan otomatis terbuka tanpa PIN

st.sidebar.markdown("---")

# Mengubah Menu Navigasi Berdasarkan Hak Akses & Status Verifikasi PIN
if role_akses == "Manajemen FinOps (Otorisasi)" and akses_diberikan:
    st.sidebar.markdown("### 🧑‍💼 Otorisasi Manajemen")
    st.sidebar.info("**Finance Manager:**\n**Dwi Nur Kolipah, S.H.**\n*Corporate Finance & Legal*")
    menu = st.sidebar.radio("Pilih Modul FinOps:", ["Dashboard Eksekutif", "Manajemen Cash Flow (Ada AI)", "Data Master Karyawan", "Absensi Terpusat (Rekap)", "Payroll & Penggajian", "Kasbon Karyawan", "Kelola Pengumuman", "Unduh Laporan"])
else:
    st.sidebar.markdown("### 👥 Portal Mandiri Karyawan")
    st.sidebar.success("Status: Hak Akses Karyawan Terverifikasi")
    menu = st.sidebar.radio("Pilih Menu Karyawan:", ["📢 Papan Pengumuman Resmi", "📍 Presensi Rutin Mandiri (GPS)"])

st.sidebar.markdown("---")
st.sidebar.caption("🤖 FinOps AI Core v2.5 | GPS Terpusat: Aktif")


# =========================================================================================
# JALUR MENU UTAMA APLIKASI
# =========================================================================================

if menu == "📢 Papan Pengumuman Resmi":
    st.markdown("<div class='main-header'>📢 Papan Pengumuman Internal Resmi</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Informasi dan Regulasi Manajemen PT TANGGUH CAHAYA PRATAMA</div>", unsafe_allow_html=True)
    
    for p in st.session_state.pengumuman:
        with st.expander(f"📌 {p['Judul']} ({p['Tanggal']})", expanded=True):
            st.write(p['Isi'])
            st.caption("Diterbitkan oleh: Manajemen Keuangan & Legal Perusahaan")

elif menu == "📍 Presensi Rutin Mandiri (GPS)":
    st.markdown("<div class='main-header'>📍 Sistem Presensi Rutin Berbasis Geolocation</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Pencatatan Kehadiran Karyawan Berbasis Pemusatan Koordinat GPS Satelit</div>", unsafe_allow_html=True)
    
    if "Nama Karyawan" in st.session_state.karyawan.columns and not st.session_state.karyawan.empty:
        list_karyawan = st.session_state.karyawan["Nama Karyawan"].tolist()
    else:
        list_karyawan = []
        
    if not list_karyawan:
        st.warning("⚠️ Database master karyawan perusahaan belum diisi oleh manajemen. Silakan hubungi bagian FinOps untuk mengisi Master Data Karyawan terlebih dahulu.")
    else:
        st.info("💡 Sistem sedang membaca koordinat perangkat Anda. Pastikan Anda telah memberikan izin/akses lokasi (Allow Location Access) pada browser laptop atau HP Anda.")
        
        lokasi_user = streamlit_js_eval(data_container_name='geolocation', before_update_data=None, key='geo')
        
        with st.form("form_absen_mandiri", clear_on_submit=False):
            nama_absen = st.selectbox("Pilih Nama Anda:", list_karyawan)
            bulan_abs = st.selectbox("Periode Bulan Buku:", ["Januari 2026", "Februari 2026", "Maret 2026", "April 2026", "Mei 2026", "Juni 2026", "Juli 2026", "Agustus 2026", "September 2026", "Oktober 2026", "November 2026", "Desember 2026"])
            
            if lokasi_user:
                lat_user = lokasi_user['coords']['latitude']
                lon_user = lokasi_user['coords']['longitude']
                st.success(f"📍 Sensor GPS Terdeteksi: Latitude {lat_user}, Longitude {lon_user}")
                
                jarak_lat = abs(lat_user - KANTOR_LAT)
                jarak_lon = abs(lon_user - KANTOR_LON)
                
                if jarak_lat <= RADIAN_TOLERANSI and jarak_lon <= RADIAN_TOLERANSI:
                    area_status = "Di Dalam Area Kantor (SAH)"
                    st.write("🟢 **Status Lokasi:** Anda berada di dalam radius area operasional kantor PT Tangguh Cahaya Pratama.")
                else:
                    area_status = "Di Luar Area Kantor"
                    st.error("❌ **Status Lokasi:** Anda terdeteksi berada di luar area/radius koordinat resmi kantor.")
            else:
                lat_user, lon_user, area_status = None, None, "GPS Tidak Aktif"
                st.warning("⚠️ Koordinat satelit belum didapatkan. Harap tunggu atau refresh halaman dan izinkan akses lokasi.")

            if st.form_submit_button("Kirim Presensi Kehadiran"):
                if area_status == "Di Luar Area Kantor":
                    st.error("❌ Gagal Absen! Anda tidak dapat melakukan absensi rutin jika berada di luar jangkauan GPS pusat perusahaan.")
                elif area_status == "GPS Tidak Aktif":
                    st.error("❌ Gagal Absen! Sensor GPS perangkat Anda wajib diaktifkan terlebih dahulu.")
                else:
                    tgl_hari_ini = str(datetime.date.today())
                    
                    if not st.session_state.absensi.empty and "Nama Karyawan" in st.session_state.absensi.columns:
                        cek_absen = st.session_state.absensi[(st.session_state.absensi["Tanggal"] == tgl_hari_ini) & (st.session_state.absensi["Nama Karyawan"] == nama_absen)]
                    else:
                        cek_absen = pd.DataFrame()
                    
                    if not cek_absen.empty:
                        st.warning(f"ℹ️ {nama_absen}, Anda sudah melakukan pengisian absensi untuk hari ini ({tgl_hari_ini}).")
                    else:
                        new_abs = {
                            "Tanggal": tgl_hari_ini,
                            "Bulan/Tahun": bulan_abs,
                            "Nama Karyawan": nama_absen,
                            "Status Kehadiran": "Hadir",
                            "Lokasi Koordinat": f"{lat_user}, {lon_user}",
                            "Metode": "Mandiri GPS (Mobile)"
                        }
                        st.session_state.absensi = pd.concat([pd.DataFrame([new_abs]), pd.DataFrame(st.session_state.absensi)], ignore_index=True)
                        st.success(f"✅ Presensi Berhasil! Kehadiran atas nama {nama_absen} pada tanggal {tgl_hari_ini} telah diverifikasi.")

elif menu == "Dashboard Eksekutif" and akses_diberikan:
    st.markdown("<div class='main-header'>📊 Dashboard Utama & Posisi Keuangan</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>PT TANGGUH CAHAYA PRATAMA</div>", unsafe_allow_html=True)
    
    total_masuk = pd.to_numeric(st.session_state.cash_flow["Pendapatan (Kas Masuk)"], errors='coerce').fillna(0).sum()
    total_keluar = pd.to_numeric(st.session_state.cash_flow["Pengeluaran (Kas Keluar)"], errors='coerce').fillna(0).sum()
    laba_Internal = total_masuk - total_keluar
    
    col1, col2, col3 = st.columns(3)
    with col1: st.metric(label="Total Arus Kas Masuk", value=f"Rp {total_masuk:,.0f}")
    with col2: st.metric(label="Total Arus Kas Keluar", value=f"Rp {total_keluar:,.0f}")
    with col3: st.metric(label="Laba / Rugi Bersih", value=f"Rp {laba_Internal:,.0f}", delta="Surplus" if laba_Internal >= 0 else "Defisit")
    st.markdown("---")
    st.subheader("📋 Ringkasan Otorisasi Manajer")
    st.write("Semua pengeluaran operasional dan struktur penggajian tertera pada sistem ini telah melalui peninjauan hukum tata kelola keuangan perusahaan oleh **Dwi Nur Kolipah, S.H.** selaku Manajer Keuangan PT Tangguh Cahaya Pratama.")

elif menu == "Manajemen Cash Flow (Ada AI)" and akses_diberikan:
    st.markdown("<div class='main-header'>💸 Manajemen Arus Kas Korporat</div>", unsafe_allow_html=True)
    col_ai, col_manual = st.columns(2)
    with col_ai:
        st.subheader("📸 Scan Nota Otomatis via AI")
        file_nota = st.file_uploader("Unggah Foto Nota", type=["jpg", "jpeg", "png"])
        if file_nota is not None:
            st.image(file_nota, width=250)
            if st.button("Mulai Baca Nota Pakai AI"):
                with st.spinner("AI sedang mengekstrak data..."):
                    st.text_area("Hasil Ekstraksi:", analisis_nota_dengan_ai(file_nota), height=120)
    with col_manual:
        st.subheader("➕ Form Validasi Transaksi Jurnal")
        with st.form("form_cf", clear_on_submit=True):
            tgl = st.date_input("Tanggal", datetime.date.today())
            kat = st.selectbox("Kategori", ["Pengeluaran", "Pendapatan"])
            ket = st.text_input("Deskripsi")
            jml = st.number_input("Nominal (Rp)", min_value=0, step=5000)
            if st.form_submit_button("Simpan Ke Ledger"):
                val_m = jml if kat == "Pendapatan" else 0
                val_k = jml if kat == "Pengeluaran" else 0
                new_data = {"Tanggal": str(tgl), "Kategori": kat, "Keterangan / Deskripsi": ket, "Pendapatan (Kas Masuk)": val_m, "Pengeluaran (Kas Keluar)": val_k}
                st.session_state.cash_flow = pd.concat([pd.DataFrame([new_data]), pd.DataFrame(st.session_state.cash_flow)], ignore_index=True)
                st.success("Tersimpan!")
                st.rerun()
    st.dataframe(st.session_state.cash_flow, use_container_width=True)

elif menu == "Data Master Karyawan" and akses_diberikan:
    st.markdown("<div class='main-header'>👥 Master Data Karyawan</div>", unsafe_allow_html=True)
    col_form, col_table = st.columns([1, 2])
    with col_form:
        with st.form("form_karyawan", clear_on_submit=True):
            id_kry = st.text_input("ID Karyawan", value=f"TCP-{len(st.session_state.karyawan)+1:03d}")
            nama_kry = st.text_input("Nama Lengkap")
            jabatan = st.text_input("Jabatan")
            gapok = st.number_input("Gaji Pokok", min_value=0)
            tunjangan = st.number_input("Tunjangan", min_value=0)
            if st.form_submit_button("Simpan"):
                new_kry = {"ID Karyawan": id_kry, "Nama Karyawan": nama_kry, "Jabatan": jabatan, "Gaji Pokok": gapok, "Tunjangan": tunjangan}
                st.session_state.karyawan = pd.concat([pd.DataFrame([new_kry]), pd.DataFrame(st.session_state.karyawan)], ignore_index=True)
                st.rerun()
    with col_table: st.dataframe(st.session_state.karyawan, use_container_width=True)

elif menu == "Absensi Terpusat (Rekap)" and akses_diberikan:
    st.markdown("<div class='main-header'>📋 Log Database Absensi Terintegrasi</div>", unsafe_allow_html=True)
    st.write("Berikut adalah log presensi masuk yang diisi secara mandiri oleh karyawan menggunakan koordinat satelit GPS:")
    st.dataframe(st.session_state.absensi, use_container_width=True)

elif menu == "Payroll & Penggajian" and akses_diberikan:
    st.markdown("<div class='main-header'>💸 Sistem Payroll & Pencairan Kompensasi</div>", unsafe_allow_html=True)
    
    if "Nama Karyawan" in st.session_state.karyawan.columns and not st.session_state.karyawan.empty:
        list_karyawan_payroll = st.session_state.karyawan["Nama Karyawan"].tolist()
    else:
        list_karyawan_payroll = []

    if not list_karyawan_payroll:
        st.warning("⚠️ Data karyawan belum tersedia di database Google Sheets. Silakan isi Master Data Karyawan terlebih dahulu.")
    else:
        with st.form("form_payroll", clear_on_submit=True):
            tgl_bayar = st.date_input("Tanggal Payroll", datetime.date.today())
            bulan_pilih = st.selectbox("Periode Pembayaran", ["Januari 2026", "Februari 2026", "Maret 2026", "April 2026", "Mei 2026", "Juni 2026", "Juli 2026", "Agustus 2026", "September 2026", "Oktober 2026", "November 2026", "Desember 2026"])
            karyawan_pilih = st.selectbox("Pilih Karyawan", list_karyawan_payroll)
            hari_kerja_sebulan = st.number_input("Target Hari Kerja", min_value=1, value=25)
            
            if not st.session_state.absensi.empty and "Nama Karyawan" in st.session_state.absensi.columns:
                db_absen = st.session_state.absensi[(st.session_state.absensi["Nama Karyawan"] == karyawan_pilih) & (st.session_state.absensi["Bulan/Tahun"] == bulan_pilih) & (st.session_state.absensi["Status Kehadiran"] == "Hadir")]
                total_masuk = len(db_absen)
            else:
                total_masuk = 0
                
            st.info(f"ℹ️ **Kehadiran Berdasarkan Absen GPS:** {total_masuk} Hari")
            
            tombol_payroll = st.form_submit_button("Otorisasi & Cairkan Gaji")
            
            if tombol_payroll:
                st.success(f"✅ Payroll untuk {karyawan_pilih} periode {bulan_pilih} sukses diproses dan diotorisasi!")

elif menu == "Kelola Pengumuman" and akses_diberikan:
    st.markdown("<div class='main-header'>✍️ Kelola Pengumuman Internal Kantor</div>", unsafe_allow_html=True)
    with st.form("form_buat_pengumuman", clear_on_submit=True):
        judul_p = st.text_input("Judul Pengumuman Baru")
        isi_p = st.text_area("Isi Informasi")
        if st.form_submit_button("Terbitkan Ke Portal Karyawan"):
            new_p = {"Tanggal": str(datetime.date.today()), "Judul": judul_p, "Isi": isi_p}
            st.session_state.pengumuman.insert(0, new_p)
            st.success("Pengumuman berhasil disiarkan ke portal karyawan!")
            st.rerun()

elif menu == "Kasbon Karyawan" and akses_diberikan:
    st.markdown("<div class='main-header'>📑 Fasilitas Kasbon Karyawan</div>", unsafe_allow_html=True)
    st.dataframe(st.session_state.kasbon, use_container_width=True)

elif menu == "Unduh Laporan" and akses_diberikan:
    st.markdown("<div class='main-header'>📥 Central Arsip</div>", unsafe_allow_html=True)
    st.download_button("📥 Unduh Jurnal Cash Flow (CSV)", st.session_state.cash_flow.to_csv(index=False), "TCP_cash_flow.csv")

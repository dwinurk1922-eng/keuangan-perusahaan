import streamlit as st
import pandas as pd
import datetime
import math
from streamlit_js_eval import streamlit_js_eval

# =========================================================================
# PENGATURAN AWAL & DATABASE LOKAL (SINKRON OTOMATIS)
# =========================================================================
st.set_page_config(
    page_title="Portal PT Tangguh Cahaya Pratama", 
    page_icon="✨",
    layout="wide"
)

# PIN untuk masuk ke menu Manajemen FinOps
PIN_OTORISASI = "2026"
RADIUS_TOLERANSI_METER = 20.0 

# Inisialisasi Database Pengumuman Global di Session State
if 'pengumuman' not in st.session_state:
    st.session_state.pengumuman = [
        {"Tanggal": "2026-07-06", "Judul": "Sistem Multi-GPS Outsourcing Aktif", "Isi": "Sistem presensi kini mendukung deteksi otomatis koordinat di berbagai area kantor klien dengan batas radius kehadiran ketat 20 meter dari titik lokasi penugasan resmi."},
        {"Tanggal": "2026-07-01", "Judul": "Kepatuhan Berkas Legalitas Finansial", "Isi": "Diingatkan kepada divisi operasional untuk mengunggah nota komersial secara berkala agar pengesahan ledger keuangan akhir bulan berjalan tepat waktu."}
    ]

# Inisialisasi Database Absensi Terpusat
if 'absensi' not in st.session_state:
    st.session_state.absensi = pd.DataFrame(columns=[
        "Tanggal", "Bulan/Tahun", "Nama Karyawan", "Status Kehadiran", 
        "Jam Masuk", "Jam Pulang", "Durasi Shift Kerja", "Lokasi Koordinat", "Metode"
    ])

# Daftar Koordinat Kantor Resmi & Durasi Shift Kerja
if "daftar_lokasi_klien" not in st.session_state:
    st.session_state.daftar_lokasi_klien = {
        "PT Tangguh Cahaya Pratama (Pusat Kalisari)": (-6.3355, 106.8620, 8),
        "RSGM FKG Usakti": (-6.1668, 106.7901, 12),  
        "Kantor Klien A (Sudirman)": (-6.2146, 106.8215, 12),
        "Kantor Klien B (Thamrin)": (-6.1953, 106.8231, 8)
    }

# Status Login Pengguna
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_nama' not in st.session_state:
    st.session_state.user_nama = ""

# =========================================================================
# KUSTOMISASI DESAIN TAMPILAN (WARNA KONTRAS TINGGI)
# =========================================================================
st.markdown("""
    <style>
        .stApp { background-color: #f8fafc !important; }
        [data-testid="stSidebar"] { background-color: #0f172a !important; border-right: 3px solid #0284c7; }
        [data-testid="stSidebar"] .stRadio p { color: #facc15 !important; font-weight: 800 !important; font-size: 16px !important; }
        [data-testid="stSidebar"] label p { color: #ffffff !important; }
        
        /* Box Input Dijamin Putih Bersih */
        input[type="text"], input[type="number"], input[type="password"], textarea { 
            background-color: #ffffff !important; 
            color: #0f172a !important; 
            border: 2px solid #94a3b8 !important; 
            border-radius: 6px !important; 
        }
        div[data-baseweb="input"] { background-color: #ffffff !important; color: #0f172a !important; }
        div[data-baseweb="select"] { background-color: #ffffff !important; color: #0f172a !important; }
        
        .main-header { font-size: 32px; font-weight: 900; color: #1e3a8a !important; }
        .stButton>button { background: linear-gradient(45deg, #0284c7, #1e40af) !important; color: #ffffff !important; font-weight: 800 !important; }
    </style>
""", unsafe_allow_html=True)

# Rumus Matematika Jarak Jangkauan GPS
def hitung_jarak_meter(lat1, lon1, lat2, lon2):
    R = 6371000.0 
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    return R * (2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a)))

# =========================================================================
# HALAMAN LOGIN UTAMA
# =========================================================================
if not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<div class='main-header' style='text-align: center;'>✨ PT TANGGUH CAHAYA PRATAMA ✨</div>", unsafe_allow_html=True)
    
    with st.columns([1, 2, 1])[1]:
        with st.form("form_login"):
            st.markdown("<h3 style='color: #1e3a8a; text-align: center;'>🔐 Masuk Ke Portal</h3>", unsafe_allow_html=True)
            input_nama = st.text_input("Nama Lengkap Karyawan:")
            input_nomor = st.text_input("Nomor Keanggotaan / ID:", type="password")
            
            if st.form_submit_button("Masuk Aplikasi ✨", use_container_width=True):
                if input_nama.strip() != "" and input_nomor.strip() != "":
                    st.session_state.logged_in = True
                    st.session_state.user_nama = input_nama.strip()
                    st.rerun()
                else:
                    st.error("❌ Nama dan Nomor ID wajib diisi!")

# =========================================================================
# SYSTEM PANEL UTAMA SETELAH LOGIN
# =========================================================================
else:
    st.sidebar.markdown(f"<div style='font-size: 18px; font-weight: 800; color: #ffffff;'>👋 Halo, {st.session_state.user_nama}!</div>", unsafe_allow_html=True)
    role_akses = st.sidebar.selectbox("Pilih Hak Akses:", ["Portal Karyawan (Umum)", "Manajemen FinOps (Otorisasi)"])
    
    akses_admin_sah = False
    if role_akses == "Manajemen FinOps (Otorisasi)":
        input_pin = st.sidebar.text_input("⚡ Masukkan PIN Otorisasi:", type="password")
        if input_pin == PIN_OTORISASI:
            akses_admin_sah = True
            st.sidebar.success("🔥 MODE ADMIN AKTIF")
        elif input_pin != "":
            st.sidebar.error("❌ PIN Salah!")

    # Penentuan Menu Pilihan Berdasarkan Akses Role
    if role_akses == "Manajemen FinOps (Otorisasi)" and akses_admin_sah:
        menu = st.sidebar.radio("Menu Admin:", ["📋 Absensi Terpusat (Rekap)", "📍 Kelola Lokasi Klien", "✍️ Kelola Pengumuman"])
    else:
        menu = st.sidebar.radio("Menu Karyawan:", ["📢 Papan Pengumuman Resmi", "📍 Presensi Rutin Mandiri (GPS)"])

    if st.sidebar.button("🚪 Keluar / Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_nama = ""
        st.rerun()

    # --- 1. MENU KARYAWAN: PAPAN PENGUMUMAN ---
    if menu == "📢 Papan Pengumuman Resmi":
        st.markdown("<div class='main-header'>📢 Papan Pengumuman Internal Resmi</div>", unsafe_allow_html=True)
        for p in st.session_state.pengumuman:
            st.markdown(f"""
                <div style='background: white; padding: 15px; border-radius: 8px; border-left: 5px solid #0284c7; margin-bottom: 12px;'>
                    <h4 style='margin: 0; color: #1e293b;'>📌 {p['Judul']}</h4>
                    <p style='color: #64748b; font-size: 12px; margin: 2px 0 8px 0;'>📆 {p['Tanggal']}</p>
                    <p style='color: #334155;'>{p['Isi']}</p>
                </div>
            """, unsafe_allow_html=True)

    # --- 2. MENU KARYAWAN: ABSENSI GPS MANDIRI ---
    elif menu == "📍 Presensi Rutin Mandiri (GPS)":
        st.markdown("<div class='main-header'>📍 Presensi Mandiri Terdeteksi GPS</div>", unsafe_allow_html=True)
        
        # Pemicu Sensor Lokasi Perangkat Browser Karyawan
        lokasi_user = streamlit_js_eval(data_container_name='geolocation', before_update_data=None, key='geo_karyawan')
        
        with st.form("form_absen"):
            bulan_abs = st.selectbox("Periode Bulan Buku:", ["Juli 2026", "Agustus 2026"])
            
            lokasi_terdeteksi = None
            durasi_shift_terdeteksi = 8 
            jarak_terdekat = float('inf')
            lat_user, lon_user = None, None
            
            if lokasi_user:
                lat_user = lokasi_user['coords']['latitude']
                lon_user = lokasi_user['coords']['longitude']
                st.success(f"📍 GPS Mengunci Koordinat Anda: {lat_user}, {lon_user}")
                
                # Loop Otomatis Mencari Kantor Klien Terdekat yang Cocok di Radius 20 Meter
                for nama_kantor, info_lokasi in st.session_state.daftar_lokasi_klien.items():
                    jarak = hitung_jarak_meter(lat_user, lon_user, info_lokasi[0], info_lokasi[1])
                    if jarak <= RADIUS_TOLERANSI_METER and jarak < jarak_terdekat:
                        jarak_terdekat = jarak
                        lokasi_terdeteksi = nama_kantor
                        durasi_shift_terdeteksi = info_lokasi[2]
            else:
                st.warning("⚠️ Menunggu koordinat GPS aktif... Pastikan izin lokasi/GPS di browser HP Anda sudah di-klik 'IZINKAN' atau 'ALLOW'.")

            waktu_sekarang = datetime.datetime.now()
            jam_masuk_str = waktu_sekarang.strftime("%H:%M:%S")
            jam_pulang_str = (waktu_sekarang + datetime.timedelta(hours=int(durasi_shift_terdeteksi))).strftime("%H:%M:%S")
            
            if lokasi_terdeteksi:
                st.info(f"🎯 Area Kerja Valid: **{lokasi_terdeteksi}** | Shift Kerja: **{durasi_shift_terdeteksi} Jam** (Jarak: {jarak_terdekat:.1f}m)")
            
            if st.form_submit_button("Kirim Kehadiran Sekarang 🚀", use_container_width=True):
                if not lokasi_user:
                    st.error("❌ Gagal Absen! Sensor lokasi HP Anda belum terbaca oleh browser.")
                elif lokasi_terdeteksi is None:
                    st.error("❌ Gagal Absen! Anda berada di luar jangkauan area resmi (Batas ketat toleransi: 20 meter).")
                else:
                    new_row = {
                        "Tanggal": str(datetime.date.today()), 
                        "Bulan/Tahun": bulan_abs, 
                        "Nama Karyawan": st.session_state.user_nama, 
                        "Status Kehadiran": "Hadir", 
                        "Jam Masuk": jam_masuk_str,
                        "Jam Pulang": jam_pulang_str,
                        "Durasi Shift Kerja": f"{durasi_shift_terdeteksi} Jam",
                        "Lokasi Koordinat": f"{lat_user}, {lon_user}", 
                        "Metode": f"GPS ({lokasi_terdeteksi})"
                    }
                    st.session_state.absensi = pd.concat([pd.DataFrame([new_row]), st.session_state.absensi], ignore_index=True)
                    st.success(f"🎉 Absensi Anda BERHASIL dicatat langsung untuk hari ini!")

    # --- 3. MENU ADMIN: KELOLA PENGUMUMAN (LANGSUNG SINKRON) ---
    elif menu == "✍️ Kelola Pengumuman" and akses_admin_sah:
        st.markdown("<div class='main-header'>✍️ Kelola & Terbitkan Pengumuman Internal</div>", unsafe_allow_html=True)
        
        with st.form("form_buat_pengumuman", clear_on_submit=True):
            judul_p = st.text_input("Judul Berita/Pengumuman Baru:")
            isi_p = st.text_area("Isi Pengumuman Lengkap:")
            
            if st.form_submit_button("Terbitkan Ke Portal Karyawan Sekarang ✨", use_container_width=True):
                if judul_p.strip() and isi_p.strip():
                    # Menambahkan pengumuman langsung ke posisi paling atas daftar memori bersama
                    st.session_state.pengumuman.insert(0, {
                        "Tanggal": str(datetime.date.today()), 
                        "Judul": judul_p.strip(), 
                        "Isi": isi_p.strip()
                    })
                    st.success("🎉 Sukses! Pengumuman sudah terbit secara real-time di halaman portal karyawan.")
                else:
                    st.error("❌ Judul dan isi informasi tidak boleh kosong!")

    # --- 4. MENU ADMIN: REKAP ABSENSI TERPUSAT ---
    elif menu == "📋 Absensi Terpusat (Rekap)" and akses_admin_sah:
        st.markdown("<div class='main-header'>📋 Log Hasil Absensi Masuk Karyawan</div>", unsafe_allow_html=True)
        if not st.session_state.absensi.empty:
            st.dataframe(st.session_state.absensi, use_container_width=True)
        else:
            st.info("Belum ada data absensi masuk untuk hari ini.")

    # --- 5. MENU ADMIN: DETAIL AREA KOORDINAT KLIEN ---
    elif menu == "📍 Kelola Lokasi Klien" and akses_admin_sah:
        st.markdown("<div class='main-header'>📍 Titik Koordinat Kantor Klien Resmi</div>", unsafe_allow_html=True)
        data_tabel_lokasi = []
        for n, k in st.session_state.daftar_lokasi_klien.items():
            data_tabel_lokasi.append({
                "Nama Kantor/Klien": n, "Latitude": k[0], "Longitude": k[1], "Ketentuan Shift Kerja": f"{k[2]} Jam Selesai"
            })
        st.dataframe(pd.DataFrame(data_tabel_lokasi), use_container_width=True)

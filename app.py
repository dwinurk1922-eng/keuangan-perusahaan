import streamlit as st
import pandas as pd
import datetime
import math
import google.generativeai as genai
from streamlit_js_eval import streamlit_js_eval

# =========================================================================
# PENGATURAN DATABASE, AI, & MULTI-LOKASI KANTOR KLIEN (RADIUS 20 METER)
# =========================================================================
SHEETS_URL = "https://docs.google.com/spreadsheets/d/1VDqISHpjg8OWWPzl1NWOcc9V6j_o6Zw2/edit?usp=sharing"
GEMINI_API_KEY = "AQ.Ab8RN6J6P_ygWhv1BVnR7cZDTwU4F3bhuTPKXHi1BB_ZzUikGg"

if "PIN_OTORISASI" in st.secrets:
    PIN_OTORISASI = str(st.secrets["PIN_OTORISASI"])
else:
    PIN_OTORISASI = "2026"

# DAFTAR LOKASI ABSENSI (KANTOR PUSAT & SEMUA KANTOR KLIEN OUTSOURCING)
KANTOR_KLIEN = {
    "PT Tangguh Cahaya Pratama (Pusat Kalisari)": (-6.3355, 106.8620),
    "Kantor Klien A (Contoh Sudirman)": (-6.2146, 106.8215),
    "Kantor Klien B (Contoh Thamrin)": (-6.1953, 106.8231),
    "Kantor Klien C (Contoh Kuningan)": (-6.2242, 106.8294)
}

RADIUS_TOLERANSI_METER = 20.0 
# =========================================================================

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

st.set_page_config(
    page_title="Portal PT Tangguh Cahaya Pratama", 
    page_icon="✨",
    layout="wide"
)

# KUSTOMISASI DESAIN ULTRA-KONTRAS & PREMIUM (ANTI-TENGGELAM)
st.markdown("""
    <style>
        /* Mengubah latar belakang halaman utama agar teks hitam terlihat sangat kontras */
        .stApp { 
            background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%); 
        }
        
        /* SIDEBAR: Menggunakan warna Biru Safir Gelap yang Solid & Tegas */
        [data-testid="stSidebar"] { 
            background-color: #0b4570 !important; 
            border-right: 3px solid #0ea5e9; 
        }
        
        /* MENYALAKAN TULISAN MENU RADIO (SIDEBAR) MENJADI KUNING LEMON TAJAM */
        [data-testid="stSidebar"] .stRadio p {
            color: #fffb00 !important; 
            font-weight: 800 !important; 
            font-size: 16px !important; 
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8) !important;
            letter-spacing: 0.3px;
            margin-bottom: 2px;
        }
        
        /* MENGUBAH TULISAN JUDUL DROPDOWN / SELECTBOX DI SIDEBAR JADI PUTIH TEBAL */
        [data-testid="stSidebar"] label p {
            color: #ffffff !important; 
            font-weight: 800 !important;
            font-size: 15px !important;
            text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.9) !important;
        }
        
        /* Teks biasa atau petunjuk teks di dalam sidebar */
        [data-testid="stSidebar"] .stMarkdown p {
            color: #ffffff !important;
            font-weight: 600 !important;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5) !important;
        }

        /* Desain Header Utama Utama */
        .main-header { 
            font-size: 36px; 
            font-weight: 900; 
            background: linear-gradient(45deg, #0b4570, #ea580c); 
            -webkit-background-clip: text; 
            -webkit-text-fill-color: transparent; 
            margin-bottom: 5px; 
            letter-spacing: 0.5px;
        }
        
        .sub-header { 
            font-size: 16px; 
            color: #475569; 
            font-weight: 600; 
            margin-bottom: 25px; 
        }
        
        /* Kartu Finansial Dashboard */
        .metric-card-custom { 
            background: white; 
            padding: 24px; 
            border-radius: 14px; 
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.08); 
            border-top: 6px solid #0284c7; 
        }
        
        /* Mengubah Desain Tombol Menjadi Berwarna Gradasi Tajam dan Jelas */
        .stButton>button { 
            background: linear-gradient(45deg, #0ea5e9, #0284c7) !important; 
            color: #ffffff !important; 
            border: none !important; 
            border-radius: 8px !important; 
            font-weight: 800 !important; 
            font-size: 15px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
            transition: all 0.2s ease; 
        }
        
        .stButton>button:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 10px 15px -3px rgba(2, 132, 199, 0.4) !important; 
        }
        
        /* Penanda Status Badge */
        .badge-admin { 
            background-color: #e11d48; 
            color: #ffffff !important; 
            padding: 8px 16px; 
            border-radius: 20px; 
            font-size: 13px; 
            font-weight: 900; 
            display: inline-block; 
            text-align: center; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.15);
        }
        
        .badge-karyawan { 
            background-color: #16a34a; 
            color: #ffffff !important; 
            padding: 8px 16px; 
            border-radius: 20px; 
            font-size: 13px; 
            font-weight: 900; 
            display: inline-block; 
            text-align: center; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.15);
        }
    </style>
""", unsafe_allow_html=True)

# Fungsi Hitung Jarak Akurat Formula Haversine
def hitung_jarak_meter(lat1, lon1, lat2, lon2):
    R = 6371000.0 
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

# Fungsi Baca Data via URL CSV Eksport
def read_data_via_csv(sheet_name, fallback_cols):
    try:
        csv_url = SHEETS_URL.split("/edit")[0] + f"/gviz/tq?tqx=out:csv&sheet={sheet_name}"
        return pd.read_csv(csv_url)
    except:
        return pd.DataFrame(columns=fallback_cols)

# Sinkronisasi Data Awal
if 'karyawan' not in st.session_state:
    st.session_state.karyawan = read_data_via_csv("Data_Karyawan", ["ID Karyawan", "Nama Karyawan", "Nomor Keanggotaan", "Jabatan", "Gaji Pokok", "Tunjangan"])
if 'cash_flow' not in st.session_state:
    st.session_state.cash_flow = read_data_via_csv("Cash_Flow", ["Tanggal", "Kategori", "Keterangan / Deskripsi", "Pendapatan (Kas Masuk)", "Pengeluaran (Kas Keluar)"])
if 'absensi' not in st.session_state:
    st.session_state.absensi = read_data_via_csv("Absensi", ["Tanggal", "Bulan/Tahun", "Nama Karyawan", "Status Kehadiran", "Lokasi Koordinat", "Metode"])
if 'kasbon' not in st.session_state:
    st.session_state.kasbon = read_data_via_csv("Kasbon_Karyawan", ["Tanggal", "Nama Karyawan", "Divisi / Bagian", "Jumlah Kasbon", "Status Pengembalian"])

if 'pengumuman' not in st.session_state:
    st.session_state.pengumuman = [
        {"Tanggal": "2026-07-06", "Judul": "Sistem Multi-GPS Outsourcing Aktif", "Isi": "Sistem presensi kini mendukung deteksi otomatis koordinat di berbagai area kantor klien dengan batas radius kehadiran ketat 20 meter dari titik lokasi penugasan resmi."},
        {"Tanggal": "2026-07-01", "Judul": "Kepatuhan Berkas Legalitas Finansial", "Isi": "Diingatkan kepada divisi operasional untuk mengunggah nota komersial secara berkala agar pengesahan ledger keuangan akhir bulan berjalan tepat waktu."}
    ]

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_nama' not in st.session_state:
    st.session_state.user_nama = ""

# =========================================================================
# LALUAN 1: FORM LOGIN UTAMA
# =========================================================================
if not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div class='main-header' style='text-align: center;'>✨ PT TANGGUH CAHAYA PRATAMA ✨</div>", unsafe_allow_html=True)
        st.markdown("<div class='sub-header' style='text-align: center;'>Sistem Informasi FinOps & Portal Presensi Mandiri (Outsourcing Multi-Client)</div>", unsafe_allow_html=True)
        
        with st.columns([1, 2, 1])[1]:
            with st.form("form_login_karyawan"):
                st.markdown("<h3 style='color: #0b4570; text-align: center;'>🔐 Masuk ke Sistem</h3>", unsafe_allow_html=True)
                input_nama = st.text_input("Nama Lengkap Karyawan:")
                input_nomor = st.text_input("Nomor Keanggotaan / ID:", type="password")
                
                st.markdown("<br>", unsafe_allow_html=True)
                tombol_masuk = st.form_submit_button("Masuk Aplikasi ✨", use_container_width=True)
                
                if tombol_masuk:
                    nama_clean = input_nama.strip().lower()
                    nomor_clean = input_nomor.strip()
                    
                    if nama_clean == "dwi nur kolipah" and nomor_clean == "2334/TG/008":
                        st.session_state.logged_in = True
                        st.session_state.user_nama = "Dwi Nur Kolipah"
                        st.success("✅ Login Berhasil! Membuka Portal...")
                        st.rerun()
                    else:
                        df_k = st.session_state.karyawan
                        if not df_k.empty and "Nama Karyawan" in df_k.columns:
                            kolom_kunci = "Nomor Keanggotaan" if "Nomor Keanggotaan" in df_k.columns else "ID Karyawan"
                            valid_user = df_k[(df_k["Nama Karyawan"].str.lower() == nama_clean) & (df_k[kolom_kunci].astype(str) == nomor_clean)]
                            
                            if not valid_user.empty:
                                st.session_state.logged_in = True
                                st.session_state.user_nama = valid_user.iloc[0]["Nama Karyawan"]
                                st.success("✅ Login Berhasil!")
                                st.rerun()
                            else:
                                st.error("❌ Nama atau Nomor Keanggotaan tidak terdaftar dalam sistem perusahaan!")
                        else:
                            st.error("❌ Nama atau Nomor Keanggotaan tidak terdaftar dalam sistem perusahaan!")

# =========================================================================
# LALUAN 2: HALAMAN UTAMA APLIKASI (LOGIN SUKSES)
# =========================================================================
else:
    st.sidebar.markdown(f"<div style='font-size: 22px; font-weight: 800; color: #ffffff; text-shadow: 1px 1px 3px #000; margin-bottom: 10px;'>👋 Halo, {st.session_state.user_nama}!</div>", unsafe_allow_html=True)
    role_akses = st.sidebar.selectbox("Pilih Hak Akses Sistem:", ["Portal Karyawan (Umum)", "Manajemen FinOps (Otorisasi)"])

    akses_admin_sah = False
    if role_akses == "Manajemen FinOps (Otorisasi)":
        input_pin = st.sidebar.text_input("⚡ Masukkan PIN Otorisasi:", type="password")
        if input_pin == PIN_OTORISASI:
            akses_admin_sah = True
            st.sidebar.markdown("<center style='margin: 10px 0;'><span class='badge-admin'>🔥 MODE ADMIN AKTIF</span></center>", unsafe_allow_html=True)
        elif input_pin != "":
            st.sidebar.error("❌ PIN Otorisasi Salah!")
    else:
        st.sidebar.markdown("<center style='margin: 10px 0;'><span class='badge-karyawan'>🍃 PORTAL KARYAWAN</span></center>", unsafe_allow_html=True)

    st.sidebar.markdown("<br>", unsafe_allow_html=True)

    if role_akses == "Manajemen FinOps (Otorisasi)" and akses_admin_sah:
        st.sidebar.markdown("<div style='background-color: #ffffff; padding: 12px; border-radius: 8px; border-left: 5px solid #ea580c; color: #1e293b !important; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.15);'>⭐ <b>Finance Manager:</b><br><span style='color: #0b4570;'>Dwi Nur Kolipah, S.H.</span></div>", unsafe_allow_html=True)
        st.sidebar.markdown("<br>", unsafe_allow_html=True)
        menu = st.sidebar.radio("Pilih Modul FinOps (Admin):", [
            "📊 Dashboard Executive", 
            "💸 Manajemen Cash Flow (Ada AI)", 
            "👥 Data Master Karyawan", 
            "📋 Absensi Terpusat (Rekap)", 
            "📑 Kasbon Karyawan", 
            "✍️ Kelola Pengumuman"
        ])
    else:
        menu = st.sidebar.radio("Pilih Menu Karyawan:", [
            "📢 Papan Pengumuman Resmi", 
            "📍 Presensi Rutin Mandiri (GPS)"
        ])

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Keluar / Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_nama = ""
        st.rerun()

    # --- MENU KARYAWAN: PENGUMUMAN ---
    if menu == "📢 Papan Pengumuman Resmi":
        st.markdown("<div class='main-header'>📢 Papan Pengumuman Internal Resmi</div>", unsafe_allow_html=True)
        for p in st.session_state.pengumuman:
            st.markdown(f"""
                <div style='background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); border-left: 5px solid #ea580c; margin-bottom: 15px;'>
                    <h4 style='margin: 0; color: #1e293b;'>📌 {p['Judul']}</h4>
                    <p style='color: #64748b; font-size: 12px; margin: 5px 0 10px 0;'>📆 Diterbitkan pada: {p['Tanggal']}</p>
                    <p style='color: #334155; line-height: 1.6;'>{p['Isi']}</p>
                </div>
            """, unsafe_allow_html=True)

    # --- MENU KARYAWAN: ABSENSI MULTI-GPS DETEKSI OTOMATIS KANTOR KLIEN ---
    elif menu == "📍 Presensi Rutin Mandiri (GPS)":
        st.markdown("<div class='main-header'>📍 Sistem Presensi Multi-GPS Area Kerja Outsourcing</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:15px; color:#475569; font-weight: 500;'>Sistem akan mendeteksi penempatan penugasan Anda secara otomatis dalam batas jangkauan aman <b>{RADIUS_TOLERANSI_METER} meter</b>.</div>", unsafe_allow_html=True)
        
        lokasi_user = streamlit_js_eval(data_container_name='geolocation', before_update_data=None, key='geo')
        
        with st.form("form_absen_mandiri"):
            st.write(f"Nama Karyawan: **{st.session_state.user_nama}**")
            bulan_abs = st.selectbox("Periode Bulan Buku:", ["Juli 2026", "Agustus 2026", "September 2026"])
            
            lokasi_terdeteksi = None
            jarak_terdekat = float('inf')
            
            if lokasi_user:
                lat_user = lokasi_user['coords']['latitude']
                lon_user = lokasi_user['coords']['longitude']
                st.success(f"📍 GPS Mengunci Koordinat Anda: {lat_user}, {lon_user}")
                
                for nama_kantor, koordinat in KANTOR_KLIEN.items():
                    jarak = hitung_jarak_meter(lat_user, lon_user, koordinat[0], koordinat[1])
                    if jarak <= RADIUS_TOLERANSI_METER and jarak < jarak_terdekat:
                        jarak_terdekat = jarak
                        lokasi_terdeteksi = nama_kantor
            else:
                lat_user, lon_user = None, None
                st.warning("⚠️ Menunggu sinyal GPS perangkat Anda aktif untuk memetakan penempatan...")

            if st.form_submit_button("Kirim Kehadiran Sekarang 🚀", use_container_width=True):
                if not lokasi_user:
                    st.error("❌ Gagal Absen! Sensor lokasi perangkat Anda belum aktif.")
                elif lokasi_terdeteksi is None:
                    st.error(f"❌ Gagal Absen! Anda berada di luar area penugasan resmi (Jarak ke PT TCP Pusat adalah {hitung_jarak_meter(lat_user, lon_user, KANTOR_KLIEN['PT Tangguh Cahaya Pratama (Pusat Kalisari)'][0], KANTOR_KLIEN['PT Tangguh Cahaya Pratama (Pusat Kalisari)'][1]):.1f} meter. Batas jangkauan maksimal wajib di bawah 20 meter).")
                else:
                    new_row = {
                        "Tanggal": str(datetime.date.today()), 
                        "Bulan/Tahun": bulan_abs, 
                        "Nama Karyawan": st.session_state.user_nama, 
                        "Status Kehadiran": "Hadir", 
                        "Lokasi Koordinat": f"{lat_user}, {lon_user}", 
                        "Metode": f"GPS ({lokasi_terdeteksi} - Jarak: {jarak_terdekat:.1f}m)"
                    }
                    st.session_state.absensi = pd.concat([pd.DataFrame([new_row]), st.session_state.absensi], ignore_index=True)
                    st.success(f"🎉 Presensi VALID & Berhasil Disimpan! Terdeteksi di lokasi: {lokasi_terdeteksi} (Jarak: {jarak_terdekat:.1f} meter dari titik utama).")

    # --- MENU ADMIN: DATA MASTER KARYAWAN ---
    elif menu == "👥 Data Master Karyawan" and akses_admin_sah:
        st.markdown("<div class='main-header'>👥 Master Data Karyawan (Admin)</div>", unsafe_allow_html=True)
        
        with st.expander("➕ Tambah Data Karyawan Baru Langsung", expanded=True):
            with st.form("form_tambah_karyawan", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    new_id = st.text_input("ID Karyawan (Misal: TCP-010)")
                    new_nama = st.text_input("Nama Lengkap Karyawan")
                    new_no_anggota = st.text_input("Nomor Keanggotaan Login (Misal: 2334/TG/010)")
                with col2:
                    new_jabatan = st.text_input("Jabatan / Divisi")
                    new_gapok = st.number_input("Gaji Pokok (Rp)", min_value=0, step=50000)
                    new_tunjangan = st.number_input("Tunjangan Jabatan (Rp)", min_value=0, step=10000)
                
                if st.form_submit_button("Simpan Data Karyawan Baru 💾", use_container_width=True):
                    if new_id and new_nama and new_no_anggota:
                        row_baru = pd.DataFrame([{
                            "ID Karyawan": new_id, "Nama Karyawan": new_nama,
                            "Nomor Keanggotaan": new_no_anggota, "Jabatan": new_jabatan,
                            "Gaji Pokok": new_gapok, "Tunjangan": new_tunjangan
                        }])
                        st.session_state.karyawan = pd.concat([st.session_state.karyawan, row_baru], ignore_index=True)
                        st.success(f"🎉 Sukses! Karyawan baru bernama '{new_nama}' telah ditambahkan.")
                        st.rerun()
                    else:
                        st.error("❌ Gagal Menyimpan! Kolom ID, Nama, dan Nomor Keanggotaan wajib diisi.")

        st.write("### 📋 Tabel Database Karyawan Saat Ini")
        st.dataframe(st.session_state.karyawan, use_container_width=True)
        st.download_button(
            label="📥 Unduh Backup Jurnal Karyawan Terbaru (CSV)",
            data=st.session_state.karyawan.to_csv(index=False),
            file_name="Data_Karyawan_Terbaru.csv",
            mime="text/csv",
            use_container_width=True
        )

    # --- MENU ADMIN LAINNYA ---
    elif menu == "📊 Dashboard Executive" and akses_admin_sah:
        st.markdown("<div class='main-header'>📊 Dashboard Utama & Posisi Keuangan (Admin)</div>", unsafe_allow_html=True)
        total_masuk = pd.to_numeric(st.session_state.cash_flow["Pendapatan (Kas Masuk)"], errors='coerce').fillna(0).sum()
        total_keluar = pd.to_numeric(st.session_state.cash_flow["Pengeluaran (Kas Keluar)"], errors='coerce').fillna(0).sum()
        laba = total_masuk - total_keluar
        
        col1, col2, col3 = st.columns(3)
        with col1: st.markdown(f"<div class='metric-card-custom' style='border-top-color: #16a34a;'><p style='color: #475569; font-size:14px; font-weight:bold; margin:0;'>📈 CASH IN</p><h2 style='color:#16a34a; margin:10px 0 0 0;'>Rp {total_masuk:,.0f}</h2></div>", unsafe_allow_html=True)
        with col2: st.markdown(f"<div class='metric-card-custom' style='border-top-color: #e11d48;'><p style='color: #475569; font-size:14px; font-weight:bold; margin:0;'>📉 CASH OUT</p><h2 style='color:#e11d48; margin:10px 0 0 0;'>Rp {total_keluar:,.0f}</h2></div>", unsafe_allow_html=True)
        with col3: st.markdown(f"<div class='metric-card-custom' style='border-top-color: #0284c7;'><p style='color: #475569; font-size:14px; font-weight:bold; margin:0;'>💰 NET PROFIT</p><h2 style='color:#0284c7; margin:10px 0 0 0;'>Rp {laba:,.0f}</h2></div>", unsafe_allow_html=True)

    elif menu == "💸 Manajemen Cash Flow (Ada AI)" and akses_admin_sah:
        st.markdown("<div class='main-header'>💸 Manajemen Arus Kas Korporat (Admin)</div>", unsafe_allow_html=True)
        st.dataframe(st.session_state.cash_flow, use_container_width=True)

    elif menu == "📋 Absensi Terpusat (Rekap)" and akses_admin_sah:
        st.markdown("<div class='main-header'>📋 Log Database Absensi Terintegrasi (Admin)</div>", unsafe_allow_html=True)
        st.dataframe(st.session_state.absensi, use_container_width=True)

    elif menu == "📑 Kasbon Karyawan" and akses_admin_sah:
        st.markdown("<div class='main-header'>📑 Fasilitas Kasbon Karyawan (Admin)</div>", unsafe_allow_html=True)
        st.dataframe(st.session_state.kasbon, use_container_width=True)

    elif menu == "✍️ Kelola Pengumuman" and akses_admin_sah:
        st.markdown("<div class='main-header'>✍️ Kelola Pengumuman Internal Kantor (Admin)</div>", unsafe_allow_html=True)
        with st.form("form_buat_pengumuman", clear_on_submit=True):
            judul_p = st.text_input("Judul Pengumuman Baru")
            isi_p = st.text_area("Isi Informasi")
            if st.form_submit_button("Terbitkan Ke Portal Karyawan ✨"):
                st.session_state.pengumuman.insert(0, {"Tanggal": str(datetime.date.today()), "Judul": judul_p, "Isi": isi_p})
                st.success("Pengumuman berhasil disiarkan!")
                st.rerun()

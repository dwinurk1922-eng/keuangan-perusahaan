import streamlit as st
import pandas as pd
import datetime
import google.generativeai as genai
from PIL import Image

# =========================================================================
# PENGATURAN DATABASE & AI ANDA (ISI DI SINI)
SHEETS_URL = "https://docs.google.com/spreadsheets/d/1VDqISHpjg8OWWPzl1NWOcc9V6j_o6Zw2/edit?usp=sharing&ouid=117398658595436431688&rtpof=true&sd=true"
GEMINI_API_KEY = "AQ.Ab8RN6J6P_ygWhv1BVnR7cZDTwU4F3bhuTPKXHi1BB_ZzUikGg"
# =========================================================================

# Konfigurasi AI Gemini
if GEMINI_API_KEY and GEMINI_API_KEY != "MASUKKAN_API_KEY_GEMINI_ANDA_DISINI":
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
        /* Mengubah font utama dan background internal */
        .reportview-container {
            background: #f8f9fa;
        }
        /* Style untuk Header Utama */
        .main-header {
            font-size: 32px;
            font-weight: bold;
            color: #1E3A8A; /* Navy Blue */
            margin-bottom: 5px;
        }
        .sub-header {
            font-size: 16px;
            color: #4B5563; /* Muted Grey */
            margin-bottom: 25px;
        }
        /* Custom Card untuk Metrik Keuangan */
        .metric-card {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            border-left: 5px solid #1E3A8A;
        }
        /* Gaya Sidebar */
        .sidebar-title {
            font-size: 20px;
            font-weight: bold;
            color: #1E3A8A;
        }
    </style>
""", unsafe_index=False)

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

# Inisialisasi Session State
if 'cash_flow' not in st.session_state:
    st.session_state.cash_flow = df_cf_sheets if df_cf_sheets is not None else pd.DataFrame(columns=["Tanggal", "Kategori", "Keterangan / Deskripsi", "Pendapatan (Kas Masuk)", "Pengeluaran (Kas Keluar)"])

if 'kasbon' not in st.session_state:
    st.session_state.kasbon = df_kb_sheets if df_kb_sheets is not None else pd.DataFrame(columns=["Tanggal", "Nama Karyawan", "Divisi / Bagian", "Jumlah Kasbon", "Status Pengembalian"])

if 'karyawan' not in st.session_state:
    st.session_state.karyawan = df_kry_sheets if df_kry_sheets is not None else pd.DataFrame(columns=["ID Karyawan", "Nama Karyawan", "Jabatan", "Gaji Pokok", "Tunjangan"])

if 'absensi' not in st.session_state:
    st.session_state.absensi = df_abs_sheets if df_abs_sheets is not None else pd.DataFrame(columns=["Tanggal", "Bulan/Tahun", "Nama Karyawan", "Status Kehadiran"])

if 'payroll' not in st.session_state:
    st.session_state.payroll = df_pr_sheets if df_pr_sheets is not None else pd.DataFrame(columns=["Tanggal Payroll", "Bulan/Tahun", "Nama Karyawan", "Total Hadir", "Total Gaji Dibayar"])

# Fungsi Analisis Nota Pakai AI
def analisis_nota_dengan_ai(foto_input):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        gambar = Image.open(foto_input)
        perintah = """
        Kamu adalah robot akuntan. Analisis foto nota/kuitansi/invoice ini.
        Berikan jawaban HANYA dalam format teks singkat seperti di bawah ini, jangan berikan penjelasan lain:
        Tanggal: YYYY-MM-DD (sesuaikan dengan tanggal di nota, jika tidak ada pakai tanggal hari ini)
        Keterangan: (Nama toko/keperluan pendek, misal: SPBU Pertamina atau Rumah Makan Padang)
        Total: (Angka nominal totalnya saja tanpa titik/Rp, misal: 150000)
        """
        response = model.generate_content([perintah, gambar])
        return response.text
    except Exception as e:
        return f"Error AI: {str(e)}"

# ==========================================
# SIDEBAR PANEL - IDENTITAS PERUSAHAAN & MANAGER
# ==========================================
st.sidebar.markdown("<div class='sidebar-title'>🏢 PT TANGGUH CAHAYA PRATAMA</div>", unsafe_allow_html=True)
st.sidebar.caption("Sistem Informasi FinOps & Payroll Enterprise")
st.sidebar.markdown("---")

# Profil Manajer Keuangan (Resmi)
st.sidebar.markdown("### 🧑‍💼 Otorisasi Sistem")
st.sidebar.info("""
    **Finance Manager:** **Dwi Nur Kolipah, S.H.** *Corporate Finance & Legal Compliance*
""")

st.sidebar.markdown("---")
menu = st.sidebar.radio("Pilih Modul Aplikasi:", ["Dashboard Eksekutif", "Manajemen Cash Flow (Ada AI)", "Data Master Karyawan", "Absensi Harian", "Payroll & Penggajian", "Kasbon Karyawan", "Unduh Laporan"])
st.sidebar.markdown("---")
st.sidebar.caption("🤖 FinOps AI Core v2.4 | Status: Terhubung")

# ==========================================
# 1. MENU DASHBOARD EKSEKUTIF
# ==========================================
if menu == "Dashboard Eksekutif":
    st.markdown("<div class='main-header'>📊 Dashboard Utama & Posisi Keuangan</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>PT TANGGUH CAHAYA PRATAMA</div>", unsafe_allow_html=True)
    
    # Menghitung Total dari Dataframe
    total_masuk = pd.to_numeric(st.session_state.cash_flow["Pendapatan (Kas Masuk)"]).sum()
    total_keluar = pd.to_numeric(st.session_state.cash_flow["Pengeluaran (Kas Keluar)"]).sum()
    laba_bersih = total_masuk - total_keluar

    # Tampilan Widget Utama Bergaya Eksekutif
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Arus Kas Masuk (Pemasukan)", value=f"Rp {total_masuk:,.0f}", delta="Pemasukan Aktif")
    with col2:
        st.metric(label="Total Arus Kas Keluar (Pengeluaran)", value=f"Rp {total_keluar:,.0f}", delta=f"-Rp {total_keluar:,.0f}", delta_color="inverse")
    with col3:
        # Menentukan delta warna untuk laba bersih
        status_laba = "Surplus" if laba_bersih >= 0 else "Defisit"
        st.metric(label="Laba / Rugi Bersih Bersih", value=f"Rp {laba_bersih:,.0f}", delta=status_laba)
    
    st.markdown("---")
    
    # Informasi neraca ringkas korporasi
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.subheader("📋 Ringkasan Otorisasi Manajer")
        st.write("Semua pengeluaran operasional, struktur penggajian karyawan, dan pencairan dana yang tertera pada sistem ini telah melalui peninjauan hukum tata kelola keuangan perusahaan oleh **Dwi Nur Kolipah, S.H.** selaku Manajer Keuangan PT Tangguh Cahaya Pratama.")
    with col_info2:
        st.subheader("💡 Petunjuk Operasional")
        st.write("Gunakan menu navigasi di sebelah kiri untuk berpindah modul, mulai dari pemindaian kuitansi otomatis berbasis AI, pengisian absensi harian, hingga otomatisasi pembagian kompensasi/payroll bulanan.")

# ==========================================
# 2. MENU CASH FLOW
# ==========================================
elif menu == "Manajemen Cash Flow (Ada AI)":
    st.markdown("<div class='main-header'>💸 Manajemen Arus Kas Korporat</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Modul Pengisian Kas & Ekstraksi Nota Otomatis Berbasis AI Flash</div>", unsafe_allow_html=True)
    
    col_ai, col_manual = st.columns(2)
    
    with col_ai:
        st.subheader("📸 Scan Nota Otomatis via AI")
        file_nota = st.file_uploader("Unggah Foto Nota/Struk Belanja Perusahaan (Format JPG/PNG)", type=["jpg", "jpeg", "png"])
        if file_nota is not None:
            st.image(file_nota, caption="Pratinjau Dokumen Nota", width=250)
            if st.button("Mulai Baca Nota Pakai AI"):
                with st.spinner("AI sedang mengekstrak data dari nota perusahaan..."):
                    hasil_ai = analisis_nota_dengan_ai(file_nota)
                    st.text_area("Hasil Ekstraksi FinOps AI:", hasil_ai, height=120)
                    st.info("💡 Silakan salin informasi di atas ke form input manual di sebelah kanan untuk validasi akhir.")

    with col_manual:
        st.subheader("➕ Form Validasi Transaksi Jurnal")
        with st.form("form_cf", clear_on_submit=True):
            tgl = st.date_input("Tanggal Transaksi", datetime.date.today())
            kat = st.selectbox("Kategori Akun", ["Pengeluaran", "Pendapatan"])
            ket = st.text_input("Keterangan / Deskripsi Penggunaan Dana")
            jml = st.number_input("Nominal Transaksi (Rp)", min_value=0, step=5000)
            
            if st.form_submit_button("Simpan Ke Ledger Perusahaan"):
                val_masuk = jml if kat == "Pendapatan" else 0
                val_keluar = jml if kat == "Pengeluaran" else 0
                new_data = {"Tanggal": str(tgl), "Kategori": kat, "Keterangan / Deskripsi": ket, "Pendapatan (Kas Masuk)": val_masuk, "Pengeluaran (Kas Keluar)": val_keluar}
                st.session_state.cash_flow = pd.concat([pd.DataFrame([new_data]), pd.DataFrame(st.session_state.cash_flow)], ignore_index=True)
                st.success("Transaksi berhasil dibukukan ke dalam sistem!")
                st.rerun()

    st.markdown("---")
    st.subheader("📜 Histori Buku Besar Buku Arus Kas")
    st.dataframe(st.session_state.cash_flow, use_container_width=True)

# ==========================================
# 3. MENU DATA KARYAWAN
# ==========================================
elif menu == "Data Master Karyawan":
    st.markdown("<div class='main-header'>👥 Master Data Karyawan</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Manajemen Database Karyawan Aktif PT Tangguh Cahaya Pratama</div>", unsafe_allow_html=True)
    
    col_form, col_table = st.columns([1, 2])
    
    with col_form:
        st.subheader("➕ Registrasi Karyawan Baru")
        with st.form("form_karyawan", clear_on_submit=True):
            id_kry = st.text_input("ID Karyawan", value=f"TCP-{len(st.session_state.karyawan)+1:03d}")
            nama_kry = st.text_input("Nama Lengkap")
            jabatan = st.text_input("Jabatan / Divisi Kerja")
            gapok = st.number_input("Gaji Pokok Utama / Bulan (Rp)", min_value=0, step=100000)
            tunjangan = st.number_input("Tunjangan Tetap / Bulan (Rp)", min_value=0, step=50000)
            
            if st.form_submit_button("Validasi & Simpan"):
                if nama_kry != "":
                    new_kry = {"ID Karyawan": id_kry, "Nama Karyawan": nama_kry, "Jabatan": jabatan, "Gaji Pokok": gapok, "Tunjangan": tunjangan}
                    st.session_state.karyawan = pd.concat([pd.DataFrame([new_kry]), pd.DataFrame(st.session_state.karyawan)], ignore_index=True)
                    st.success(f"Karyawan baru atas nama {nama_kry} berhasil terdaftar.")
                    st.rerun()

    with col_table:
        st.subheader("📋 File Database Karyawan")
        st.dataframe(st.session_state.karyawan, use_container_width=True)

# ==========================================
# 4. MENU ABSENSI KARYAWAN
# ==========================================
elif menu == "Absensi Harian":
    st.markdown("<div class='main-header'>📅 Modul Rekapitulasi Absensi</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Pencatatan Presensi Kehadiran Karyawan Sebagai Komponen Penggajian</div>", unsafe_allow_html=True)
    
    if st.session_state.karyawan.empty:
        st.warning("⚠️ Database karyawan masih kosong. Daftarkan karyawan di menu 'Data Master Karyawan' terlebih dahulu.")
    else:
        col_abs1, col_abs2 = st.columns([1, 2])
        
        with col_abs1:
            st.subheader("📝 Pencatatan Presensi")
            with st.form("form_absensi", clear_on_submit=True):
                tgl_abs = st.date_input("Tanggal Kerja", datetime.date.today())
                bulan_abs = st.selectbox("Periode Buku", ["Januari 2026", "Februari 2026", "Maret 2026", "April 2026", "Mei 2026", "Juni 2026", "Juli 2026", "Agustus 2026", "September 2026", "Oktober 2026", "November 2026", "Desember 2026"])
                list_karyawan = st.session_state.karyawan["Nama Karyawan"].tolist()
                karyawan_abs = st.selectbox("Nama Personel", list_karyawan)
                status_abs = st.selectbox("Status Kehadiran", ["Hadir", "Sakit (Surat Dokter)", "Izin Resmi", "Alpa / Tanpa Keterangan"])
                
                if st.form_submit_button("Submit Absen"):
                    cek_absen = st.session_state.absensi[(st.session_state.absensi["Tanggal"] == str(tgl_abs)) & (st.session_state.absensi["Nama Karyawan"] == karyawan_abs)]
                    if not cek_absen.empty:
                        st.error(f"❌ Presensi {karyawan_abs} untuk tanggal {tgl_abs} sudah tercatat sebelumnya!")
                    else:
                        new_abs = {"Tanggal": str(tgl_abs), "Bulan/Tahun": bulan_abs, "Nama Karyawan": karyawan_abs, "Status Kehadiran": status_abs}
                        st.session_state.absensi = pd.concat([pd.DataFrame([new_abs]), pd.DataFrame(st.session_state.absensi)], ignore_index=True)
                        st.success(f"✅ Kehadiran {karyawan_abs} terekam.")
                        st.rerun()

        with col_abs2:
            st.subheader("📋 Log Kehadiran Karyawan")
            st.dataframe(st.session_state.absensi, use_container_width=True)

# ==========================================
# 5. MENU PAYROLL & GAJI
# ==========================================
elif menu == "Payroll & Penggajian":
    st.markdown("<div class='main-header'>💸 Sistem Payroll & Pencairan Kompensasi</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Kalkulasi Gaji Otomatis Berdasarkan Tingkat Kehadiran Personel Bulanan</div>", unsafe_allow_html=True)
    
    if st.session_state.karyawan.empty:
        st.warning("⚠️ Data master karyawan kosong.")
    else:
        col_pay_form, col_pay_hist = st.columns([1, 2])
        
        with col_pay_form:
            st.subheader("✍️ Pemrosesan Gaji")
            with st.form("form_payroll", clear_on_submit=True):
                tgl_bayar = st.date_input("Tanggal Pengeluaran Kas Gaji", datetime.date.today())
                bulan_pilih = st.selectbox("Periode Pembayaran Buku", ["Januari 2026", "Februari 2026", "Maret 2026", "April 2026", "Mei 2026", "Juni 2026", "Juli 2026", "Agustus 2026", "September 2026", "Oktober 2026", "November 2026", "Desember 2026"])
                
                list_karyawan = st.session_state.karyawan["Nama Karyawan"].tolist()
                karyawan_pilih = st.selectbox("Pilih Personel", list_karyawan)
                hari_kerja_sebulan = st.number_input("Target Hari Kerja Perusahaan Sebulan", min_value=1, value=25, step=1)
                
                # Integrasi data absensi otomatis
                db_absen_karyawan = st.session_state.absensi[
                    (st.session_state.absensi["Nama Karyawan"] == karyawan_pilih) & 
                    (st.session_state.absensi["Bulan/Tahun"] == bulan_pilih) & 
                    (st.session_state.absensi["Status Kehadiran"] == "Hadir")
                ]
                total_masuk = len(db_absen_karyawan)
                
                # Ambil Gaji Master
                data_kry_terpilih = st.session_state.karyawan[st.session_state.karyawan["Nama Karyawan"] == karyawan_pilih].iloc[0]
                gapok_full = data_kry_terpilih["Gaji Pokok"]
                tunjangan_full = data_kry_terpilih["Tunjangan"]
                
                # Formula Gaji Proporsional Berbasis Kehadiran
                gaji_maksimal = gapok_full + tunjangan_full
                if total_masuk > 0:
                    total_gaji_bersih = int((total_masuk / hari_kerja_sebulan) * gaji_maksimal)
                else:
                    total_gaji_bersih = 0
                
                if total_gaji_bersih > gaji_maksimal:
                    total_gaji_bersih = int(gaji_maksimal)
                
                st.markdown(f"ℹ️ **Kehadiran Efektif ({bulan_pilih}):** {total_masuk} Hari Kerja")
                st.write(f"💵 **Gaji Pokok Kontrak:** Rp {gapok_full:,.0f}")
                st.write(f"➕ **Tunjangan Kontrak:** Rp {tunjangan_full:,.0f}")
                st.info(f"💰 **Total Gaji Dicairkan (Net):** Rp {total_gaji_bersih:,.0f}")
                
                if st.form_submit_button("Otorisasi & Cairkan Gaji"):
                    # 1. Simpan Riwayat Payroll
                    new_pay = {"Tanggal Payroll": str(tgl_bayar), "Bulan/Tahun": bulan_pilih, "Nama Karyawan": karyawan_pilih, "Total Hadir": f"{total_masuk} Hari", "Total Gaji Dibayar": total_gaji_bersih}
                    st.session_state.payroll = pd.concat([pd.DataFrame([new_pay]), pd.DataFrame(st.session_state.payroll)], ignore_index=True)
                    
                    # 2. Otomatis Potong Kas Utama
                    new_cash_out = {
                        "Tanggal": str(tgl_bayar),
                        "Kategori": "Pengeluaran",
                        "Keterangan / Deskripsi": f"Beban Payroll Karyawan - {karyawan_pilih} ({bulan_pilih})",
                        "Pendapatan (Kas Masuk)": 0,
                        "Pengeluaran (Kas Keluar)": total_gaji_bersih
                    }
                    st.session_state.cash_flow = pd.concat([pd.DataFrame([new_cash_out]), pd.DataFrame(st.session_state.cash_flow)], ignore_index=True)
                    
                    st.success(f"Dana payroll untuk {karyawan_pilih} berhasil ditransfer dan dibukukan ke pengeluaran kas!")
                    st.rerun()
                    
        with col_pay_hist:
            st.subheader("📜 Riwayat Penggajian Resmi (Payroll Ledger)")
            st.dataframe(st.session_state.payroll, use_container_width=True)

# ==========================================
# 6. MENU KASBON
# ==========================================
elif menu == "Kasbon Karyawan":
    st.markdown("<div class='main-header'>📑 Fasilitas Kasbon Karyawan</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Pencatatan Pinjaman Sementara Dan Status Pengembalian Finansial</div>", unsafe_allow_html=True)
    
    with st.form("form_kasbon", clear_on_submit=True):
        tgl_kb = st.date_input("Tanggal Pengajuan Kasbon", datetime.date.today())
        nm_kb = st.text_input("Nama Karyawan Pemohon")
        div_kb = st.text_input("Divisi / Jabatan")
        jml_kb = st.number_input("Nominal Pinjaman Kasbon (Rp)", min_value=0, step=50000)
        status_kb = st.selectbox("Status Tagihan", ["Belum Lunas", "Lunas"])
        
        if st.form_submit_button("Proses Dokumen Pinjaman"):
            new_kb = {"Tanggal": str(tgl_kb), "Nama Karyawan": nm_kb, "Divisi / Bagian": div_kb, "Jumlah Kasbon": jml_kb, "Status Pengembalian": status_kb}
            st.session_state.kasbon = pd.concat([pd.DataFrame([new_kb]), pd.DataFrame(st.session_state.kasbon)], ignore_index=True)
            st.success("Pencatatan kasbon berhasil diverifikasi ke dalam sistem.")
            st.rerun()
            
    st.dataframe(st.session_state.kasbon, use_container_width=True)

# ==========================================
# 7. MENU UNDUH LAPORAN
# ==========================================
elif menu == "Unduh Laporan":
    st.markdown("<div class='main-header'>📥 Central Arsip & Ekspor Laporan</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Ekspor Data FinOps Perusahaan Ke Format Dokumen CSV Resmi</div>", unsafe_allow_html=True)
    
    st.write("Silakan unduh dokumen di bawah ini untuk keperluan dokumentasi fisik korporat atau kebutuhan audit internal:")
    
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button("📥 Unduh Jurnal Cash Flow (CSV)", st.session_state.cash_flow.to_csv(index=False), "TCP_cash_flow.csv", "text/csv")
        st.download_button("📥 Unduh Database Master Karyawan (CSV)", st.session_state.karyawan.to_csv(index=False), "TCP_data_karyawan.csv", "text/csv")
    with col_dl2:
        st.download_button("📥 Unduh Berkas Absensi (CSV)", st.session_state.absensi.to_csv(index=False), "TCP_absensi.csv", "text/csv")
        st.download_button("📥 Unduh Laporan Riwayat Payroll (CSV)", st.session_state.payroll.to_csv(index=False), "TCP_riwayat_payroll.csv", "text/csv")

import streamlit as st
import pandas as pd
import datetime

# =========================================================================
# LALU TEMPELKAN/PASTE LINK GOOGLE SHEETS ANDA DI DALAM TANDA PETIK DI BAWAH INI:
SHEETS_URL = "https://docs.google.com/spreadsheets/d/1VDqISHpjg8OWWPzl1NWOcc9V6j_o6Zw2/edit?usp=sharing&ouid=117398658595436431688&rtpof=true&sd=true"
# =========================================================================

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="FinOps Central - Finance Manager App", layout="wide")

# Fungsi untuk membaca data dari Google Sheets secara real-time
@st.cache_data(ttl=10)
def load_data_from_sheets(sheet_name):
    try:
        # Mengubah link share Google Sheets biasa menjadi format pembacaan CSV/Data
        csv_url = SHEETS_URL.replace("/edit?usp=sharing", f"/gviz/tq?tqx=out:csv&sheet={sheet_name}")
        csv_url = csv_url.split("/edit")[0] + f"/gviz/tq?tqx=out:csv&sheet={sheet_name}"
        return pd.read_csv(csv_url)
    except Exception as e:
        return None

# 2. PROSES PENGAMBILAN DATA UTAMA
df_cf_sheets = load_data_from_sheets("Cash_Flow")
df_kb_sheets = load_data_from_sheets("Kasbon_Karyawan")

# Validasi data cadangan jika koneksi sheets gagal
if 'cash_flow' not in st.session_state:
    if df_cf_sheets is not None and not df_cf_sheets.empty:
        st.session_state.cash_flow = df_cf_sheets
    else:
        st.session_state.cash_flow = pd.DataFrame([
            {"Tanggal": "2026-07-01", "Kategori": "Pendapatan", "Keterangan": "Invoice Client A - Projek Jasa Hukum", "Jumlah": 150000000},
            {"Tanggal": "2026-07-02", "Kategori": "Pengeluaran", "Keterangan": "Sewa Ruang Kantor Bulanan", "Jumlah": 25000000},
        ])

if 'kasbon' not in st.session_state:
    if df_kb_sheets is not None and not df_kb_sheets.empty:
        st.session_state.kasbon = df_kb_sheets
    else:
        st.session_state.kasbon = pd.DataFrame([
            {"Tanggal": "2026-07-03", "Nama Karyawan": "Budi Santoso", "Divisi / Bagian": "Marketing", "Jumlah Kasbon": 5000000, "Status Pengembalian": "Belum Settle"},
            {"Tanggal": "2026-07-06", "Nama Karyawan": "Siti Aminah", "Divisi / Bagian": "Operations", "Jumlah Kasbon": 2000000, "Status Pengembalian": "Sudah Settle"}
        ])

# 3. FUNGSI UTAMA HELPER
def hitung_neraca_dan_pajak():
    df_cf = pd.DataFrame(st.session_state.cash_flow)
    
    # Menyamakan nama kolom agar tidak error
    if "Pendapatan (Kas Masuk)" in df_cf.columns:
        total_masuk = pd.to_numeric(df_cf["Pendapatan (Kas Masuk)"], errors='coerce').sum()
        total_keluar = pd.to_numeric(df_cf["Pengeluaran (Kas Keluar)"], errors='coerce').sum()
    else:
        total_masuk = df_cf[df_cf['Kategori'] == 'Pendapatan']['Jumlah'].sum()
        total_keluar = df_cf[df_cf['Kategori'] == 'Pengeluaran']['Jumlah'].sum()
        
    laba_bersih = total_masuk - total_keluar
    estimasi_pajak = laba_bersih * 0.11 if laba_bersih > 0 else 0
    return total_masuk, total_keluar, laba_bersih, estimasi_pajak

# 4. SIDEBAR NAVIGASI
st.sidebar.title("🚀 FinOps Central")
st.sidebar.subheader("Finance Manager Dashboard")
st.sidebar.info("✅ Status Database: Terhubung Permanen ke Google Sheets")
menu = st.sidebar.radio("Pilih Modul:", ["Dashboard & Neraca", "Manajemen Cash Flow", "Kasbon Karyawan & Jurnal", "Unduh Rekapan"])

# 5. HALAMAN 1: DASHBOARD & NERACA
if menu == "Dashboard & Neraca":
    st.title("📊 Dashboard Utama & Posisi Keuangan")
    t_masuk, t_keluar, laba, pajak = hitung_neraca_dan_pajak()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Kas Masuk", f"Rp {t_masuk:,.0f}")
    col2.metric("Total Kas Keluar", f"Rp {t_keluar:,.0f}")
    col3.metric("Laba/Rugi Bersih", f"Rp {laba:,.0f}")
    col4.metric("Estimasi Pajak (PPh)", f"Rp {pajak:,.0f}")
    
    st.markdown("---")
    
    st.subheader("🏛️ Ikhtisar Neraca Sederhana (Balance Sheet)")
    col_aset, col_liabilitas = st.columns(2)
    
    with col_aset:
        st.write("**ASET (Harta)**")
        st.info(f"Kas dan Setara Kas: Rp {laba:,.0f}")
        st.write(f"**Total Aset: Rp {laba:,.0f}**")
        
    with col_liabilitas:
        st.write("**KEWAJIBAN & EKUITAS**")
        st.warning(f"Utang Pajak (Estimasi): Rp {pajak:,.0f}")
        st.success(f"Modal Akhir (Ekuitas): Rp {laba - pajak:,.0f}")
        st.write(f"**Total Pasiva: Rp {laba:,.0f}**")

# 6. HALAMAN 2: CASH FLOW
elif menu == "Manajemen Cash Flow":
    st.title("💸 Manajemen Cash Flow (Arus Kas)")
    
    with st.expander("➕ Tambah Transaksi Arus Kas Baru"):
        with st.form("form_cf", clear_on_submit=True):
            tgl = st.date_input("Tanggal Transaksi", datetime.date.today())
            kat = st.selectbox("Kategori", ["Pendapatan", "Pengeluaran"])
            ket = st.text_input("Keterangan/Deskripsi Transaksi")
            jml = st.number_input("Jumlah (Rp)", min_value=0, step=100000)
            
            submit = st.form_submit_button("Simpan Transaksi")
            if submit and ket:
                if "Pendapatan (Kas Masuk)" in st.session_state.cash_flow.columns:
                    val_masuk = jml if kat == "Pendapatan" else 0
                    val_keluar = jml if kat == "Pengeluaran" else 0
                    new_data = {"Tanggal": str(tgl), "Kategori": kat, "Keterangan / Deskripsi": ket, "Pendapatan (Kas Masuk)": val_masuk, "Pengeluaran (Kas Keluar)": val_keluar}
                else:
                    new_data = {"Tanggal": str(tgl), "Kategori": kat, "Keterangan": ket, "Jumlah": jml}
                    
                st.session_state.cash_flow = pd.concat([pd.DataFrame([new_data]), pd.DataFrame(st.session_state.cash_flow)], ignore_index=True)
                st.success("Transaksi Berhasil Dicatat di Aplikasi!")
                st.rerun()

    st.subheader("Histori Transaksi Kas")
    st.dataframe(st.session_state.cash_flow, use_container_width=True)

# 7. HALAMAN 3: KASBON KARYAWAN
elif menu == "Kasbon Karyawan & Jurnal":
    st.title("🧑‍💼 Jurnal Besar Kasbon Karyawan")
    
    with st.expander("📝 Form Pengajuan Kasbon Baru"):
        with st.form("form_kasbon", clear_on_submit=True):
            nama = st.text_input("Nama Karyawan")
            divisi = st.selectbox("Divisi", ["Finance", "Marketing", "HR", "Operations", "IT"])
            jumlah_kb = st.number_input("Jumlah Kasbon (Rp)", min_value=0, step=50000)
            
            submit_kb = st.form_submit_button("Ajukan Kasbon")
            if submit_kb and nama:
                # Menyesuaikan nama kolom template excel
                if "Nama Karyawan" in st.session_state.kasbon.columns:
                    new_kb = {"Tanggal": str(datetime.date.today()), "Nama Karyawan": nama, "Divisi / Bagian": divisi, "Jumlah Kasbon": jumlah_kb, "Status Pengembalian": "Belum Settle"}
                else:
                    new_kb = {"Karyawan": nama, "Divisi": divisi, "Jumlah": jumlah_kb, "Status": "Belum Settle", "Tanggal": str(datetime.date.today())}
                
                st.session_state.kasbon = pd.concat([pd.DataFrame([new_kb]), pd.DataFrame(st.session_state.kasbon)], ignore_index=True)
                st.success("Kasbon berhasil diajukan!")
                st.rerun()

    st.subheader("Daftar Piutang Kasbon Karyawan")
    df_kasbon = pd.DataFrame(st.session_state.kasbon)
    st.dataframe(df_kasbon, use_container_width=True)
    
    st.subheader("🔧 Update Status Settlement Kasbon")
    col_status_name = "Status Pengembalian" if "Status Pengembalian" in df_kasbon.columns else "Status"
    col_karyawan_name = "Nama Karyawan" if "Nama Karyawan" in df_kasbon.columns else "Karyawan"
    col_jumlah_name = "Jumlah Kasbon" if "Jumlah Kasbon" in df_kasbon.columns else "Jumlah"
    
    karyawan_list = df_kasbon[df_kasbon[col_status_name] == 'Belum Settle'][col_karyawan_name].tolist()
    
    if karyawan_list:
        pilih_karyawan = st.selectbox("Pilih Karyawan yang mengembalikan nota:", karyawan_list)
        if st.button("Settle Kasbon Karyawan"):
            st.session_state.kasbon.loc[st.session_state.kasbon[col_karyawan_name] == pilih_karyawan, col_status_name] = 'Sudah Settle'
            nilai_kasbon = st.session_state.kasbon.loc[st.session_state.kasbon[col_karyawan_name] == pilih_karyawan, col_jumlah_name].values[0]
            
            if "Pendapatan (Kas Masuk)" in st.session_state.cash_flow.columns:
                new_cf_from_kb = {"Tanggal": str(datetime.date.today()), "Kategori": "Pengeluaran", "Keterangan / Deskripsi": f"Settlement Kasbon a.n {pilih_karyawan}", "Pendapatan (Kas Masuk)": 0, "Pengeluaran (Kas Keluar)": nilai_kasbon}
            else:
                new_cf_from_kb = {"Tanggal": str(datetime.date.today()), "Kategori": "Pengeluaran", "Keterangan": f"Settlement Kasbon a.n {pilih_karyawan}", "Jumlah": nilai_kasbon}
                
            st.session_state.cash_flow = pd.concat([pd.DataFrame([new_cf_from_kb]), pd.DataFrame(st.session_state.cash_flow)], ignore_index=True)
            st.success(f"Kasbon {pilih_karyawan} selesai diproses!")
            st.rerun()
    else:
        st.info("Semua kasbon karyawan telah diselesaikan.")

# 8. HALAMAN 4: UNDUH REKAPAN
elif menu == "Unduh Rekapan":
    st.title("📥 Unduh Laporan Keuangan")
    st.write("Unduh data transaksi terbaru untuk di-sinkronisasikan kembali ke Google Sheets atau arsip luring.")

    def convert_df_to_excel():
        import io
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            pd.DataFrame(st.session_state.cash_flow).to_excel(writer, sheet_name='Cash_Flow', index=False)
            pd.DataFrame(st.session_state.kasbon).to_excel(writer, sheet_name='Kasbon_Karyawan', index=False)
        return output.getvalue()

    excel_data = convert_df_to_excel()
    st.download_button(
        label="🟢 Unduh Seluruh Laporan Keuangan Aktual (Excel)",
        data=excel_data,
        file_name=f"Laporan_Aktual_FinOps_{datetime.date.today()}.xlsx",
        mime="application/vnd.ms-excel"
    )

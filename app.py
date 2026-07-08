import streamlit as st
import hashlib
import jwt
import datetime
import os
import pandas as pd
import geopy.distance

# ==========================
# 🔐 Autentikasi JWT + RBAC
# ==========================
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")

USERS = {
    "admin": {"password": hashlib.sha256("admin123".encode()).hexdigest(), "role": "admin"},
    "manager": {"password": hashlib.sha256("manager123".encode()).hexdigest(), "role": "manager"},
    "staff": {"password": hashlib.sha256("staff123".encode()).hexdigest(), "role": "staff"}
}

def create_token(username, role):
    payload = {
        "user": username,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        st.error("Token expired, silakan login ulang.")
        return None
    except jwt.InvalidTokenError:
        st.error("Token tidak valid.")
        return None

def login():
    st.sidebar.title("🔐 Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        hashed = hashlib.sha256(password.encode()).hexdigest()
        if username in USERS and USERS[username]["password"] == hashed:
            role = USERS[username]["role"]
            token = create_token(username, role)
            st.session_state["token"] = token
            st.success(f"Selamat datang {username} ({role})!")
        else:
            st.error("Login gagal")

# ==========================
# 📊 Modul Keuangan & Payroll
# ==========================
def laporan_keuangan():
    st.header("📊 Laporan Keuangan (Dummy Data)")
    data = {
        "Bulan": ["Jan", "Feb", "Mar"],
        "Pemasukan": [10000000, 12000000, 9000000],
        "Pengeluaran": [7000000, 8000000, 6000000],
    }
    df = pd.DataFrame(data)
    df["Saldo"] = df["Pemasukan"] - df["Pengeluaran"]
    st.dataframe(df)

def payroll():
    st.header("💼 Payroll & Slip Gaji")
    karyawan = st.text_input("Nama Karyawan")
    hari_masuk = st.number_input("Jumlah Hari Masuk", min_value=0)
    gaji_harian = st.number_input("Gaji per Hari", min_value=0)
    kasbon = st.number_input("Kasbon", min_value=0)
    if st.button("Hitung Gaji"):
        total = (hari_masuk * gaji_harian) - kasbon
        st.success(f"Gaji Bulanan {karyawan}: Rp {total:,.0f}")
        st.write(f"Slip Gaji: {karyawan} | Hari Masuk: {hari_masuk} | Kasbon: Rp {kasbon:,.0f} | Total: Rp {total:,.0f}")

# ==========================
# 📍 Absensi GPS & Rekap
# ==========================
OFFICE_LOCATION = (-6.2297, 106.8123)  # Jakarta

def absensi():
    st.header("📍 Absensi GPS")
    lat = st.number_input("Latitude")
    lon = st.number_input("Longitude")
    if st.button("Absensi"):
        distance = geopy.distance.distance((lat, lon), OFFICE_LOCATION).m
        if distance < 100:  # radius 100 meter
            st.success("Absensi berhasil!")
        else:
            st.error("Anda berada di luar lokasi absensi!")

def rekap_absen():
    st.header("🗂️ Rekap Absensi (Dummy Data)")
    data = {"Nama":["Andi","Budi"],"Hari Masuk":[20,18]}
    df = pd.DataFrame(data)
    st.dataframe(df)

# ==========================
# 📢 Pengumuman Admin
# ==========================
def pengumuman(role):
    st.header("📢 Pengumuman")
    if role == "admin":
        msg = st.text_area("Tulis Pengumuman")
        if st.button("Publikasikan"):
            st.session_state["announcement"] = msg
            st.success("Pengumuman berhasil dibuat!")
    else:
        st.info(st.session_state.get("announcement", "Belum ada pengumuman"))

# ==========================
# 🚀 Main App
# ==========================
st.set_page_config(page_title="Office Finance App", layout="wide")

if "token" not in st.session_state:
    login()
else:
    payload = verify_token(st.session_state["token"])
    if payload:
        role = payload["role"]
        menu = st.sidebar.selectbox("Menu", ["Dashboard","Laporan Keuangan","Payroll","Absensi","Rekap Absen","Pengumuman"])
        
        if menu == "Dashboard":
            st.title("🏢 Office Finance App")
            st.write(f"Selamat datang {payload['user']} ({role})")
        
        elif menu == "Laporan Keuangan":
            if role in ["admin","manager"]:
                laporan_keuangan()
            else:
                st.error("Akses ditolak: hanya admin/manager.")
        
        elif menu == "Payroll":
            if role in ["admin","manager"]:
                payroll()
            else:
                st.error("Akses ditolak.")
        
        elif menu == "Absensi":
            if role in ["staff","manager","admin"]:
                absensi()
        
        elif menu == "Rekap Absen":
            if role in ["admin","manager"]:
                rekap_absen()
            else:
                st.error("Akses ditolak.")
        
        elif menu == "Pengumuman":
            pengumuman(role)

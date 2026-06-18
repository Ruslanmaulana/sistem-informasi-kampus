import streamlit as st
import sqlite3
import math
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash

# ==========================================
# 1. KONFIGURASI HALAMAN & DATABASE
# ==========================================
st.set_page_config(page_title="Sistem Informasi Kampus", layout="wide")

def get_db_connection():
    # Menggunakan nama database asli Anda: data_kampus.db
    conn = sqlite3.connect('data_kampus.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# ==========================================
# 2. LOGIKA OOP & ALGORITMA (Bawaan Anda)
# ==========================================
class Person:
    def __init__(self, nama):
        self._nama = nama  # Menerapkan Prinsip Encapsulation (Pilar OOP)
    def get_nama(self):
        return self._nama

class MahasiswaObj(Person):  # Menerapkan Prinsip Inheritance (Pilar OOP)
    def __init__(self, nim, nama, tanggal_lahir, jenis_kelamin, alamat, no_hp, email, nama_fakultas, nama_prodi, kelas, status, id_fakultas, id_prodi):
        super().__init__(nama)
        self.nim = nim
        self.tanggal_lahir = tanggal_lahir
        self.jenis_kelamin = jenis_kelamin
        self.alamat = alamat
        self.no_hp = no_hp
        self.email = email
        self.nama_fakultas = nama_fakultas
        self.nama_prodi = nama_prodi
        self.kelas = kelas
        self.status = status
        self.id_fakultas = id_fakultas
        self.id_prodi = id_prodi

    def to_dict(self):
        """Mengonversi data objek menjadi dictionary agar mudah dibaca oleh Streamlit/Pandas Dataframe"""
        return {
            "nim": self.nim, 
            "nama": self.get_nama(), 
            "tanggal_lahir": self.tanggal_lahir,
            "jenis_kelamin": self.jenis_kelamin, 
            "alamat": self.alamat, 
            "no_hp": self.no_hp,
            "email": self.email, 
            "nama_fakultas": self.nama_fakultas, 
            "nama_prodi": self.nama_prodi,
            "kelas": self.kelas, 
            "status": self.status, 
            "id_fakultas": self.id_fakultas, 
            "id_prodi": self.id_prodi
        }

def bubble_sort_mhs(data_list):
    """Algoritma Sorting murni Python untuk mengurutkan nama Mahasiswa A-Z"""
    n = len(data_list)
    for i in range(n):
        for j in range(0, n-i-1):
            if data_list[j]['nama'].lower() > data_list[j+1]['nama'].lower():
                data_list[j], data_list[j+1] = data_list[j+1], data_list[j]
    return data_list

# ==========================================
# 3. MANAJEMEN SESSION STATUS (PENGGANTI FLASK SESSION)
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = ""

# ==========================================
# 4. TAMPILAN HALAMAN LOGIN
# ==========================================
if not st.session_state['logged_in']:
    st.markdown("<h2 style='text-align: center;'>🔐 Login Sistem Informasi Kampus</h2>", unsafe_allow_html=True)
    
    # Membuat form box login di tengah halaman
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            login_btn = st.button("Login Ke Sistem", type="primary", use_container_width=True)
            
            if login_btn:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
                user = cursor.fetchone()
                conn.close()
                
                if user and check_password_hash(user['password'], password):
                    st.session_state['logged_in'] = True
                    st.session_state['user_name'] = user['name']
                    st.success(f"Selamat datang, {user['name']}!")
                    st.rerun()
                else:
                    st.error("Email atau Password salah!")

# ==========================================
# 5. TAMPILAN SISTEM UTAMA (SETELAH LOGIN)
# ==========================================
else:
    # Navigasi Menu Menu di Sidebar Kiri
    st.sidebar.title(f"👤 {st.session_state['user_name']}")
    st.sidebar.markdown("---")
    menu = st.sidebar.radio("Menu Navigasi", ["Dashboard", "Data Mahasiswa", "Logout"])
    
    if menu == "Logout":
        st.session_state['logged_in'] = False
        st.session_state['user_name'] = ""
        st.rerun()
        
    elif menu == "Dashboard":
        st.title("📊 Dashboard Analisis")
        st.markdown("---")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Kalkulasi Ringkasan Informasi Kampus
        total_fakultas = cursor.execute('SELECT COUNT(*) FROM fakultas').fetchone()[0]
        total_prodi = cursor.execute('SELECT COUNT(*) FROM program_studi').fetchone()[0]
        total_mhs = cursor.execute('SELECT COUNT(*) FROM mahasiswa').fetchone()[0]
        
        # Tampilan Grid Widget ala AdminLTE
        col1, col2, col3 = st.columns(3)
        col1.metric(label="Total Fakultas", value=total_fakultas)
        col2.metric(label="Total Program Studi", value=total_prodi)
        col3.metric(label="Total Mahasiswa Terdaftar", value=total_mhs)
        
        st.markdown("---")
        st.subheader("📌 5 Registrasi Mahasiswa Terbaru")
        
        cursor.execute('SELECT nim, nama, status FROM mahasiswa ORDER BY nim DESC LIMIT 5')
        recent_rows = cursor.fetchall()
        conn.close()
        
        if recent_rows:
            df_recent = pd.DataFrame([dict(r) for r in recent_rows])
            st.table(df_recent)
            
    elif menu == "Data Mahasiswa":
        st.title("🎓 Manajemen Data Mahasiswa")
        st.markdown("---")
        
        # FITUR INPUT TAMBAH DATA MAHASISWA (Modal Dropdown / Expander)
        with st.expander("➕ Formulir Tambah Mahasiswa Baru"):
            with st.form("form_tambah_mahasiswa"):
                col_left, col_right = st.columns(2)
                
                with col_left:
                    nim = st.text_input("NIM (Nomor Induk Mahasiswa)")
                    nama_lengkap = st.text_input("Nama Lengkap")
                    tgl_lahir = st.date_input("Tanggal Lahir")
                    jk = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
                
                with col_right:
                    alamat = st.text_area("Alamat Tinggal")
                    no_hp = st.text_input("Nomor Handphone")
                    email_mhs = st.text_input("Email Mahasiswa")
                    
                    # Ambil daftar program studi langsung dari database untuk Dropdown
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute('SELECT * FROM program_studi')
                    prodi_data = cursor.fetchall()
                    conn.close()
                    
                    dict_prodi = {r['nama_prodi']: (r['id'], r['id_fakultas']) for r in prodi_data}
                    pilihan_prodi = st.selectbox("Pilihan Program Studi", list(dict_prodi.keys()))
                
                submit_btn = st.form_submit_button("Simpan Data Ke Sistem", type="primary")
                
                if submit_btn:
                    if not nim or not nama_lengkap:
                        st.error("NIM dan Nama Lengkap wajib diisi!")
                    else:
                        id_prodi, id_fakultas = dict_prodi[pilihan_prodi]
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        try:
                            cursor.execute('''
                                INSERT INTO mahasiswa (nim, nama, tanggal_lahir, jenis_kelamin, alamat, no_hp, email, id_fakultas, id_prodi, status)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Aktif')
                            ''', (nim, nama_lengkap, str(tgl_lahir), jk, alamat, no_hp, email_mhs, id_fakultas, id_prodi))
                            conn.commit()
                            st.success(f"Berhasil! Data mahasiswa {nama_lengkap} telah disimpan.")
                        except sqlite3.IntegrityError:
                            st.error("Eror Gagal Menyimpan: NIM sudah terdaftar di sistem!")
                        finally:
                            conn.close()
                            st.rerun()

        st.markdown("---")
        
        # AMBIL DATA DARI DATABASE (Gabungan Relasional Multi-Tabel)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT m.*, p.nama_prodi, p.kelas, f.nama_fakultas
            FROM mahasiswa m
            LEFT JOIN program_studi p ON m.id_prodi = p.id
            LEFT JOIN fakultas f ON m.id_fakultas = f.id
            ORDER BY m.nim DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        # Proses Instansiasi Objek OOP Mahasiswa Bawaan Anda
        mhs_objects = []
        for r in rows:
            obj = MahasiswaObj(
                r['nim'], r['nama'], r['tanggal_lahir'], r['jenis_kelamin'],
                r['alamat'], r['no_hp'], r['email'], r['nama_fakultas'],
                r['nama_prodi'], r['kelas'], r['status'], r['id_fakultas'], r['id_prodi']
            )
            mhs_objects.append(obj.to_dict())
            
        # FITUR SEARCHING MURNI PYTHON (Bawaan Logika Proyek Anda)
        search_query = st.text_input("🔍 Pencarian Instan (Ketik Nama / NIM Mahasiswa)")
        if search_query:
            mhs_objects = [m for m in mhs_objects if search_query.lower() in m['nama'].lower() or search_query in m['nim']]
            
        # FITUR SORTING MURNI PYTHON (Menggunakan Algoritma Bubble Sort Anda)
        mhs_objects = bubble_sort_mhs(mhs_objects)
        
        # MENAMPILKAN DATA UTAMA KE TABEL INTERAKTIF STREAMLIT
        if mhs_objects:
            df_mhs = pd.DataFrame(mhs_objects)
            
            # Memfilter susunan kolom agar rapi saat dilihat dosen
            kolom_tampil = ['nim', 'nama', 'jenis_kelamin', 'nama_prodi', 'kelas', 'status']
            st.dataframe(df_mhs[kolom_tampil], use_container_width=True, hide_index=True)
            
            # FITUR EKSPOR LAPORAN (Langsung Excel Friendly)
            st.markdown("### 📥 Cetak Laporan Eksternal")
            st.download_button(
                label="Unduh Excel/CSV Laporan Mahasiswa",
                data=df_mhs.to_csv(index=False).encode('utf-8'),
                file_name='Laporan_Data_Mahasiswa.csv',
                mime='text/csv',
            )
        else:
            st.warning("Sistem tidak menemukan data mahasiswa terdaftar.")
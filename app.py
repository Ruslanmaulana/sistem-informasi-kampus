import streamlit as st
import sqlite3
import math
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash

# ==========================================
# 1. SUNTIKAN DESAIN ASLI ADMINLTE & BOOTSTRAP (CSS INJECTION)
# ==========================================
st.set_page_config(page_title="Sistem Manajemen Data Mahasiswa", layout="wide")

st.markdown("""
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Source+Sans+Pro:300,400,400i,700&display=fallback">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/admin-lte@3.2/dist/css/adminlte.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.1/dist/css/bootstrap.min.css">
    
    <style>
    /* Mengubah Paksa Sidebar Streamlit Menjadi Biru Gelap (#003366) Sesuai Desain Anda */
    [data-testid="stSidebar"] {
        background-color: #003366 !important;
        background-image: none !important;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    /* Merapikan Jarak Konten */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    /* Desain Kepala Kartu Khas AdminLTE */
    .adminlte-card-header {
        background-color: #ffffff;
        padding: 12px 20px;
        border-top: 3px solid #0056b3;
        border-radius: 4px 4px 0 0;
        margin-bottom: 0px;
        border-bottom: 1px solid #dee2e6;
    }
    /* Memperbaiki teks putih di dalam small-box AdminLTE */
    .small-box .inner h3, .small-box .inner p {
        color: #ffffff !important;
    }
    .small-box .icon i {
        color: rgba(255,255,255,0.15) !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. KONFIGURASI DATABASE
# ==========================================
DB_FILE = 'data_kampus.db'

def get_db_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fakultas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_fakultas TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS program_studi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_fakultas INTEGER NOT NULL,
            nama_prodi TEXT NOT NULL,
            kelas TEXT NOT NULL,
            FOREIGN KEY (id_fakultas) REFERENCES fakultas (id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mahasiswa (
            nim TEXT PRIMARY KEY NOT NULL,
            nama TEXT NOT NULL,
            tanggal_lahir TEXT,
            jenis_kelamin TEXT,
            alamat TEXT,
            no_hp TEXT,
            email TEXT,
            id_fakultas INTEGER,
            id_prodi INTEGER,
            status TEXT DEFAULT 'Aktif',
            FOREIGN KEY (id_fakultas) REFERENCES fakultas (id),
            FOREIGN KEY (id_prodi) REFERENCES program_studi (id)
        )
    ''')
    cursor.execute("SELECT * FROM users WHERE email = 'admin@gmail.com'")
    if not cursor.fetchone():
        hashed_pw = generate_password_hash('admin123', method='scrypt')
        cursor.execute("INSERT INTO users (name, email, password) VALUES ('Admin', 'admin@gmail.com', ?)", (hashed_pw,))
    conn.commit()
    conn.close()

init_db()

# ==========================================
# 3. LOGIKA OOP & ALGORITMA (Bawaan Anda)
# ==========================================
class Person:
    def __init__(self, nama):
        self._nama = nama
    def get_nama(self):
        return self._nama

class MahasiswaObj(Person):
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
        return {
            "nim": self.nim, "nama": self.get_nama(), "tanggal_lahir": self.tanggal_lahir,
            "jenis_kelamin": self.jenis_kelamin, "alamat": self.alamat, "no_hp": self.no_hp,
            "email": self.email, "nama_fakultas": self.nama_fakultas, "nama_prodi": self.nama_prodi,
            "kelas": self.kelas, "status": self.status, "id_fakultas": self.id_fakultas, "id_prodi": self.id_prodi
        }

def bubble_sort_mhs(data_list):
    n = len(data_list)
    for i in range(n):
        for j in range(0, n-i-1):
            if data_list[j]['nama'].lower() > data_list[j+1]['nama'].lower():
                data_list[j], data_list[j+1] = data_list[j+1], data_list[j]
    return data_list

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = ""

# ==========================================
# 4. HALAMAN AUTENTIKASI (DESAIN KARTU)
# ==========================================
if not st.session_state['logged_in']:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h2 class='text-center font-weight-bold'>Form Login</h2>", unsafe_allow_html=True)
        tab_login, tab_register = st.tabs(["🔑 Sesi Login", "📝 Registrasi"])
        
        with tab_login:
            email_input = st.text_input("Masukan Email", key="login_email")
            password_input = st.text_input("Masukan Password", type="password", key="login_password")
            if st.button("Login", type="primary", use_container_width=True):
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE email = ?', (email_input,))
                user = cursor.fetchone()
                conn.close()

                if user and check_password_hash(user['password'], password_input):
                    st.session_state['logged_in'] = True
                    st.session_state['user_name'] = user['name']
                    st.success("Login berhasil!")
                    st.rerun()
                else:
                    st.error("Email atau Password salah!")
                    
        with tab_register:
            reg_name = st.text_input("Nama Lengkap", key="reg_name")
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input("Password", type="password", key="reg_password")
            if st.button("Daftar Baru", use_container_width=True):
                if reg_name and reg_email and reg_password:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    try:
                        cursor.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', 
                                       (reg_name, reg_email, generate_password_hash(reg_password)))
                        conn.commit()
                        st.success("Registrasi Berhasil! Silakan pindah ke tab Login.")
                    except sqlite3.IntegrityError:
                        st.error("Email sudah digunakan!")
                    finally:
                        conn.close()

# ==========================================
# 5. HALAMAN UTAMA (TAMPILAN ASLI SIDEBAR & DASHBOARD)
# ==========================================
else:
    # Desain Header User Panel di Sidebar Kiri Sesuai base.html
    st.sidebar.markdown(f"""
        <div style='text-align: center; padding: 10px; border-bottom: 1px solid #4f5d73; margin-bottom: 15px;'>
            <h4 style='color: white; font-weight: bold; margin: 0;'>
                <i class='fas fa-user-circle'></i> {st.session_state['user_name']}
            </h4>
            <small style='color: #cbd5e1;'>Sistem Akademik Admin</small>
        </div>
    """, unsafe_allow_html=True)
    
    menu = st.sidebar.radio(
        "MENU NAVIGASI",
        ["Dashboard", "Manajemen Fakultas", "Manajemen Program Studi", "Manajemen Mahasiswa", "Log Out"]
    )
    
    if menu == "Log Out":
        st.session_state['logged_in'] = False
        st.session_state['user_name'] = ""
        st.rerun()
        
    # --- PANDUAN TAMPILAN DASHBOARD (PERSIS GAMBAR ORIGINAL ANDA) ---
    elif menu == "Dashboard":
        st.markdown(f"""
            <div class='alert alert-info shadow-sm'>
                <h5><i class='icon fas fa-info'></i> Selamat Datang, {st.session_state['user_name']}!</h5>
                Sistem Manajemen Data Mahasiswa - Universitas Pamulang
            </div>
        """, unsafe_allow_html=True)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        tf = cursor.execute('SELECT COUNT(*) FROM fakultas').fetchone()[0]
        tp = cursor.execute('SELECT COUNT(*) FROM program_studi').fetchone()[0]
        tm = cursor.execute('SELECT COUNT(*) FROM mahasiswa').fetchone()[0]
        ma = cursor.execute("SELECT COUNT(*) FROM mahasiswa WHERE status = 'Aktif'").fetchone()[0]
        mna = cursor.execute("SELECT COUNT(*) FROM mahasiswa WHERE status = 'Tidak Aktif'").fetchone()[0]
        
        # Grid Baris 1 Kotak Besar (Fakultas & Prodi) Sesuai File HTML Anda
        st.markdown(f"""
        <div class="row">
          <div class="col-lg-6 col-12">
            <div class="small-box bg-primary">
              <div class="inner"><h3>{tf}</h3><p>TOTAL FAKULTAS</p></div>
              <div class="icon"><i class="fas fa-university"></i></div>
            </div>
          </div>
          <div class="col-lg-6 col-12">
            <div class="small-box bg-success">
              <div class="inner"><h3>{tp}</h3><p>TOTAL PROGRAM STUDI</p></div>
              <div class="icon"><i class="fas fa-book-open"></i></div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Grid Baris 2 Kotak Kecil (Statistik Aktivasi Mahasiswa) Sesuai File HTML Anda
        st.markdown(f"""
        <div class="row">
          <div class="col-lg-4 col-6"><div class="small-box bg-info"><div class="inner"><h3>{tm}</h3><p>Total Mahasiswa</p></div><div class="icon"><i class="fas fa-users"></i></div></div></div>
          <div class="col-lg-4 col-6"><div class="small-box bg-success"><div class="inner"><h3>{ma}</h3><p>Mahasiswa Aktif</p></div><div class="icon"><i class="fas fa-user-check"></i></div></div></div>
          <div class="col-lg-4 col-12"><div class="small-box bg-danger"><div class="inner"><h3>{mna}</h3><p>Mahasiswa Tidak Aktif</p></div><div class="icon"><i class="fas fa-user-times"></i></div></div></div>
        </div>
        """, unsafe_allow_html=True)
        
        # Tabel Dashboard 5 Data Terbaru Sesuai Gambar
        st.markdown("<div class='adminlte-card-header'><h4 class='m-0 text-dark'><i class='fas fa-list text-success mr-2'></i>Mahasiswa Terbaru</h4></div>", unsafe_allow_html=True)
        cursor.execute('''
            SELECT m.nim, m.nama, p.nama_prodi, p.kelas, m.status 
            FROM mahasiswa m
            LEFT JOIN program_studi p ON m.id_prodi = p.id
            ORDER BY m.nim DESC LIMIT 5
        ''')
        mhs_baru = cursor.fetchall()
        conn.close()
        
        if mhs_baru:
            df_dash = pd.DataFrame([dict(r) for r in mhs_baru])
            st.table(df_dash)

    # --- MANAJEMEN FAKULTAS ---
    elif menu == "Manajemen Fakultas":
        st.title("🏛️ Manajemen Fakultas")
        
        with st.expander("➕ Tambah Fakultas Baru"):
            nf = st.text_input("Nama Fakultas")
            if st.button("Simpan Fakultas", type="primary"):
                if nf:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute('INSERT INTO fakultas (nama_fakultas) VALUES (?)', (nf,))
                    conn.commit()
                    conn.close()
                    st.success("Fakultas Berhasil Ditambahkan!")
                    st.rerun()

        search_q = st.text_input("🔍 Cari Fakultas...")
        conn = get_db_connection()
        cursor = conn.cursor()
        if search_q:
            cursor.execute('SELECT * FROM fakultas WHERE nama_fakultas LIKE ?', ('%' + search_q + '%',))
        else:
            cursor.execute('SELECT * FROM fakultas')
        rows_f = cursor.fetchall()
        conn.close()
        
        if rows_f:
            df_f = pd.DataFrame([dict(r) for r in rows_f])
            # Tampilan Tabel Elegan Berwarna Header Biru
            st.markdown("<div class='adminlte-card-header'><h5 class='m-0 text-dark'>Daftar Tabel Fakultas</h5></div>", unsafe_allow_html=True)
            st.dataframe(df_f, use_container_width=True, hide_index=True)

    # --- MANAJEMEN PROGRAM STUDI ---
    elif menu == "Manajemen Program Studi":
        st.title("📚 Manajemen Program Studi")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM fakultas')
        fak_rows = cursor.fetchall()
        
        if not fak_rows:
            st.warning("Isi data Fakultas terlebih dahulu!")
        else:
            fak_dict = {r['nama_fakultas']: r['id'] for r in fak_rows}
            with st.expander("➕ Tambah Program Studi Baru"):
                p_nama = st.text_input("Nama Prodi")
                p_kelas = st.selectbox("Kelas", ["Reguler A", "Reguler B", "Reguler C", "CS Employee"])
                p_fak = st.selectbox("Pilih Fakultas Hubungan", list(fak_dict.keys()))
                
                if st.button("Simpan Program Studi", type="primary"):
                    cursor.execute('INSERT INTO program_studi (id_fakultas, nama_prodi, kelas) VALUES (?, ?, ?)',
                                   (fak_dict[p_fak], p_nama, p_kelas))
                    conn.commit()
                    st.success("Prodi Berhasil Ditambahkan!")
                    st.rerun()
            
            cursor.execute('''
                SELECT p.id, p.nama_prodi, p.kelas, f.nama_fakultas 
                FROM program_studi p
                JOIN fakultas f ON p.id_fakultas = f.id
            ''')
            prodi_rows = cursor.fetchall()
            if prodi_rows:
                df_p = pd.DataFrame([dict(r) for r in prodi_rows])
                st.markdown("<div class='adminlte-card-header'><h5 class='m-0 text-dark'>Daftar Tabel Program Studi</h5></div>", unsafe_allow_html=True)
                st.dataframe(df_p, use_container_width=True, hide_index=True)
        conn.close()

    # --- MANAJEMEN MAHASISWA (FITUR OOP + BUBBLE SORT + CETAK ) ---
    elif menu == "Manajemen Mahasiswa":
        st.title("🎓 Manajemen Data Mahasiswa")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM program_studi')
        prodi_list = cursor.fetchall()
        
        if not prodi_list:
            st.warning("Isi data Program Studi terlebih dahulu!")
        else:
            prodi_dict = {f"{r['nama_prodi']} ({r['kelas']})": (r['id'], r['id_fakultas']) for r in prodi_list}
            
            with st.expander("➕ Form Tambah Mahasiswa"):
                m_nim = st.text_input("NIM")
                m_nama = st.text_input("Nama Lengkap")
                m_tgl = st.text_input("Tanggal Lahir (Contoh: 2000-01-01)")
                m_jk = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
                m_alamat = st.text_area("Alamat Rumah")
                m_hp = st.text_input("Nomor Handphone")
                m_email = st.text_input("Email Valid")
                m_prod_string = st.selectbox("Hubungkan ke Program Studi", list(prodi_dict.keys()))
                m_status = st.selectbox("Status Keaktifan", ["Aktif", "Tidak Aktif"])
                
                if st.button("Simpan Mahasiswa", type="primary"):
                    if m_nim and m_nama:
                        id_p, id_f = prodi_dict[m_prod_string]
                        try:
                            cursor.execute('''
                                INSERT INTO mahasiswa (nim, nama, tanggal_lahir, jenis_kelamin, alamat, no_hp, email, id_fakultas, id_prodi, status)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (m_nim, m_nama, m_tgl, m_jk, m_alamat, m_hp, m_email, id_f, id_p, m_status))
                            conn.commit()
                            st.success("Mahasiswa Baru Berhasil Tersimpan!")
                        except sqlite3.IntegrityError:
                            st.error("Error: NIM sudah terdaftar!")
                        st.rerun()
            
            # AMBIL DATA UTK DIPROSES KE STRUKTUR PROGRAM ASLI ANDA
            cursor.execute('''
                SELECT m.*, p.nama_prodi, p.kelas, f.nama_fakultas
                FROM mahasiswa m
                LEFT JOIN program_studi p ON m.id_prodi = p.id
                LEFT JOIN fakultas f ON m.id_fakultas = f.id
                ORDER BY m.nim DESC
            ''')
            rows = cursor.fetchall()
            
            mhs_objects = []
            for r in rows:
                obj = MahasiswaObj(
                    r['nim'], r['nama'], r['tanggal_lahir'], r['jenis_kelamin'],
                    r['alamat'], r['no_hp'], r['email'], r['nama_fakultas'],
                    r['nama_prodi'], r['kelas'], r['status'], r['id_fakultas'], r['id_prodi']
                )
                mhs_objects.append(obj.to_dict())
                
            search_mhs = st.text_input("🔍 Pencarian Murni Python (Ketik Nama / NIM)...")
            if search_mhs:
                mhs_objects = [m for m in mhs_objects if search_mhs.lower() in m['nama'].lower() or search_mhs in m['nim']]
                
            # Pemanggilan Fungsi Bubble Sort Asli Anda
            mhs_objects = bubble_sort_mhs(mhs_objects)
            
            if mhs_objects:
                df_mhs = pd.DataFrame(mhs_objects)
                st.markdown("<div class='adminlte-card-header'><h5 class='m-0 text-dark'>Daftar Tabel Mahasiswa Berjalan</h5></div>", unsafe_allow_html=True)
                st.dataframe(df_mhs[['nim', 'nama', 'jenis_kelamin', 'nama_prodi', 'kelas', 'status']], use_container_width=True, hide_index=True)
                
                # Integrasi Fitur Pusat Cetak Laporan Excel Langsung Download
                st.markdown("### 📥 Ekspor Berkas Resmi")
                st.download_button(
                    label="Export Excel / CSV Laporan",
                    data=df_mhs[['nim', 'nama', 'nama_prodi', 'kelas', 'status']].to_csv(index=False).encode('utf-8'),
                    file_name='Laporan_Data_Mahasiswa.csv',
                    mime='text/csv'
                )
        conn.close()

import streamlit as st
import sqlite3
import math
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash

# ==========================================
# 1. CDN & CSS INJECTION (MENYUNTIKKAN TEMA ASLI ADMINLTE)
# ==========================================
st.set_page_config(page_title="Sistem Manajemen Data Mahasiswa", layout="wide")

st.markdown("""
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Source+Sans+Pro:300,400,400i,700&display=fallback">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/admin-lte@3.2/dist/css/adminlte.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.1/dist/css/bootstrap.min.css">
    
    <style>
    /* Mengubah Warna Sidebar Streamlit Menjadi Biru Gelap (#003366) Sesuai Desain Anda */
    [data-testid="stSidebar"] {
        background-color: #003366 !important;
        background-image: none !important;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    /* Penyesuaian Ruang Kerja Utama */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
    }
    /* Desain Kepala Kartu Form / Tabel ala AdminLTE */
    .adminlte-card-header {
        background-color: #ffffff;
        padding: 12px 20px;
        border-top: 3px solid #0056b3;
        border-radius: 4px 4px 0 0;
        border-bottom: 1px solid #dee2e6;
        margin-bottom: 15px;
    }
    .adminlte-card-header-success { border-top: 3px solid #28a745; }
    .adminlte-card-header-warning { border-top: 3px solid #ffc107; }
    .adminlte-card-header-danger { border-top: 3px solid #dc3545; }
    
    /* Memaksa Warna Teks Dalam Kotak Statistik Tetap Putih */
    .small-box .inner h3, .small-box .inner p {
        color: #ffffff !important;
    }
    .small-box .icon i {
        color: rgba(255,255,255,0.15) !important;
    }
    /* Mempercantik Inputbox bawaan Streamlit agar Selaras dengan Bootstrap */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. MANAJEMEN KONEKSI DATABASE LOKAL
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
            nama_fakultas TEXT NOT NULL
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
# 3. IMPLEMENTASI PILAR OOP & ALGORITMA SORTING
# ==========================================
class Person:
    def __init__(self, nama):
        self._nama = nama  # Pilar Encapsulation
    def get_nama(self):
        return self._nama

class MahasiswaObj(Person):  # Pilar Inheritance
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

# Inisialisasi status sesi aplikasi
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = ""
if 'auth_view' not in st.session_state:
    st.session_state['auth_view'] = "login"

# ==========================================
# 4. HALAMAN AUTENTIKASI (KEMBAR IDENTIK LOGIN.HTML)
# ==========================================
if not st.session_state['logged_in']:
    col1, col2, col3 = st.columns([1, 1.8, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h2 class='text-center font-weight-bold mb-3'>Form Login</h2>", unsafe_allow_html=True)
        
        # Desain Tab Toggle antara Login dan Daftar Sesuai Berkas login.html Anda
        c_tab1, c_tab2 = st.columns(2)
        with c_tab1:
            if st.button("🔒 Login", use_container_width=True, type="primary" if st.session_state['auth_view'] == "login" else "secondary"):
                st.session_state['auth_view'] = "login"
                st.rerun()
        with c_tab2:
            if st.button("📝 Daftar", use_container_width=True, type="primary" if st.session_state['auth_view'] == "register" else "secondary"):
                st.session_state['auth_view'] = "register"
                st.rerun()
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        if st.session_state['auth_view'] == "login":
            email = st.text_input("Masukan Email", placeholder="contoh@gmail.com")
            password = st.text_input("Masukan Password", type="password", placeholder="******")
            if st.button("Login Ke Sistem", use_container_width=True):
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
                user = cursor.fetchone()
                conn.close()
                if user and check_password_hash(user['password'], password):
                    st.session_state['logged_in'] = True
                    st.session_state['user_name'] = user['name']
                    st.success("Login Berhasil!")
                    st.rerun()
                else:
                    st.error("Email atau Password salah!")
        else:
            reg_name = st.text_input("Masukan Nama Lengkap")
            reg_email = st.text_input("Masukan Email Baru")
            reg_password = st.text_input("Masukan Password Baru", type="password")
            if st.button("Daftar Sekarang", use_container_width=True):
                if reg_name and reg_email and reg_password:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    try:
                        cursor.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', 
                                       (reg_name, reg_email, generate_password_hash(reg_password)))
                        conn.commit()
                        st.success("Registrasi Berhasil! Silakan klik tab Login.")
                        st.session_state['auth_view'] = "login"
                    except sqlite3.IntegrityError:
                        st.error("Email tersebut sudah terdaftar!")
                    finally:
                        conn.close()
                else:
                    st.warning("Mohon lengkapi seluruh kolom forms!")

# ==========================================
# 5. HALAMAN UTAMA (SISTEM NAVIGASI & KONTEN ADMINLTE)
# ==========================================
else:
    # Sidebar Navigasi Berwarna Biru Dongker (#003366) Khas base.html Anda
    st.sidebar.markdown(f"""
        <div style='text-align: center; padding: 12px; border-bottom: 1px solid #4f5d73; margin-bottom: 15px;'>
            <h4 style='color: white; font-weight: bold; margin: 0;'>
                <i class='fas fa-graduation-cap'></i> Data Mahasiswa
            </h4>
            <p style='color: #cbd5e1; font-size:13px; margin: 5px 0 0 0;'>
                <i class='fas fa-user-circle'></i> {st.session_state['user_name']} (Admin)
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    menu = st.sidebar.radio(
        "MENU UTAMA",
        ["Dashboard", "Mahasiswa", "Fakultas", "Program Studi", "Cetak Laporan", "Keluar Sistem"]
    )
    
    if menu == "Keluar Sistem":
        st.session_state['logged_in'] = False
        st.session_state['user_name'] = ""
        st.rerun()

    # ------------------------------------------
    # A. DASHBOARD VIEW (PERSIS DASHBOARD.HTML)
    # ------------------------------------------
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
        
        # Grid Atas Baris 1 Kotak Besar (Fakultas & Prodi) Sesuai Dashboard.html Anda
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
        
        # Grid Bawah Baris 2 Kotak Kecil (Statistik Keaktifan Mahasiswa) Sesuai Dashboard.html Anda
        st.markdown(f"""
        <div class="row">
          <div class="col-lg-4 col-6"><div class="small-box bg-info"><div class="inner"><h3>{tm}</h3><p>Total Mahasiswa</p></div><div class="icon"><i class="fas fa-users"></i></div></div></div>
          <div class="col-lg-4 col-6"><div class="small-box bg-success"><div class="inner"><h3>{ma}</h3><p>Mahasiswa Aktif</p></div><div class="icon"><i class="fas fa-user-check"></i></div></div></div>
          <div class="col-lg-4 col-12"><div class="small-box bg-danger"><div class="inner"><h3>{mna}</h3><p>Mahasiswa Tidak Aktif</p></div><div class="icon"><i class="fas fa-user-times"></i></div></div></div>
        </div>
        """, unsafe_allow_html=True)
        
        # Komponen Tabel Mahasiswa Terbaru Sesuai Gambar Berkas Anda
        st.markdown("<div class='adminlte-card-header'><h5 class='m-0 text-dark'><i class='fas fa-list text-success mr-2'></i> 5 Mahasiswa Terbaru</h5></div>", unsafe_allow_html=True)
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

    # ------------------------------------------
    # B. FAKULTAS VIEW (PERSIS FAKULTAS.HTML + CRUD)
    # ------------------------------------------
    elif menu == "Fakultas":
        st.markdown("<div class='adminlte-card-header'><h3 class='m-0 text-dark'><i class='fas fa-university mr-2'></i>Manajemen Data Fakultas</h3></div>", unsafe_allow_html=True)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Pembagian Form CRUD Fakultas
        c_add, c_edit, c_del = st.columns(3)
        with c_add:
            st.markdown("<div class='adminlte-card-header'><span class='font-weight-bold'>➕ Tambah Fakultas</span></div>", unsafe_allow_html=True)
            f_baru = st.text_input("Nama Fakultas Baru", key="add_f")
            if st.button("Simpan Fakultas"):
                if f_baru:
                    cursor.execute('INSERT INTO fakultas (nama_fakultas) VALUES (?)', (f_baru,))
                    conn.commit()
                    st.success("Berhasil Menambahkan Fakultas!")
                    st.rerun()
                    
        with c_edit:
            st.markdown("<div class='adminlte-card-header-warning'><span class='font-weight-bold'>📝 Edit Fakultas</span></div>", unsafe_allow_html=True)
            cursor.execute('SELECT * FROM fakultas')
            f_list = cursor.fetchall()
            if f_list:
                edit_f_choice = st.selectbox("Pilih Fakultas Diubah", options=[r['nama_fakultas'] for r in f_list], key="sel_f_edit")
                edit_f_id = [r['id'] for r in f_list if r['nama_fakultas'] == edit_f_choice][0]
                edit_f_name = st.text_input("Nama Fakultas Baru", value=edit_f_choice, key="name_f_edit")
                if st.button("Update Data Fakultas"):
                    cursor.execute('UPDATE fakultas SET nama_fakultas = ? WHERE id = ?', (edit_f_name, edit_f_id))
                    conn.commit()
                    st.success("Fakultas Berhasil Diperbarui!")
                    st.rerun()
                    
        with c_del:
            st.markdown("<div class='adminlte-card-header-danger'><span class='font-weight-bold'>🚨 Hapus Data Fakultas</span></div>", unsafe_allow_html=True)
            if f_list:
                del_f_choice = st.selectbox("Pilih Fakultas Dihapus", options=[r['nama_fakultas'] for r in f_list], key="sel_f_del")
                del_f_id = [r['id'] for r in f_list if r['nama_fakultas'] == del_f_choice][0]
                if st.button("Hapus Permanen Fakultas", type="primary"):
                    cursor.execute('DELETE FROM fakultas WHERE id = ?', (del_f_id,))
                    conn.commit()
                    st.warning("Fakultas Telah Terhapus!")
                    st.rerun()
                    
        st.markdown("<hr>", unsafe_allow_html=True)
        search_f = st.text_input("🔍 Cari Berdasarkan Nama Fakultas...")
        if search_f:
            cursor.execute('SELECT * FROM fakultas WHERE nama_fakultas LIKE ?', ('%' + search_f + '%',))
        else:
            cursor.execute('SELECT * FROM fakultas')
        all_f = cursor.fetchall()
        conn.close()
        
        if all_f:
            st.markdown(f"<h5>Total Fakultas Terdaftar: <span class='badge bg-primary text-white'>{len(all_f)}</span></h5>", unsafe_allow_html=True)
            st.table(pd.DataFrame([dict(r) for r in all_f]))

    # ------------------------------------------
    # C. PROGRAM STUDI VIEW (PERSIS PRODI.HTML + CRUD)
    # ------------------------------------------
    elif menu == "Program Studi":
        st.markdown("<div class='adminlte-card-header'><h3 class='m-0 text-dark'><i class='fas fa-book-open mr-2'></i>Manajemen Program Studi</h3></div>", unsafe_allow_html=True)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM fakultas')
        fak_rows = cursor.fetchall()
        
        if not fak_rows:
            st.error("Mohon isi tabel Fakultas terlebih dahulu!")
        else:
            fak_mapping = {r['nama_fakultas']: r['id'] for r in fak_rows}
            
            cp_add, cp_edit, cp_del = st.columns(3)
            with cp_add:
                st.markdown("<div class='adminlte-card-header'><span class='font-weight-bold'>➕ Tambah Prodi</span></div>", unsafe_allow_html=True)
                p_baru = st.text_input("Nama Program Studi Baru")
                p_kelas = st.selectbox("Pilihan Kelas", ["Reguler A", "Reguler B", "Reguler C", "CS"])
                p_fak = st.selectbox("Hubungkan Ke Fakultas", list(fak_mapping.keys()), key="add_p_fak")
                if st.button("Simpan Prodi Baru"):
                    if p_baru:
                        cursor.execute('INSERT INTO program_studi (id_fakultas, nama_prodi, kelas) VALUES (?, ?, ?)', 
                                       (fak_mapping[p_fak], p_baru, p_kelas))
                        conn.commit()
                        st.success("Prodi Berhasil Ditambahkan!")
                        st.rerun()
                        
            cursor.execute('''
                SELECT p.id, p.nama_prodi, p.kelas, f.nama_fakultas, p.id_fakultas 
                FROM program_studi p
                JOIN fakultas f ON p.id_fakultas = f.id
            ''')
            all_prodi_data = cursor.fetchall()
            
            with cp_edit:
                st.markdown("<div class='adminlte-card-header-warning'><span class='font-weight-bold'>📝 Edit Prodi</span></div>", unsafe_allow_html=True)
                if all_prodi_data:
                    p_edit_choices = [f"{r['nama_prodi']} ({r['kelas']})" for r in all_prodi_data]
                    sel_p_edit = st.selectbox("Pilih Prodi Diubah", p_edit_choices)
                    p_edit_id = [r['id'] for r in all_prodi_data if f"{r['nama_prodi']} ({r['kelas']})" == sel_p_edit][0]
                    p_curr_row = [r for r in all_prodi_data if r['id'] == p_edit_id][0]
                    
                    up_p_name = st.text_input("Ubah Nama Prodi", value=p_curr_row['nama_prodi'])
                    up_p_kelas = st.selectbox("Ubah Kelas", ["Reguler A", "Reguler B", "Reguler C", "CS"], index=["Reguler A", "Reguler B", "Reguler C", "CS"].index(p_curr_row['kelas']))
                    up_p_fak = st.selectbox("Ubah Hubungan Fakultas", list(fak_mapping.keys()), index=list(fak_mapping.values()).index(p_curr_row['id_fakultas']), key="edit_p_fak")
                    if st.button("Update Data Prodi"):
                        cursor.execute('UPDATE program_studi SET id_fakultas=?, nama_prodi=?, kelas=? WHERE id=?', 
                                       (fak_mapping[up_p_fak], up_p_name, up_p_kelas, p_edit_id))
                        conn.commit()
                        st.success("Prodi Berhasil Diupdate!")
                        st.rerun()
                        
            with cp_del:
                st.markdown("<div class='adminlte-card-header-danger'><span class='font-weight-bold'>🚨 Hapus Prodi</span></div>", unsafe_allow_html=True)
                if all_prodi_data:
                    sel_p_del = st.selectbox("Pilih Prodi Dihapus", [f"{r['nama_prodi']} ({r['kelas']})" for r in all_prodi_data])
                    p_del_id = [r['id'] for r in all_prodi_data if f"{r['nama_prodi']} ({r['kelas']})" == sel_p_del][0]
                    if st.button("Hapus Permanen Prodi", type="primary"):
                        cursor.execute('DELETE FROM program_studi WHERE id=?', (p_id_del,))
                        conn.commit()
                        st.warning("Program Studi Berhasil Dihapus!")
                        st.rerun()
                        
            st.markdown("<hr>", unsafe_allow_html=True)
            search_p = st.text_input("🔍 Cari Berdasarkan Nama Prodi / Fakultas...")
            if search_p:
                cursor.execute('''
                    SELECT p.id, p.nama_prodi, p.kelas, f.nama_fakultas 
                    FROM program_studi p
                    JOIN fakultas f ON p.id_fakultas = f.id
                    WHERE p.nama_prodi LIKE ? OR f.nama_fakultas LIKE ?
                ''', ('%' + search_p + '%', '%' + search_p + '%'))
            else:
                cursor.execute('''
                    SELECT p.id, p.nama_prodi, p.kelas, f.nama_fakultas FROM program_studi p
                    JOIN fakultas f ON p.id_fakultas = f.id
                ''')
            final_p_rows = cursor.fetchall()
            conn.close()
            if final_p_rows:
                st.table(pd.DataFrame([dict(r) for r in final_p_rows]))

    # ------------------------------------------
    # D. MAHASISWA VIEW (PERSIS MAHASISWA.HTML + PAGINATION + BUBBLE SORT + CRUD)
    # ------------------------------------------
    elif menu == "Mahasiswa":
        st.markdown("<div class='adminlte-card-header'><h3 class='m-0 text-dark'><i class='fas fa-users mr-2'></i>Manajemen Data Mahasiswa</h3></div>", unsafe_allow_html=True)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM program_studi')
        prodi_rows = cursor.fetchall()
        
        if not prodi_rows:
            st.error("Mohon lengkapi tabel Program Studi terlebih dahulu!")
        else:
            prodi_mapping = {f"{r['nama_prodi']} - {r['kelas']}": (r['id'], r['id_fakultas']) for r in prodi_rows}
            
            # Pembagian Layout CRUD Vertikal agar Nyaman Beroperasi
            with st.expander("➕ Formulir Registrasi Tambah Mahasiswa"):
                with st.form("form_add_mhs"):
                    cm1, cm2 = st.columns(2)
                    with cm1:
                        add_nim = st.text_input("NIM")
                        add_nama = st.text_input("Nama Lengkap")
                        add_tgl = st.text_input("Tanggal Lahir (YYYY-MM-DD)")
                        add_jk = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
                    with cm2:
                        add_alamat = st.text_area("Alamat Lengkap")
                        add_hp = st.text_input("No Handphone")
                        add_email = st.text_input("Email")
                        add_prodi_str = st.selectbox("Program Studi", list(prodi_mapping.keys()))
                        add_status = st.selectbox("Status", ["Aktif", "Tidak Aktif"])
                        
                    if st.form_submit_button("Simpan Mahasiswa"):
                        if add_nim and add_nama:
                            id_p, id_f = prodi_mapping[add_prodi_str]
                            try:
                                cursor.execute('''
                                    INSERT INTO mahasiswa (nim, nama, tanggal_lahir, jenis_kelamin, alamat, no_hp, email, id_fakultas, id_prodi, status)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (add_nim, add_nama, add_tgl, add_jk, add_alamat, add_hp, add_email, id_f, id_p, add_status))
                                conn.commit()
                                st.success("Mahasiswa Baru Berhasil Ditambahkan!")
                                st.rerun()
                            except sqlite3.IntegrityError:
                                st.error("Error: NIM sudah terdaftar!")
                        else:
                            st.warning("Kolom NIM dan Nama wajib diisi!")
                            
            # AMBIL DATA, INSTANSIASI OBJEK OOP MAHASISWA, SEARCHING & BUBBLE SORTING
            cursor.execute('''
                SELECT m.*, p.nama_prodi, p.kelas, f.nama_fakultas
                FROM mahasiswa m
                LEFT JOIN program_studi p ON m.id_prodi = p.id
                LEFT JOIN fakultas f ON m.id_fakultas = f.id
                ORDER BY m.nim DESC
            ''')
            rows_mhs = cursor.fetchall()
            
            mhs_objects = []
            for r in rows_mhs:
                obj = MahasiswaObj(
                    r['nim'], r['nama'], r['tanggal_lahir'], r['jenis_kelamin'],
                    r['alamat'], r['no_hp'], r['email'], r['nama_fakultas'],
                    r['nama_prodi'], r['kelas'], r['status'], r['id_fakultas'], r['id_prodi']
                )
                mhs_objects.append(obj.to_dict())
                
            search_query = st.text_input("🔍 Pencarian Instan Murni Python (Ketik Nama / NIM Mahasiswa)...")
            if search_query:
                mhs_objects = [m for m in mhs_objects if search_query.lower() in m['nama'].lower() or search_query in m['nim']]
                
            # Mengeksekusi Algoritma Pengurutan Mandiri Bubble Sort Anda
            mhs_objects = bubble_sort_mhs(mhs_objects)
            
            # IMPLEMENTASI FITUR PAGINATION (PEMBATASAN 10 DATA PER HALAMAN)
            if mhs_objects:
                per_page = 10
                total_rows = len(mhs_objects)
                total_pages = math.ceil(total_rows / per_page)
                
                # Input Angka Halaman Dinamis Pengganti Tombol Prev/Next Jinja2
                page = st.number_input(f"Halaman (1 - {total_pages})", min_value=1, max_value=total_pages, value=1, step=1)
                offset = (page - 1) * per_page
                paginated_list = mhs_objects[offset : offset + per_page]
                
                df_final_mhs = pd.DataFrame(paginated_list)
                st.markdown("<div class='adminlte-card-header'><h5 class='m-0 text-dark'>Tabel Data Mahasiswa Terbuka</h5></div>", unsafe_allow_html=True)
                st.dataframe(df_final_mhs[['nim', 'nama', 'jenis_kelamin', 'nama_prodi', 'kelas', 'status']], use_container_width=True, hide_index=True)
                
                # Kelola Data Terpilih (Update / Delete)
                with st.expander("⚙️ Aksi Kelola Ubah / Hapus Data Mahasiswa"):
                    sel_nim = st.selectbox("Pilih NIM Mahasiswa Sasaran", options=[m['nim'] for m in paginated_list])
                    curr_m = [m for m in paginated_list if m['nim'] == sel_nim][0]
                    
                    cedit, cdel = st.columns(2)
                    with cedit:
                        st.markdown("<span class='font-weight-bold text-warning'>Ubah Biodata:</span>", unsafe_allow_html=True)
                        u_nama = st.text_input("Nama Lengkap", value=curr_m['nama'])
                        u_tgl = st.text_input("Tanggal Lahir", value=curr_m['tanggal_lahir'])
                        u_jk = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"], index=["Laki-laki", "Perempuan"].index(curr_m['jenis_kelamin']))
                        u_alamat = st.text_area("Alamat", value=curr_m['alamat'])
                        u_hp = st.text_input("No HP", value=curr_m['no_hp'])
                        u_email = st.text_input("Email", value=curr_m['email'])
                        
                        prodi_keys = list(prodi_mapping.keys())
                        match_str = f"{curr_m['nama_prodi']} - {curr_m['kelas']}"
                        p_idx = prodi_keys.index(match_str) if match_str in prodi_keys else 0
                        u_prodi = st.selectbox("Program Studi", prodi_keys, index=p_idx)
                        u_status = st.selectbox("Status", ["Aktif", "Tidak Aktif"], index=["Aktif", "Tidak Aktif"].index(curr_m['status']))
                        
                        if st.button("Update Data Mahasiswa"):
                            id_p, id_f = prodi_mapping[u_prodi]
                            cursor.execute('''
                                UPDATE mahasiswa 
                                SET nama=?, tanggal_lahir=?, jenis_kelamin=?, alamat=?, no_hp=?, email=?, id_fakultas=?, id_prodi=?, status=?
                                WHERE nim=?
                            ''', (u_nama, u_tgl, u_jk, u_alamat, u_hp, u_email, id_f, id_p, u_status, sel_nim))
                            conn.commit()
                            st.success("Data Mahasiswa Berhasil Diperbarui!")
                            st.rerun()
                            
                    with cdel:
                        st.markdown("<span class='font-weight-bold text-danger'>Penghapusan Permanen:</span>", unsafe_allow_html=True)
                        st.write(f"Apakah Anda yakin menghapus data mahasiswa bernama **{curr_m['nama']}**?")
                        if st.button("🚨 Hapus Mahasiswa", type="primary"):
                            cursor.execute('DELETE FROM mahasiswa WHERE nim=?', (sel_nim,))
                            conn.commit()
                            st.warning("Data Mahasiswa Berhasil Dihapus!")
                            st.rerun()
            else:
                st.warning("Belum ada data mahasiswa terdaftar.")
        conn.close()

    # ------------------------------------------
    # E. CETAK LAPORAN VIEW (PERSIS LAPORAN.HTML)
    # ------------------------------------------
    elif menu == "Cetak Laporan":
        st.markdown("<div class='adminlte-card-header'><h3 class='m-0 text-dark'><i class='fas fa-file-alt text-primary mr-2'></i>Pusat Unduh Laporan</h3></div>", unsafe_allow_html=True)
        st.write("Silakan pilih format dokumen resmi untuk mengekspor seluruh data manajemen mahasiswa Anda.")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT m.nim, m.nama, p.nama_prodi, p.kelas, m.status 
            FROM mahasiswa m
            LEFT JOIN program_studi p ON m.id_prodi = p.id
            ORDER BY m.nim DESC
        ''')
        report_rows = cursor.fetchall()
        conn.close()
        
        if report_rows:
            df_report = pd.DataFrame([dict(r) for r in report_rows])
            
            # Desain Layout Box Samping Cetak Laporan Excel Seperti Berkas laporan.html
            col_rep1, col_rep2 = st.columns(2)
            with col_rep1:
                st.markdown("""
                    <div class='card shadow-sm text-center p-3'>
                        <h5 class='font-weight-bold text-success'><i class='fas fa-file-excel fa-2x mb-2 d-block'></i> Export Microsoft Excel Friendly</h5>
                        <p class='small text-muted'>Dokumen mencakup data relasi nama Fakultas, Program Studi, Kelas, dan Status Mahasiswa terbaru.</p>
                    </div>
                """, unsafe_allow_html=True)
                
                st.download_button(
                    label="📥 Unduh Berkas Excel (.csv friendly)",
                    data=df_report.to_csv(index=False, sep=';').encode('utf-8-sig'), # Menggunakan pembatas titik koma regional Indonesia Sesuai Kode Asli Anda
                    file_name='Laporan_Data_Mahasiswa.csv',
                    mime='text/csv',
                    use_container_width=True
                )
            with col_rep2:
                st.markdown("""
                    <div class='card shadow-sm text-center p-3'>
                        <h5 class='font-weight-bold text-danger'><i class='fas fa-file-pdf fa-2x mb-2 d-block'></i> Cetak Dokumen PDF Resmi</h5>
                        <p class='small text-muted'>Menampilkan pratinjau data komparasi bersih universitas siap cetak lewat piranti keras.</p>
                    </div>
                """, unsafe_allow_html=True)
                # Fitur Ekspor Tabel Berkas PDF dalam Streamlit Terintegrasi Lewat Slicing Print Preview Browser
                st.table(df_report)

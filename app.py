import streamlit as st
import sqlite3
import math
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash

# ==========================================
# 1. KONFIGURASI HALAMAN & DATABASE
# ==========================================
st.set_page_config(page_title="Sistem Manajemen Data Mahasiswa", layout="wide")

DB_FILE = 'data_kampus.db'

def get_db_connection():
    # check_same_thread=False wajib di Streamlit karena sifatnya yang multithreading
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Tabel Users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # 2. Tabel Fakultas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fakultas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_fakultas TEXT NOT NULL
        )
    ''')
    
    # 3. Tabel Program Studi
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS program_studi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_fakultas INTEGER NOT NULL,
            nama_prodi TEXT NOT NULL,
            kelas TEXT NOT NULL,
            FOREIGN KEY (id_fakultas) REFERENCES fakultas (id)
        )
    ''')
    
    # 4. Tabel Mahasiswa
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
# 2. LOGIKA OOP & ALGORITMA (Bawaan Anda)
# ==========================================
class Person:
    def __init__(self, nama):
        self._nama = nama  # Encapsulation

    def get_nama(self):
        return self._nama

class MahasiswaObj(Person):
    def __init__(self, nim, nama, tanggal_lahir, jenis_kelamin, alamat, no_hp, email, nama_fakultas, nama_prodi, kelas, status, id_fakultas, id_prodi):
        super().__init__(nama) # Inheritance
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

# ==========================================
# 3. MANAJEMEN SESSION STATE STREAMLIT
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = ""

# ==========================================
# 4. HALAMAN AUTENTIKASI (LOGIN & REGISTER)
# ==========================================
if not st.session_state['logged_in']:
    st.title("🎓 Sistem Informasi Akademik Kampus")
    tab_login, tab_register = st.tabs(["🔒 Login Admin", "📝 Daftar Akun Baru"])
    
    with tab_login:
        email_input = st.text_input("Email", key="login_email")
        password_input = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", type="primary", use_container_width=True):
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = ?', (email_input,))
            user = cursor.fetchone()
            conn.close()

            if user and check_password_hash(user['password'], password_input):
                st.session_state['logged_in'] = True
                st.session_state['user_name'] = user['name']
                st.success("Login Berhasil!")
                st.rerun()
            else:
                st.error("Email atau Password salah!")
                
    with tab_register:
        reg_name = st.text_input("Nama Lengkap", key="reg_name")
        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        if st.button("Daftar Akun", use_container_width=True):
            if reg_name and reg_email and reg_password:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE email = ?', (reg_email,))
                if cursor.fetchone():
                    st.error("Email sudah terdaftar!")
                    conn.close()
                else:
                    hashed_password = generate_password_hash(reg_password)
                    cursor.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', 
                                   (reg_name, reg_email, hashed_password))
                    conn.commit()
                    conn.close()
                    st.success("Registrasi berhasil! Silakan pindah ke tab Login.")
            else:
                st.warning("Semua data pendaftaran wajib diisi!")

# ==========================================
# 5. HALAMAN UTAMA (SETELAH LOGIN)
# ==========================================
else:
    st.sidebar.title(f"👤 {st.session_state['user_name']}")
    st.sidebar.write("Role: Administrator")
    
    menu = st.sidebar.radio(
        "Menu Navigasi",
        ["Dashboard", "Manajemen Fakultas", "Manajemen Prodi", "Manajemen Mahasiswa", "Logout"]
    )
    
    if menu == "Logout":
        st.session_state['logged_in'] = False
        st.session_state['user_name'] = ""
        st.rerun()
        
    # --- DASHBOARD VIEW ---
    elif menu == "Dashboard":
        st.title("📊 Dashboard Utama")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        tf = cursor.execute('SELECT COUNT(*) FROM fakultas').fetchone()[0]
        tp = cursor.execute('SELECT COUNT(*) FROM program_studi').fetchone()[0]
        tm = cursor.execute('SELECT COUNT(*) FROM mahasiswa').fetchone()[0]
        ma = cursor.execute("SELECT COUNT(*) FROM mahasiswa WHERE status = 'Aktif'").fetchone()[0]
        mna = cursor.execute("SELECT COUNT(*) FROM mahasiswa WHERE status = 'Tidak Aktif'").fetchone()[0]
        
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Fakultas", tf)
        col2.metric("Total Prodi", tp)
        col3.metric("Total Mahasiswa", tm)
        col4.metric("Mhs Aktif", ma)
        col5.metric("Mhs Tidak Aktif", mna)
        
        st.subheader("📌 5 Registrasi Mahasiswa Terbaru")
        cursor.execute('''
            SELECT m.nim, m.nama, p.nama_prodi, p.kelas, m.status 
            FROM mahasiswa m
            LEFT JOIN program_studi p ON m.id_prodi = p.id
            ORDER BY m.nim DESC LIMIT 5
        ''')
        mhs_baru = cursor.fetchall()
        conn.close()
        
        if mhs_baru:
            df_dashboard = pd.DataFrame([dict(r) for r in mhs_baru])
            st.dataframe(df_dashboard, use_container_width=True, hide_index=True)
            
    # --- MANAJEMEN FAKULTAS ---
    elif menu == "Manajemen Fakultas":
        st.title("🏛️ Kelola Data Fakultas")
        
        # Form Tambah
        with st.expander("➕ Tambah Fakultas Baru"):
            new_fakultas = st.text_input("Nama Fakultas Baru")
            if st.button("Simpan Fakultas"):
                if new_fakultas:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute('INSERT INTO fakultas (nama_fakultas) VALUES (?)', (new_fakultas,))
                    conn.commit()
                    conn.close()
                    st.success("Fakultas berhasil ditambahkan!")
                    st.rerun()
                    
        # Ambil Data & Fitur Pencarian
        search_q = st.text_input("🔍 Cari Fakultas...")
        conn = get_db_connection()
        cursor = conn.cursor()
        if search_q:
            cursor.execute('SELECT * FROM fakultas WHERE nama_fakultas LIKE ?', ('%' + search_q + '%',))
        else:
            cursor.execute('SELECT * FROM fakultas')
        fakultas_rows = cursor.fetchall()
        
        if fakultas_rows:
            df_f = pd.DataFrame([dict(r) for r in fakultas_rows])
            st.dataframe(df_f, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            st.subheader("⚙️ Aksi Kelola")
            select_f = st.selectbox("Pilih Fakultas untuk Diubah/Hapus", options=[r['nama_fakultas'] for r in fakultas_rows])
            f_id = [r['id'] for r in fakultas_rows if r['nama_fakultas'] == select_f][0]
            
            edit_col, delete_col = st.columns(2)
            with edit_col:
                new_name = st.text_input("Ubah Nama Fakultas", value=select_f)
                if st.button("Update Nama"):
                    cursor.execute('UPDATE fakultas SET nama_fakultas = ? WHERE id = ?', (new_name, f_id))
                    conn.commit()
                    st.success("Nama fakultas diperbarui!")
                    conn.close()
                    st.rerun()
            with delete_col:
                st.write("⚠️ Perhatian: Menghapus fakultas akan berdampak pada relasi data lainnya.")
                if st.button("🚨 Hapus Fakultas", type="primary"):
                    cursor.execute('DELETE FROM fakultas WHERE id = ?', (f_id,))
                    conn.commit()
                    st.warning("Fakultas telah dihapus!")
                    conn.close()
                    st.rerun()
        conn.close()

    # --- MANAJEMEN PROGRAM STUDI ---
    elif menu == "Manajemen Prodi":
        st.title("📚 Kelola Program Studi")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM  fakultas')
        all_fakultas = cursor.fetchall()
        
        if not all_fakultas:
            st.warning("Silakan isi data Fakultas terlebih dahulu!")
        else:
            fakultas_dict = {r['nama_fakultas']: r['id'] for r in all_fakultas}
            
            with st.expander("➕ Tambah Program Studi Baru"):
                p_nama = st.text_input("Nama Program Studi")
                p_kelas = st.selectbox("Kelas", ["Reguler A", "Reguler B", "Reguler C", "CS"])
                p_fak = st.selectbox("Hubungkan ke Fakultas", list(fakultas_dict.keys()))
                
                if st.button("Simpan Prodi"):
                    if p_nama:
                        cursor.execute('INSERT INTO program_studi (id_fakultas, nama_prodi, kelas) VALUES (?, ?, ?)', 
                                       (fakultas_dict[p_fak], p_nama, p_kelas))
                        conn.commit()
                        st.success("Program studi berhasil disimpan!")
                        st.rerun()
                        
            search_prodi = st.text_input("🔍 Cari Program Studi / Fakultas...")
            if search_prodi:
                cursor.execute('''
                    SELECT p.id, p.nama_prodi, p.kelas, f.nama_fakultas, p.id_fakultas 
                    FROM program_studi p
                    JOIN fakultas f ON p.id_fakultas = f.id
                    WHERE p.nama_prodi LIKE ? OR f.nama_fakultas LIKE ?
                ''', ('%' + search_prodi + '%', '%' + search_prodi + '%'))
            else:
                cursor.execute('''
                    SELECT p.id, p.nama_prodi, p.kelas, f.nama_fakultas, p.id_fakultas 
                    FROM program_studi p
                    JOIN fakultas f ON p.id_fakultas = f.id
                ''')
            prodi_rows = cursor.fetchall()
            
            if prodi_rows:
                df_p = pd.DataFrame([dict(r) for r in prodi_rows])
                st.dataframe(df_p[['id', 'nama_prodi', 'kelas', 'nama_fakultas']], use_container_width=True, hide_index=True)
                
                st.markdown("---")
                st.subheader("⚙️ Aksi Kelola Prodi")
                select_p = st.selectbox("Pilih Prodi untuk Diubah/Hapus", options=[f"{r['nama_prodi']} ({r['kelas']})" for r in prodi_rows])
                p_id = [r['id'] for r in prodi_rows if f"{r['nama_prodi']} ({r['kelas']})" == select_p][0]
                current_p = [r for r in prodi_rows if r['id'] == p_id][0]
                
                edit_p_col, del_p_col = st.columns(2)
                with edit_p_col:
                    edit_nama_p = st.text_input("Ubah Nama Prodi", value=current_p['nama_prodi'])
                    edit_kelas_p = st.selectbox("Ubah Kelas", ["Reguler A", "Reguler B", "Reguler C", "CS"], index=["Reguler A", "Reguler B", "Reguler C", "CS"].index(current_p['kelas']))
                    edit_fak_p = st.selectbox("Ubah Fakultas Hubungan", list(fakultas_dict.keys()), index=list(fakultas_dict.values()).index(current_p['id_fakultas']))
                    
                    if st.button("Update Data Prodi"):
                        cursor.execute('UPDATE program_studi SET id_fakultas=?, nama_prodi=?, kelas=? WHERE id=?', 
                                       (fakultas_dict[edit_fak_p], edit_nama_p, edit_kelas_p, p_id))
                        conn.commit()
                        st.success("Data prodi berhasil diperbarui!")
                        st.rerun()
                with del_p_col:
                    if st.button("🚨 Hapus Program Studi", type="primary"):
                        cursor.execute('DELETE FROM program_studi WHERE id=?', (p_id,))
                        conn.commit()
                        st.warning("Program studi dihapus!")
                        st.rerun()
        conn.close()

    # --- MANAJEMEN MAHASISWA (OOP INTEGRATED) ---
    elif menu == "Manajemen Mahasiswa":
        st.title("🎓 Sistem Manajemen Data Mahasiswa (OOP + Bubble Sort)")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM program_studi')
        prodi_list = cursor.fetchall()
        
        if not prodi_list:
            st.warning("Silakan isi data Program Studi terlebih dahulu!")
        else:
            prodi_dict = {f"{r['nama_prodi']} - {r['kelas']}": (r['id'], r['id_fakultas']) for r in prodi_list}
            
            with st.expander("➕ Formulir Registrasi Mahasiswa Baru"):
                with st.form("tambah_mhs_form"):
                    m_nim = st.text_input("NIM")
                    m_nama = st.text_input("Nama Lengkap")
                    m_tgl = st.text_input("Tanggal Lahir (YYYY-MM-DD)")
                    m_jk = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
                    m_alamat = st.text_area("Alamat")
                    m_hp = st.text_input("No HP")
                    m_email = st.text_input("Email")
                    m_prodi_sel = st.selectbox("Program Studi Tujuan", list(prodi_dict.keys()))
                    m_status = st.selectbox("Status", ["Aktif", "Tidak Aktif"])
                    
                    if st.form_submit_button("Simpan Mahasiswa Baru"):
                        if m_nim and m_nama:
                            id_prodi, id_fakultas = prodi_dict[m_prodi_sel]
                            try:
                                cursor.execute('''
                                    INSERT INTO mahasiswa (nim, nama, tanggal_lahir, jenis_kelamin, alamat, no_hp, email, id_fakultas, id_prodi, status)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (m_nim, m_nama, m_tgl, m_jk, m_alamat, m_hp, m_email, id_fakultas, id_prodi, m_status))
                                conn.commit()
                                st.success("Mahasiswa berhasil disimpan!")
                            except sqlite3.IntegrityError:
                                st.error("Error: NIM sudah digunakan!")
                            st.rerun()
                        else:
                            st.warning("NIM dan Nama Lengkap wajib diisi!")
            
            # AMBIL DATA, PROSES OOP INSTANTIATION, SEARCH & SORT
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
                
            search_mhs = st.text_input("🔍 Pencarian Murni Python (Ketik Nama / NIM)")
            if search_mhs:
                mhs_objects = [m for m in mhs_objects if search_mhs.lower() in m['nama'].lower() or search_mhs in m['nim']]
                
            # Algoritma Urut Nama Menggunakan Bubble Sort Anda
            mhs_objects = bubble_sort_mhs(mhs_objects)
            
            if mhs_objects:
                df_mhs = pd.DataFrame(mhs_objects)
                st.dataframe(df_mhs[['nim', 'nama', 'jenis_kelamin', 'nama_prodi', 'kelas', 'status']], use_container_width=True, hide_index=True)
                
                # FITUR UNDUH LAPORAN EKSTERNAL (Excel/CSV Friendly)
                st.download_button(
                    label="📥 Unduh Laporan Resmi (CSV/Excel Friendly)",
                    data=df_mhs[['nim', 'nama', 'nama_prodi', 'kelas', 'status']].to_csv(index=False).encode('utf-8'),
                    file_name='Laporan_Data_Mahasiswa.csv',
                    mime='text/csv'
                )
                
                st.markdown("---")
                st.subheader("⚙️ Aksi Kelola Mahasiswa")
                select_m = st.selectbox("Pilih NIM Mahasiswa untuk Diubah/Hapus", options=[m['nim'] for m in mhs_objects])
                current_m = [m for m in mhs_objects if m['nim'] == select_m][0]
                
                medit_col, mdel_col = st.columns(2)
                with medit_col:
                    enama = st.text_input("Ubah Nama", value=current_m['nama'])
                    etgl = st.text_input("Ubah Tgl Lahir", value=current_m['tanggal_lahir'])
                    ejk = st.selectbox("Ubah JK", ["Laki-laki", "Perempuan"], index=["Laki-laki", "Perempuan"].index(current_m['jenis_kelamin']))
                    ealamat = st.text_area("Ubah Alamat", value=current_m['alamat'])
                    ehp = st.text_input("Ubah No HP", value=current_m['no_hp'])
                    eemail = st.text_input("Ubah Email", value=current_m['email'])
                    
                    # Mencari default index untuk prodi dropdown
                    prodi_string_list = list(prodi_dict.keys())
                    match_string = f"{current_m['nama_prodi']} - {current_m['kelas']}"
                    default_idx = prodi_string_list.index(match_string) if match_string in prodi_string_list else 0
                    
                    eprodi = st.selectbox("Ubah Program Studi", prodi_string_list, index=default_idx)
                    estatus = st.selectbox("Ubah Status", ["Aktif", "Tidak Aktif"], index=["Aktif", "Tidak Aktif"].index(current_m['status']))
                    
                    if st.button("Update Data Mahasiswa"):
                        id_p, id_f = prodi_dict[eprodi]
                        cursor.execute('''
                            UPDATE mahasiswa 
                            SET nama=?, tanggal_lahir=?, jenis_kelamin=?, alamat=?, no_hp=?, email=?, id_fakultas=?, id_prodi=?, status=?
                            WHERE nim=?
                        ''', (enama, etgl, ejk, ealamat, ehp, eemail, id_f, id_p, estatus, select_m))
                        conn.commit()
                        st.success("Data mahasiswa berhasil diperbarui!")
                        st.rerun()
                with mdel_col:
                    st.write(f"Menghapus data mahasiswa dengan NIM {select_m}")
                    if st.button("🚨 Hapus Mahasiswa", type="primary"):
                        cursor.execute('DELETE FROM mahasiswa WHERE nim=?', (select_m,))
                        conn.commit()
                        st.warning("Data mahasiswa berhasil dihapus dari sistem!")
                        st.rerun()
            else:
                st.warning("Data mahasiswa tidak ditemukan.")
        conn.close()
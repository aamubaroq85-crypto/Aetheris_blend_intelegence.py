import hashlib
import sqlite3
from datetime import datetime
import io
import numpy as np
import pandas as pd
import streamlit as st

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Aetheris Blend Intelligence - Enterprise Edition",
    page_icon="🌿",
    layout="wide",
)


# Inisialisasi Database SQLite untuk Manajemen Resep & Autentikasi Enterprise
def init_db():
  conn = sqlite3.connect("aetheris_enterprise.db")
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT,
            role TEXT
        )
    """)
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            blend_name TEXT,
            author TEXT,
            virginia REAL,
            temanggung REAL,
            madura REAL,
            besuki REAL,
            casing_ph REAL,
            humectant REAL,
            temp REAL,
            estimated_tar REAL,
            estimated_nic REAL,
            throat_hit REAL,
            consistency REAL,
            total_cost REAL,
            created_at TEXT
        )
    """)
  cursor.execute("SELECT * FROM users WHERE username = 'masterblender'")
  if not cursor.fetchone():
    default_pass = hashlib.sha256("aetheris2026".encode()).hexdigest()
    cursor.execute(
        "INSERT INTO users VALUES ('masterblender', ?, 'Master Blender')",
        (default_pass,),
    )
  conn.commit()
  conn.close()


init_db()


def hash_password(password):
  return hashlib.sha256(password.encode()).hexdigest()


if "logged_in" not in st.session_state:
  st.session_state["logged_in"] = False
  st.session_state["username"] = ""
  st.session_state["role"] = ""

st.sidebar.title("🔐 Enterprise Security")
if not st.session_state["logged_in"]:
  st.sidebar.subheader("Login R&D Portal")
  login_user = st.sidebar.text_input("Username")
  login_pass = st.sidebar.text_input("Password", type="password")

  if st.sidebar.button("Autentikasi Masuk"):
    conn = sqlite3.connect("aetheris_enterprise.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT password_hash, role FROM users WHERE username = ?", (login_user,)
    )
    result = cursor.fetchone()
    conn.close()

    if result and result[0] == hash_password(login_pass):
      st.session_state["logged_in"] = True
      st.session_state["username"] = login_user
      st.session_state["role"] = result[1]
      st.success("Autentikasi Berhasil!")
      st.rerun()
    else:
      st.sidebar.error("Kredensial tidak valid.")
  st.stop()
else:
  st.sidebar.success(
      f"Login sebagai: {st.session_state['username']}"
      f" ({st.session_state['role']})"
  )
  if st.sidebar.button("Logout"):
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.rerun()

st.title("🌿 Aetheris Blend Intelligence (Enterprise Suite)")
st.markdown(
    "Sistem cerdas perumusan racikan tembakau industri berbasis **Aetheris"
    " Kinetic Formulation Matrix** dengan proteksi data rahasia (*Secure"
    " Enterprise Storage*) & Ekspor Laporan Spesifikasi Batch."
)

menu_tab = st.tabs([
    "⚡ Matriks Kinetika & Formulasi",
    "🗄️ Database & Resep Rahasia",
    "📈 Analisis Biaya & Pasok",
])

with menu_tab[0]:
  col1, col2 = st.columns(2)

  with col1:
    st.subheader("📊 Parameter Input Varietas Daun & Saus")

    st.markdown("##### Komposisi Proporsi Tembakau Nusantara (%)")
    virginia_ratio = st.slider("Virginia Leaf (%)", 0, 100, 40)
    temanggung_ratio = st.slider(
        "Temanggung Local (Aromatic/Srintil) (%)", 0, 100, 25
    )
    madura_ratio = st.slider("Madura / Kasturi (Pungent) (%)", 0, 100, 20)
    besuki_ratio = max(
        0, 100 - (virginia_ratio + temanggung_ratio + madura_ratio)
    )
    st.text(f"Besuki / Vorstenlanden (Otomatis): {besuki_ratio}%")

    st.markdown("##### Parameter Biaya Bahan Baku ($/kg)")
    cost_v = st.number_input("Harga Virginia ($/kg)", value=6.5)
    cost_t = st.number_input("Harga Temanggung ($/kg)", value=9.0)
    cost_m = st.number_input("Harga Madura ($/kg)", value=7.5)
    cost_b = st.number_input("Harga Besuki ($/kg)", value=5.5)

    st.markdown("---")
    casing_ph = st.slider("pH Larutan Saus (pH_s)", 4.0, 8.0, 5.5)
    humectant_pct = st.slider("Rasio Humektan / Gliserol (%)", 2.0, 15.0, 8.0)
    combustion_temp = st.slider("Estimasi Suhu Bakar (°C)", 600.0, 900.0, 750.0)

  with col2:
    st.subheader("🔬 Hasil Kalkulasi & Validasi Kinetika")

    target_tar = st.sidebar.slider("Target Tar (mg/batang)", 1.0, 20.0, 12.0)
    target_nicotine = st.sidebar.slider(
        "Target Nikotin (mg/batang)", 0.1, 2.0, 1.0
    )
    target_throat_hit = st.sidebar.slider("Indeks Throat Hit (Th_idx)", 1, 10, 7)


    def calculate_enterprise_matrix(
        v_rat, t_rat, m_rat, b_rat, ph, hum, temp, t_tar, t_nic, t_th
    ):
      matrix_factor = (
          (v_rat * 0.011)
          + (t_rat * 0.018)
          + (m_rat * 0.016)
          + (b_rat * 0.013)
      )
      pi_eff = matrix_factor * (temp / 750.0) * (1.0 + (hum * 0.01))

      ph_dissociation = 1.0 + ((ph - 5.5) * 0.18)
      information_viscosity = (
          (v_rat * 0.12)
          + (t_rat * 0.22)
          + (m_rat * 0.19)
          + (b_rat * 0.15)
      ) / 100 * ph_dissociation

      predicted_tar = max(
          1.2,
          (
              (
                  (v_rat * 0.13)
                  + (t_rat * 0.16)
                  + (m_rat * 0.19)
                  + (b_rat * 0.15)
              )
              - (hum * 0.40)
              - ((temp - 750) * 0.01)
          )
          * pi_eff,
      )
      predicted_nic = max(
          0.05,
          (
              (
                  (v_rat * 0.008)
                  + (t_rat * 0.015)
                  + (m_rat * 0.021)
                  + (b_rat * 0.014)
              )
              * ph_dissociation
              / (hum * 0.04 + 0.85)
          ),
      )
      predicted_th = min(
          10.0,
          max(1.0, (predicted_nic * 4.8) + ((ph - 5.0) * 1.2) + (hum * 0.07)),
      )

      total_cost_per_kg = (
          v_rat * cost_v
          + t_rat * cost_t
          + m_rat * cost_m
          + b_rat * cost_b
      ) / 100.0

      error_margin = (
          abs(predicted_tar - t_tar) * 1.3
          + abs(predicted_nic - t_nic) * 9.0
          + abs(predicted_th - t_th) * 0.7
      )
      consistency_index = max(0.0, min(100.0, 100.0 - error_margin))

      return (
          pi_eff,
          information_viscosity,
          predicted_tar,
          predicted_nic,
          predicted_th,
          consistency_index,
          total_cost_per_kg,
      )


    pi_val, info_visc, p_tar, p_nic, p_th, c_idx, total_cost = (
        calculate_enterprise_matrix(
            virginia_ratio,
            temanggung_ratio,
            madura_ratio,
            besuki_ratio,
            casing_ph,
            humectant_pct,
            combustion_temp,
            target_tar,
            target_nicotine,
            target_throat_hit,
        )
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Tar", f"{p_tar:.2f} mg")
    m2.metric("Nikotin", f"{p_nic:.2f} mg")
    m3.metric("Throat Hit", f"{p_th:.1f}/10")
    m4.metric("Konsistensi", f"{c_idx:.1f}%")

    st.info(
        f"**Analisis Kinetika & Finansial Industri:**\n"
        f"- Konstanta Geometri (pi_eff): **{pi_val:.4f}**\n"
        f"- Viskositas Informasi (nu_i): **{info_visc:.4f}**\n"
        f"- Estimasi Biaya Bahan Baku: **${total_cost:.2f} / kg**"
    )

    blend_name_input = st.text_input(
        "Nama Batch / Kode Formula", "Blend_Nusantara_Alpha_01"
    )
    if st.button("💾 Simpan Formula ke Database Rahasia"):
      conn = sqlite3.connect("aetheris_enterprise.db")
      cursor = conn.cursor()
      cursor.execute(
          """
                INSERT INTO recipes (blend_name, author, virginia, temanggung, madura, besuki, casing_ph, humectant, temp, estimated_tar, estimated_nic, throat_hit, consistency, total_cost, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
          (
              blend_name_input,
              st.session_state["username"],
              virginia_ratio,
              temanggung_ratio,
              madura_ratio,
              besuki_ratio,
              casing_ph,
              humectant_pct,
              combustion_temp,
              p_tar,
              p_nic,
              p_th,
              c_idx,
              total_cost,
              datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
          ),
      )
      conn.commit()
      conn.close()
      st.success(
          f"Formula '{blend_name_input}' berhasil disimpan ke database"
          " perusahaan yang aman!"
      )

with menu_tab[1]:
  st.subheader(
      "🗄️ Manajemen Database & Ekspor Lembar Spesifikasi (Specification Sheet)"
  )
  conn = sqlite3.connect("aetheris_enterprise.db")
  df_recipes = pd.read_sql_query("SELECT * FROM recipes", conn)
  conn.close()

  if not df_recipes.empty:
    st.dataframe(df_recipes, use_container_width=True)

    selected_blend = st.selectbox(
        "Pilih Batch untuk Cetak Lembar Spesifikasi",
        df_recipes["blend_name"].tolist(),
    )
    row_data = df_recipes[df_recipes["blend_name"] == selected_blend].iloc[0]

    if st.button("📄 Generate Laporan Spesifikasi Resmi (HTML / Teks Siap Cetak)"):
      report_text = f"""
==================================================
        AETHERIS BLEND INTELLIGENCE - SPECIFICATION SHEET
==================================================
Nama Formula / Batch : {row_data['blend_name']}
Disusun Oleh         : {row_data['author']}
Waktu Simpan         : {row_data['created_at']}
--------------------------------------------------
KOMPOSISI BAHAN BAKU:
- Virginia Leaf      : {row_data['virginia']}%
- Temanggung Local   : {row_data['temanggung']}%
- Madura / Kasturi   : {row_data['madura']}%
- Besuki / Vorst.    : {row_data['besuki']}%
--------------------------------------------------
PARAMETER KINETIKA & FISIKOKIMIA:
- pH Larutan Saus    : {row_data['casing_ph']}
- Rasio Humektan     : {row_data['humectant']}%
- Suhu Bakar Est.    : {row_data['temp']} C
--------------------------------------------------
PREDIKSI HASIL OUTPUT (LABORATORIUM):
- Kadar Tar          : {row_data['estimated_tar']:.2f} mg
- Kadar Nikotin      : {row_data['estimated_nic']:.2f} mg
- Indeks Throat Hit  : {row_data['throat_hit']:.1f} / 10
- Indeks Konsistensi : {row_data['consistency']:.1f}%
- Estimasi Biaya/kg  : ${row_data['total_cost']:.2f}
==================================================
[STATUS]: RAHASIA & TERVERIFIKASI ENTERPRISE R&D
            """
      st.text_area("Pratinjau Dokumen Spesifikasi Resmi", report_text, height=300)
      st.download_button(
          label="📥 Unduh Dokumen Spesifikasi (.txt)",
          data=report_text,
          file_name=f"Spec_Sheet_{selected_blend}.txt",
          mime="text/plain",
      )
  else:
    st.info("Belum ada resep yang tersimpan di dalam database enterprise.")

with menu_tab[2]:
  st.subheader("📈 Analisis Margin & Optimasi Rantai Pasok")
  st.markdown(
      "Modul ini memproyeksikan efisiensi biaya terhadap target spesifikasi"
      " produk untuk kebutuhan pabrikan rokok komersial."
  )
  if not df_recipes.empty:
    st.bar_chart(
        df_recipes.set_index("blend_name")[["estimated_tar", "total_cost"]]
    )
  else:
    st.info(
        "Simpan beberapa formula pada menu pertama untuk melihat grafik"
        " komparasi biaya dan tar."
    )

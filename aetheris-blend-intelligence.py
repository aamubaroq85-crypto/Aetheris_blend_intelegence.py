import numpy as np
import pandas as pd
import streamlit as st

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Aetheris Blend Intelligence", page_icon="🌿", layout="wide"
)

# Header Utama Aplikasi
st.title("🌿 Aetheris Blend Intelligence (pi_eff)")
st.markdown(
    "Sistem cerdas perumusan racikan tembakau dan saus berbasis **Aetheris"
    " Kinetic Formulation Matrix** dan *Advanced Molecular Information"
    " Theory*."
)

# Sidebar: Pengaturan Target Output
st.sidebar.header("🎯 Target Spesifikasi Produk")
target_tar = st.sidebar.slider("Target Tar (mg/batang)", 1.0, 15.0, 10.0)
target_nicotine = st.sidebar.slider("Target Nikotin (mg/batang)", 0.1, 1.5, 0.8)
target_throat_hit = st.sidebar.slider("Indeks Throat Hit (Th_idx)", 1, 10, 7)
cost_limit = st.sidebar.number_input(
    "Maksimal Biaya Bahan Baku ($/kg)", value=45.0
)

# Main Dashboard Layout
col1, col2 = st.columns(2)

with col1:
  st.subheader("📊 Parameter Input Daun & Saus")
  virginia_ratio = st.slider("Proporsi Daun Virginia (%)", 0, 100, 50)
  burley_ratio = st.slider("Proporsi Daun Burley (%)", 0, 100, 30)
  oriental_ratio = max(0, 100 - (virginia_ratio + burley_ratio))
  st.text(f"Proporsi Daun Oriental (Otomatis): {oriental_ratio}%")

  casing_ph = st.slider("pH Larutan Saus (pH_s)", 4.0, 8.0, 5.5)
  humectant_pct = st.slider("Rasio Humektan / Gliserol (%)", 2.0, 15.0, 8.0)
  combustion_temp = st.slider(
      "Estimasi Suhu Bakar (°C)", 600.0, 900.0, 750.0
  )

with col2:
  st.subheader("🔬 Matriks Kinetika & Viskositas Informasi")


  def calculate_aetheris_kinetic_matrix(
      v_rat, b_rat, o_rat, ph, hum, temp, t_tar, t_nic, t_th
  ):
    # 1. Aetheris Kinetic Formulation Matrix (Koefisien Hambatan Termal & Fluks)
    matrix_factor = v_rat * 0.011 + b_rat * 0.014 + o_rat * 0.016
    pi_eff = matrix_factor * (temp / 750.0) * (1.0 + (hum * 0.01))

    # 2. Viskositas Informasi Senyawa Volatil & Disosiasi Nikotin
    ph_dissociation = 1.0 + ((ph - 5.5) * 0.18)
    information_viscosity = (
        (v_rat * 0.13) + (b_rat * 0.17) + (o_rat * 0.22)
    ) / 100 * ph_dissociation

    # 3. Prediksi Kinetika Output Kimia
    predicted_tar = max(
        1.2,
        (
            (v_rat * 0.14 + b_rat * 0.18 + o_rat * 0.08)
            - (hum * 0.45)
            - ((temp - 750) * 0.012)
        )
        * pi_eff,
    )

    predicted_nic = max(
        0.05,
        (
            (v_rat * 0.009 + b_rat * 0.019 + o_rat * 0.013)
            * ph_dissociation
            / (hum * 0.04 + 0.85)
        ),
    )

    predicted_th = min(
        10.0,
        max(1.0, (predicted_nic * 5.2) + ((ph - 5.0) * 1.3) + (hum * 0.08)),
    )

    # 4. Evaluasi Deviasi dan Konsistensi Matriks
    error_margin = (
        abs(predicted_tar - t_tar) * 1.4
        + abs(predicted_nic - t_nic) * 9.5
        + abs(predicted_th - t_th) * 0.75
    )
    consistency_index = max(0.0, min(100.0, 100.0 - error_margin))

    return (
        pi_eff,
        information_viscosity,
        predicted_tar,
        predicted_nic,
        predicted_th,
        consistency_index,
    )


  if st.button("Jalankan Matriks Kinetika Lanjutan", type="primary"):
    (
        pi_val,
        info_visc,
        p_tar,
        p_nic,
        p_th,
        c_idx,
    ) = calculate_aetheris_kinetic_matrix(
        virginia_ratio,
        burley_ratio,
        oriental_ratio,
        casing_ph,
        humectant_pct,
        combustion_temp,
        target_tar,
        target_nicotine,
        target_throat_hit,
    )

    st.success(
        "Kalkulasi Berhasil: Matriks Kinetika Aetheris Telah Disinkronisasi!"
    )

    # Menampilkan Metrik Hasil
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Estimasi Tar", f"{p_tar:.2f} mg", delta=f"{p_tar - target_tar:.2f}")
    m2.metric(
        "Estimasi Nikotin",
        f"{p_nic:.2f} mg",
        delta=f"{p_nic - target_nicotine:.2f}",
    )
    m3.metric(
        "Throat Hit", f"{p_th:.1f}/10", delta=f"{p_th - target_throat_hit:.1f}"
    )
    m4.metric("Konsistensi", f"{c_idx:.1f}%")

    # Detail Analisis Matriks Kinetika (Aman dari SyntaxError)
    st.info(
        "Aetheris Kinetic Formulation Metrics:\n"
        f"- Konstanta Geometri Dinamis (pi_eff): **{pi_val:.4f}**\n"
        f"- Viskositas Informasi Molekul (nu_i): **{info_visc:.4f}**\n"
        f"- Status Kinetika Suhu & pH: Stabil pada pH_s {casing_ph} dan"
        f" {combustion_temp} C."
    )
  else:
    st.info(
        "Atur variabel parameter pada panel kiri, lalu klik tombol untuk"
        " mengeksekusi matriks kinetika."
    )

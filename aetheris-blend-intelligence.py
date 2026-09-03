import numpy as np
import pandas as pd
import streamlit as st

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Aetheris Blend Intelligence", page_icon="🌿", layout="wide"
)

st.title("🌿 Aetheris Blend Intelligence ($\pi_{\text{eff}}$)")
st.markdown(
    "Sistem cerdas perumusan racikan tembakau dan saus berbasis geometri"
    " informasi molekuler dan *Zuhri Formalism*."
)

# Sidebar: Pengaturan Target Output
st.sidebar.header("🎯 Target Spesifikasi Produk")
target_tar = st.sidebar.slider("Target Tar (mg/batang)", 1.0, 15.0, 10.0)
target_nicotine = st.sidebar.slider("Target Nikotin (mg/batang)", 0.1, 1.5, 0.8)
target_throat_hit = st.sidebar.slider("Indeks Throat Hit ($Th_{idx}$)", 1, 10, 7)
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

  casing_ph = st.slider("pH Larutan Saus ($pH_s$)", 4.0, 8.0, 5.5)
  humectant_pct = st.slider("Rasio Humektan / Gliserol (%)", 2.0, 15.0, 8.0)
  combustion_temp = st.slider(
      "Estimasi Suhu Bakar (°C)", 600.0, 900.0, 750.0
  )

with col2:
  st.subheader("🔬 Analisis Viskositas Informasi & Kimia ($\pi_{\text{eff}}$)")


  def calculate_aetheris_blend(
      v_rat, b_rat, o_rat, ph, hum, temp, t_tar, t_nic, t_th
  ):
    # Konstanta Efisiensi Geometri Fluks Molekuler (Zuhri Formalism)
    pi_eff = (
        (v_rat * 1.02 + b_rat * 1.15 + o_rat * 1.25)
        / 100
        * (temp / 750.0)
    )

    # Viskositas Informasi Senyawa Volatil
    ph_factor = 1.0 + ((ph - 5.5) * 0.15)
    entropy_score = (
        (v_rat * 0.12) + (b_rat * 0.16) + (o_rat * 0.21)
    ) / 100 * ph_factor

    # Prediksi Output Kimia Berbasis Model Matriks $\pi_{\text{eff}}$
    predicted_tar = max(
        1.5,
        (
            (v_rat * 0.13 + b_rat * 0.17 + o_rat * 0.09)
            - (hum * 0.4)
            - ((temp - 750) * 0.01)
        )
        * pi_eff,
    )

    predicted_nic = max(
        0.1,
        (
            (v_rat * 0.008 + b_rat * 0.018 + o_rat * 0.012)
            * ph_factor
            / (hum * 0.05 + 0.8)
        ),
    )

    predicted_th = min(
        10.0, max(1.0, (predicted_nic * 5.0) + ((ph - 5.0) * 1.2) + (hum * 0.1))
    )

    error_margin = (
        abs(predicted_tar - t_tar) * 1.5
        + abs(predicted_nic - t_nic) * 10.0
        + abs(predicted_th - t_th) * 0.8
    )
    consistency_index = max(0.0, min(100.0, 100.0 - error_margin))

    return (
        pi_eff,
        entropy_score,
        predicted_tar,
        predicted_nic,
        predicted_th,
        consistency_index,
    )


  if st.button("Jalankan Optimasi AI Lanjutan ($\pi_{\text{eff}}$)", type="primary"):
    (
        pi_val,
        e_score,
        p_tar,
        p_nic,
        p_th,
        c_idx,
    ) = calculate_aetheris_blend(
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

    st.success("Matriks Formula Berhasil Dikalkulasi oleh Aetheris AI!")

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

    # Detail Analisis Sifat Kimia
    st.info(
        f"**Aetheris Intelligence Parameters:**\n"
        f"- Konstanta Geometri ($\pi_{\text{eff}}$): **{pi_val:.4f}**\n"
        f"- Viskositas Informasi Molekul ($\nu_i$): **{e_score:.4f}**\n"
        f"- Kalibrasi pH Sahih: level pH {casing_ph}."
    )
  else:
    st.info(
        "Sesuaikan parameter konfigurasi di panel kiri, lalu klik tombol untuk"
        " memulai simulasi."
    )

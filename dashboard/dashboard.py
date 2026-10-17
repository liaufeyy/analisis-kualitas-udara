import os

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Dashboard Kualitas Udara Beijing", page_icon="🌫️", layout="wide")

MERAH = "#d62728"
ABU = "#c7c7c7"
KATEGORI = ["Baik", "Sedang", "Tidak Sehat bagi Kelompok Sensitif",
            "Tidak Sehat", "Sangat Tidak Sehat", "Berbahaya"]
WARNA_KATEGORI = ["#2ca02c", "#bcbd22", "#ff7f0e", "#d62728", "#8c564b", "#4d4d4d"]


@st.cache_data
def load_data():
    path = os.path.join(os.path.dirname(__file__), "main_data.csv")
    return pd.read_csv(path)


def rata_rata(df, by):
    """Rata-rata PM2.5 tertimbang (total PM2.5 dibagi jumlah jam)."""
    g = df.groupby(by)[["total_pm25", "jumlah_jam"]].sum()
    return (g["total_pm25"] / g["jumlah_jam"]).rename("PM2.5")


data = load_data()
semua_stasiun = sorted(data["station"].unique())
tahun_min, tahun_max = int(data["year"].min()), int(data["year"].max())

# ---------------- Sidebar ----------------
st.sidebar.header("Filter")
stasiun_dipilih = st.sidebar.multiselect("Stasiun", semua_stasiun, default=semua_stasiun)
rentang_tahun = st.sidebar.slider("Rentang tahun (Pertanyaan 2 dan kategori udara)",
                                  tahun_min, tahun_max, (tahun_min, tahun_max))
st.sidebar.caption("Data: Maret 2013 - Februari 2017, sehingga tahun 2013 dan 2017 tidak penuh 12 bulan.")

if not stasiun_dipilih:
    st.warning("Pilih minimal satu stasiun di sidebar.")
    st.stop()

df_stasiun = data[data["station"].isin(stasiun_dipilih)]
df_rentang = df_stasiun[df_stasiun["year"].between(*rentang_tahun)]

# ---------------- Header ----------------
st.title("Dashboard Kualitas Udara (PM2.5) Beijing")
st.write("Analisis rata-rata PM2.5 dari 12 stasiun pemantauan di Beijing, Maret 2013 - Februari 2017.")

pm_hour = rata_rata(df_rentang, "hour")
pm_season = rata_rata(df_rentang, "season").sort_values(ascending=False)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Rata-rata PM2.5", f"{df_rentang['total_pm25'].sum() / df_rentang['jumlah_jam'].sum():.1f} µg/m³")
col2.metric("Jam puncak", f"{pm_hour.idxmax()}:00", f"{pm_hour.max():.1f} µg/m³", delta_color="off")
col3.metric("Musim tertinggi", pm_season.idxmax(), f"{pm_season.max():.1f} µg/m³", delta_color="off")
col4.metric("Jumlah stasiun", len(stasiun_dipilih))

# ---------------- Pertanyaan 1 ----------------
st.header("Pertanyaan 1: Stasiun dengan PM2.5 tertinggi dan terendah")
tahun_q1 = st.selectbox("Tahun", sorted(data["year"].unique()),
                        index=sorted(data["year"].unique()).index(2016))

pm_station = rata_rata(df_stasiun[df_stasiun["year"] == tahun_q1], "station").sort_values()
if pm_station.empty:
    st.info("Tidak ada data untuk pilihan ini.")
else:
    warna = [MERAH if s == pm_station.idxmax() else ABU for s in pm_station.index]
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(pm_station.index, pm_station.values, color=warna)
    ax.set_title(f"Rata-rata PM2.5 per Stasiun di Beijing ({tahun_q1})", fontsize=14)
    ax.set_xlabel("PM2.5 (µg/m³)", fontsize=12)
    ax.set_ylabel("Stasiun", fontsize=12)
    ax.set_xlim(0, pm_station.max() * 1.15)
    for bar in bars:
        ax.text(bar.get_width() + 0.8, bar.get_y() + bar.get_height() / 2,
                f"{bar.get_width():.1f}", va="center", fontsize=10)
    plt.tight_layout()
    st.pyplot(fig)

    st.write(f"Pada {tahun_q1}, **{pm_station.idxmax()}** tertinggi ({pm_station.max():.1f} µg/m³) dan "
             f"**{pm_station.idxmin()}** terendah ({pm_station.min():.1f} µg/m³), "
             f"selisih sekitar **{pm_station.max() - pm_station.min():.1f} µg/m³**.")

# ---------------- Pertanyaan 2 ----------------
st.header("Pertanyaan 2: Jam dan musim dengan PM2.5 tertinggi")
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].plot(pm_hour.index, pm_hour.values, color="#7f7f7f", linewidth=2)
axes[0].scatter(pm_hour.idxmax(), pm_hour.max(), color=MERAH, zorder=3)
axes[0].annotate(f"Tertinggi: {pm_hour.max():.1f} (jam {pm_hour.idxmax()})",
                 (pm_hour.idxmax(), pm_hour.max()), textcoords="offset points",
                 xytext=(-110, 8), fontsize=10, color=MERAH)
axes[0].set_title("Rata-rata PM2.5 per Jam", fontsize=13)
axes[0].set_xlabel("Jam", fontsize=12)
axes[0].set_ylabel("PM2.5 (µg/m³)", fontsize=12)
axes[0].set_xticks(range(0, 24, 2))
axes[0].set_ylim(0, pm_hour.max() * 1.2)

warna_musim = [MERAH if s == pm_season.idxmax() else ABU for s in pm_season.index]
bars = axes[1].bar(pm_season.index, pm_season.values, color=warna_musim)
axes[1].set_title("Rata-rata PM2.5 per Musim", fontsize=13)
axes[1].set_xlabel("Musim", fontsize=12)
axes[1].set_ylabel("PM2.5 (µg/m³)", fontsize=12)
axes[1].set_ylim(0, pm_season.max() * 1.15)
for bar in bars:
    axes[1].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                 f"{bar.get_height():.1f}", ha="center", fontsize=10)
plt.tight_layout()
st.pyplot(fig)

st.write(f"Jam tertinggi: **{pm_hour.idxmax()}:00** ({pm_hour.max():.1f} µg/m³), terendah: "
         f"**{pm_hour.idxmin()}:00** ({pm_hour.min():.1f} µg/m³). "
         f"Musim tertinggi: **{pm_season.idxmax()}** ({pm_season.max():.1f} µg/m³), terendah: "
         f"**{pm_season.idxmin()}** ({pm_season.min():.1f} µg/m³).")

# ---------------- Analisis lanjutan ----------------
st.header("Analisis Lanjutan: Kategori Kualitas Udara")
st.write("PM2.5 dikelompokkan ke kategori kualitas udara (binning, acuan AQI US EPA) "
         "untuk melihat proporsi jam dengan kualitas udara buruk di tiap stasiun.")

tabel = (df_rentang.pivot_table(index="station", columns="kategori_pm25",
                                values="jumlah_jam", aggfunc="sum", fill_value=0)
         .reindex(columns=KATEGORI, fill_value=0))
tabel = tabel.div(tabel.sum(axis=1), axis=0) * 100

fig, ax = plt.subplots(figsize=(12, 6))
tabel.sort_values("Baik").plot(kind="barh", stacked=True, color=WARNA_KATEGORI, ax=ax)
ax.set_title("Proporsi Jam per Kategori Kualitas Udara (PM2.5) per Stasiun", fontsize=14)
ax.set_xlabel("Proporsi Jam (%)", fontsize=12)
ax.set_ylabel("Stasiun", fontsize=12)
ax.set_xlim(0, 100)
ax.legend(title="Kategori", bbox_to_anchor=(1.02, 1), loc="upper left")
plt.tight_layout()
st.pyplot(fig)

st.caption("Sumber data: Beijing Multi-Site Air-Quality Data (PRSA), Maret 2013 - Februari 2017.")
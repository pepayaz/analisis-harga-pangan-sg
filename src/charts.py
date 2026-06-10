"""
04_charts.py
------------
Membuat empat grafik yang digunakan dalam makalah:

Gambar 1 - Tren harga bulanan tiga komoditas (2023–2025)
Gambar 2 - Perbandingan Koefisien Variasi (CV) tiga komoditas
Gambar 3 - Perubahan harga bulanan cabai rawit merah dengan penandaan kejadian ekstrem
Gambar 4 - Perbandingan harga tahunan (min, rata-rata, maks) per komoditas
"""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from src.extreme_events import identify_extreme_events

OUTPUT_DIR = Path(__file__).parent.parent / "outputs"

# Warna per komoditas
WARNA = {
    "Beras Medium": "#185FA5",
    "Cabai Rawit Merah": "#993C1D",
    "Daging Ayam Ras": "#0F6E56",
}

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linestyle": "--",
    "axes.facecolor": "white",
    "figure.facecolor": "white",
})


def _format_rupiah(value, _):
    """Formatter sumbu Y: menampilkan harga dalam satuan ribu Rupiah."""
    return f"Rp{value/1000:.0f}rb"


def _label_bulan(index: pd.DatetimeIndex, step: int = 3) -> list[str]:
    """Menghasilkan label bulan singkat untuk sumbu X."""
    labels = []
    for i, dt in enumerate(index):
        if i % step == 0:
            labels.append(dt.strftime("%b %y"))
        else:
            labels.append("")
    return labels


def buat_gambar1_tren(df: pd.DataFrame) -> Path:
    """
    Gambar 1: Tren harga bulanan tiga komoditas, Januari 2023 – Desember 2025.
    Mencakup anotasi lonjakan harga terbesar dan shading per tahun.
    """
    fig, ax = plt.subplots(figsize=(12, 5))

    for col, color in WARNA.items():
        style = "--" if col == "Daging Ayam Ras" else "-"
        marker = "s" if col == "Daging Ayam Ras" else ("o" if col == "Beras Medium" else "^")
        ax.plot(
            df.index, df[col],
            color=color, lw=2, linestyle=style,
            marker=marker, markersize=2.5,
            label=col,
        )

    # Shading per tahun
    for year, label in [(2023, "2023"), (2024, "2024"), (2025, "2025")]:
        year_data = df[df.index.year == year]
        if len(year_data) == 0:
            continue
        ax.axvspan(
            year_data.index[0], year_data.index[-1],
            alpha=0.04, color="gray"
        )
        mid = year_data.index[len(year_data) // 2]
        ax.text(mid, df.max().max() * 1.04, label,
                ha="center", fontsize=9, color="gray", alpha=0.7)

    # Anotasi dua titik paling informatif pada grafik cabai:
    # - Titik 1: lonjakan % terbesar di tahun pertama data (sinyal awal volatilitas)
    # - Titik 2: bulan dengan harga absolut tertinggi sepanjang periode (puncak krisis)
    # Pendekatan ini dinamis — tidak bergantung pada tahun tertentu yang di-hardcode.
    cabai = df["Cabai Rawit Merah"]
    pct = cabai.pct_change() * 100

    first_year = df.index.year.min()
    pct_first_year = pct[(pct > 0) & (pct.index.year == first_year)]
    date_first_year_spike = pct_first_year.idxmax()  # lonjakan terbesar di tahun pertama
    date_price_peak = cabai.idxmax()                  # harga absolut tertinggi

    for date in sorted({date_first_year_spike, date_price_peak}):
        val = pct[date]
        idx = df.index.get_loc(date)
        ax.annotate(
            f"+{val:.1f}%\n{date.strftime('%b %y')}",
            xy=(date, cabai[date]),
            xytext=(df.index[max(0, idx - 3)], cabai[date] + 8000),
            fontsize=7.5, color=WARNA["Cabai Rawit Merah"],
            arrowprops=dict(arrowstyle="->", color=WARNA["Cabai Rawit Merah"], lw=1),
        )

    # Anotasi kenaikan total beras
    try:
        total_change = (df["Beras Medium"].iloc[-1] - df["Beras Medium"].iloc[0]) / df["Beras Medium"].iloc[0] * 100
        total_text = f"{total_change:+.1f}%\n(total)"
    except Exception:
        total_text = "+N/A%\n(total)"

    ax.annotate(
        total_text,
        xy=(df.index[-1], df["Beras Medium"].iloc[-1]),
        xytext=(df.index[-6], df["Beras Medium"].iloc[-1] + 1500),
        fontsize=7.5, color=WARNA["Beras Medium"],
        arrowprops=dict(arrowstyle="->", color=WARNA["Beras Medium"], lw=1),
    )

    ax.set_xticks(df.index[::3])
    ax.set_xticklabels(
        [d.strftime("%b %y") for d in df.index[::3]],
        rotation=30, ha="right", fontsize=8,
    )
    ax.yaxis.set_major_formatter(plt.FuncFormatter(_format_rupiah))
    ax.set_ylabel("Harga (Rp/kg)", fontsize=10)
    ax.set_ylim(0, df.max().max() * 1.15)
    ax.set_title(
        "Gambar 1. Tren Harga Bulanan Tiga Komoditas Strategis\n"
        "Januari 2023 – Desember 2025  (Sumber: PIHPS Bank Indonesia)",
        fontsize=10, pad=12,
    )
    ax.legend(loc="upper left", fontsize=9, framealpha=0.9)

    fig.tight_layout()
    out = OUTPUT_DIR / "gambar1_tren_harga.png"
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return out


def buat_gambar2_cv(df: pd.DataFrame) -> Path:
    """
    Gambar 2: Perbandingan Koefisien Variasi (CV) tiga komoditas.
    CV = (standar deviasi / rata-rata) x 100%
    """
    cv_values = {
        col: (df[col].std() / df[col].mean()) * 100
        for col in df.columns
    }
    # Urutkan dari terkecil ke terbesar agar grafik lebih mudah dibaca
    sorted_items = sorted(cv_values.items(), key=lambda x: x[1])
    labels = [item[0] for item in sorted_items]
    values = [item[1] for item in sorted_items]
    colors = [WARNA[l] for l in labels]

    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.barh(labels, values, color=colors, height=0.5, edgecolor="white")

    for bar, val in zip(bars, values):
        ax.text(
            val + 0.3, bar.get_y() + bar.get_height() / 2,
            f"{val:.1f}%", va="center", fontsize=11,
            fontweight="bold", color=bar.get_facecolor(),
        )

    ax.axvline(x=10, color="orange", lw=1.5, linestyle="--", alpha=0.7,
               label="Ambang volatilitas tinggi (10%)")
    ax.set_xlabel("Koefisien Variasi / CV (%)", fontsize=10)
    ax.set_title(
        "Gambar 2. Perbandingan Koefisien Variasi Harga Tiga Komoditas\n"
        "Januari 2023 – Desember 2025  (Sumber: PIHPS Bank Indonesia)",
        fontsize=10, pad=10,
    )
    ax.legend(fontsize=8, loc="lower right")
    ax.set_xlim(0, max(values) * 1.2)
    ax.grid(axis="x", alpha=0.3)
    ax.grid(axis="y", visible=False)

    fig.tight_layout()
    out = OUTPUT_DIR / "gambar2_koefisien_variasi.png"
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return out


def buat_gambar3_perubahan_cabai(df: pd.DataFrame) -> Path:
    """
    Gambar 3: Perubahan harga bulanan cabai rawit merah (%) dengan
    penandaan kejadian perubahan harga ekstrem (lebih dari ±10%).
    """
    cabai = df["Cabai Rawit Merah"]
    pct = cabai.pct_change() * 100
    pct = pct.dropna()

    bar_colors = [
        WARNA["Cabai Rawit Merah"] if v > 0 else "#2E7D5E"
        for v in pct.values
    ]

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.bar(pct.index, pct.values, color=bar_colors, alpha=0.8, width=20)

    ax.axhline(y=10, color="orange", lw=1.5, linestyle="--", alpha=0.8,
               label="Ambang +10%")
    ax.axhline(y=-10, color="steelblue", lw=1.5, linestyle="--", alpha=0.8,
               label="Ambang -10%")
    ax.axhline(y=0, color="black", lw=0.8, alpha=0.5)

    # Label untuk perubahan lebih dari ±20%
    for date, val in pct.items():
        if abs(val) > 20:
            ax.text(
                date, val + (2.5 if val > 0 else -4),
                f"{val:+.0f}%",
                ha="center", fontsize=7, fontweight="bold",
                color=WARNA["Cabai Rawit Merah"] if val > 0 else "#2E7D5E",
            )

    ax.set_xticks(df.index[::3])
    ax.set_xticklabels(
        [d.strftime("%b %y") for d in df.index[::3]],
        rotation=30, ha="right", fontsize=8,
    )
    ax.set_ylabel("Perubahan harga (%)", fontsize=10)
    # Hitung jumlah kejadian ekstrem cabai rawit merah saja
    try:
        events = identify_extreme_events(df)
        n_events = len(events[events["Komoditas"] == "Cabai Rawit Merah"])
    except Exception:
        n_events = "N/A"

    ax.set_title(
        f"Gambar 3. Perubahan Harga Bulanan Cabai Rawit Merah (%)\n"
        f"{n_events} Kejadian Perubahan Harga Ekstrem (≥±10%)  (Sumber: PIHPS Bank Indonesia)",
        fontsize=10, pad=10,
    )
    ax.legend(fontsize=8, loc="upper right")

    fig.tight_layout()
    out = OUTPUT_DIR / "gambar3_perubahan_cabai.png"
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return out


def buat_gambar4_tahunan(df: pd.DataFrame) -> Path:
    """
    Gambar 4: Perbandingan harga tahunan (min, rata-rata, maks) per komoditas
    untuk tahun 2023, 2024, dan 2025.
    """
    years = sorted(df.index.year.unique())
    commodities = list(df.columns)

    fig, axes = plt.subplots(1, 3, figsize=(13, 4.5))

    for ax, col in zip(axes, commodities):
        color = WARNA[col]
        yearly_min = [df.loc[df.index.year == y, col].min() for y in years]
        yearly_mean = [df.loc[df.index.year == y, col].mean() for y in years]
        yearly_max = [df.loc[df.index.year == y, col].max() for y in years]
        xi = np.arange(len(years))

        ax.bar(xi, yearly_max, color=color, alpha=0.25, width=0.55, label="Maks")
        ax.bar(xi, yearly_mean, color=color, alpha=0.75, width=0.55, label="Rata-rata")
        ax.bar(xi, yearly_min, color="white", alpha=1.0, width=0.55,
               edgecolor=color, linewidth=1.5, label="Min")

        for i, (mn, avg, mx) in enumerate(zip(yearly_min, yearly_mean, yearly_max)):
            ax.text(i, mx * 1.02, _format_rupiah(mx, None),
                    ha="center", fontsize=7.5, color="#333")
            ax.text(i, mn * 0.93, _format_rupiah(mn, None),
                    ha="center", fontsize=7.5, color="#333", va="top")

        ax.set_xticks(xi)
        ax.set_xticklabels([str(y) for y in years], fontsize=9)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(_format_rupiah))
        ax.set_title(col, fontsize=9.5, fontweight="bold", pad=6)
        ax.legend(fontsize=7.5, loc="upper left")
        ax.set_ylim(0, max(yearly_max) * 1.20)

    fig.suptitle(
        "Gambar 4. Perbandingan Harga Tahunan per Komoditas (Min, Rata-rata, Maks)\n"
        "Sumber: PIHPS Bank Indonesia",
        fontsize=10, y=1.02,
    )
    fig.tight_layout()
    out = OUTPUT_DIR / "gambar4_perbandingan_tahunan.png"
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return out


def buat_semua_grafik(df: pd.DataFrame) -> None:
    """Membuat semua grafik sekaligus dan menyimpannya ke folder outputs/."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Membuat Gambar 1: Tren harga bulanan...")
    out1 = buat_gambar1_tren(df)
    print(f"  Tersimpan: {out1}")

    print("Membuat Gambar 2: Perbandingan CV...")
    out2 = buat_gambar2_cv(df)
    print(f"  Tersimpan: {out2}")

    print("Membuat Gambar 3: Perubahan harga cabai rawit...")
    out3 = buat_gambar3_perubahan_cabai(df)
    print(f"  Tersimpan: {out3}")

    print("Membuat Gambar 4: Perbandingan tahunan...")
    out4 = buat_gambar4_tahunan(df)
    print(f"  Tersimpan: {out4}")

    print("\nSemua grafik berhasil dibuat.")


if __name__ == "__main__":
    from src.load_data import load_all

    df = load_all()
    buat_semua_grafik(df)
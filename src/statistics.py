"""
02_statistics.py
----------------
Menghitung statistik deskriptif dan Koefisien Variasi (CV) untuk setiap komoditas.

Koefisien Variasi (CV) digunakan sebagai ukuran volatilitas relatif yang dapat
dibandingkan antarkomoditas secara adil meskipun skala harga absolutnya berbeda.
Pendekatan ini mengacu pada Sumaryanto (2009).

Formula:
    CV = (standar_deviasi / rata_rata) * 100  [dalam persen]
"""

import pandas as pd
import numpy as np


def compute_descriptive_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame harga bulanan dengan kolom per komoditas.

    Returns
    -------
    pd.DataFrame
        Tabel statistik dengan baris per komoditas.
    """
    stats = {}

    for col in df.columns:
        series = df[col].dropna()
        cv = (series.std() / series.mean()) * 100

        stats[col] = {
            "Jumlah Data (bulan)": len(series),
            "Harga Minimum (Rp/kg)": int(series.min()),
            "Harga Maksimum (Rp/kg)": int(series.max()),
            "Rata-rata (Rp/kg)": int(series.mean()),
            "Standar Deviasi (Rp)": int(series.std()),
            "CV (%)": round(cv, 1),
            "Perubahan Total (%)": round(
                (series.iloc[-1] - series.iloc[0]) / series.iloc[0] * 100, 1
            ),
        }

    result = pd.DataFrame(stats).T
    result.index.name = "Komoditas"
    return result


def compute_yearly_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Menghitung statistik per tahun untuk setiap komoditas.

    Returns
    -------
    pd.DataFrame
        Multi-index DataFrame (Komoditas, Tahun) dengan statistik per tahun.
    """
    records = []

    for col in df.columns:
        for year in sorted(df.index.year.unique()):
            yearly = df.loc[df.index.year == year, col].dropna()
            if len(yearly) == 0:
                continue
            records.append({
                "Komoditas": col,
                "Tahun": year,
                "Min (Rp/kg)": int(yearly.min()),
                "Rata-rata (Rp/kg)": int(yearly.mean()),
                "Maks (Rp/kg)": int(yearly.max()),
            })

    result = pd.DataFrame(records)

    # Tambahkan kolom perubahan rata-rata dan maks terhadap tahun sebelumnya
    result = result.sort_values(["Komoditas", "Tahun"]).reset_index(drop=True)
    result["Perub. Rata-rata (%)"] = (
        result.groupby("Komoditas")["Rata-rata (Rp/kg)"]
        .pct_change()
        .mul(100)
        .round(1)
    )
    result["Perub. Maks (%)"] = (
        result.groupby("Komoditas")["Maks (Rp/kg)"]
        .pct_change()
        .mul(100)
        .round(1)
    )

    return result


if __name__ == "__main__":
    from src.load_data import load_all

    df = load_all()

    print("=" * 60)
    print("STATISTIK DESKRIPTIF (Januari 2023 – Desember 2025)")
    print("=" * 60)
    stats = compute_descriptive_stats(df)
    print(stats.to_string())

    print("\n" + "=" * 60)
    print("STATISTIK PER TAHUN")
    print("=" * 60)
    yearly = compute_yearly_stats(df)
    print(yearly.to_string(index=False))

"""
03_extreme_events.py
--------------------
Mengidentifikasi kejadian perubahan harga ekstrem, yaitu kenaikan atau penurunan
harga lebih dari 10 persen dalam satu bulan.

Catatan metodologis:
Ambang 10 persen digunakan sebagai batas operasional sederhana untuk tujuan
deskriptif dalam makalah ini. Ini bukan standar resmi sistem peringatan dini
pemerintah, melainkan alat bantu agar kejadian ekstrem dapat diidentifikasi
secara konsisten dan dapat dibandingkan antarkomoditas.
"""

import pandas as pd
import numpy as np


THRESHOLD_PCT = 10.0  # persen


def compute_monthly_changes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Menghitung perubahan harga bulanan (persen) untuk setiap komoditas.

    Returns
    -------
    pd.DataFrame
        DataFrame perubahan persentase bulanan.
    """
    return df.pct_change() * 100


def identify_extreme_events(
    df: pd.DataFrame,
    threshold: float = THRESHOLD_PCT
) -> pd.DataFrame:
    """
    Mengidentifikasi bulan-bulan dengan perubahan harga ekstrem.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame harga bulanan.
    threshold : float
        Ambang perubahan harga (persen). Default 10 persen.

    Returns
    -------
    pd.DataFrame
        DataFrame dengan semua kejadian ekstrem, berisi kolom:
        tanggal, komoditas, harga_sebelumnya, harga_sekarang,
        perubahan_pct, arah (naik/turun).
    """
    changes = compute_monthly_changes(df)
    records = []

    for col in changes.columns:
        for date, pct in changes[col].items():
            if pd.isna(pct):
                continue
            if abs(pct) > threshold:
                prev_date = changes.index[changes.index.get_loc(date) - 1]
                records.append({
                    "Tanggal": date,
                    "Komoditas": col,
                    "Harga Sebelumnya (Rp/kg)": int(df.loc[prev_date, col]),
                    "Harga Sekarang (Rp/kg)": int(df.loc[date, col]),
                    "Perubahan (%)": round(pct, 1),
                    "Arah": "Naik" if pct > 0 else "Turun",
                })

    result = pd.DataFrame(records)
    if not result.empty:
        result = result.sort_values(["Komoditas", "Tanggal"]).reset_index(drop=True)
    return result


def summarize_extreme_events(df: pd.DataFrame) -> pd.DataFrame:
    """
    Merangkum jumlah dan intensitas kejadian ekstrem per komoditas.
    """
    events = identify_extreme_events(df)
    if events.empty:
        return pd.DataFrame()

    summary = (
        events.groupby("Komoditas")
        .agg(
            Total_Kejadian=("Perubahan (%)", "count"),
            Kejadian_Naik=("Arah", lambda x: (x == "Naik").sum()),
            Kejadian_Turun=("Arah", lambda x: (x == "Turun").sum()),
            Perubahan_Terbesar=("Perubahan (%)", "max"),
            Penurunan_Terdalam=("Perubahan (%)", "min"),
        )
        .reset_index()
    )
    return summary


if __name__ == "__main__":
    from src.load_data import load_all

    df = load_all()

    print("=" * 70)
    print(f"KEJADIAN PERUBAHAN HARGA EKSTREM (ambang ±{THRESHOLD_PCT}% per bulan)")
    print("=" * 70)

    events = identify_extreme_events(df)
    print(f"\nTotal kejadian ditemukan: {len(events)}\n")
    print(events.to_string(index=False))

    print("\n" + "=" * 70)
    print("RINGKASAN PER KOMODITAS")
    print("=" * 70)
    summary = summarize_extreme_events(df)
    print(summary.to_string(index=False))

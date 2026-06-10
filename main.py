"""
main.py
-------
Menjalankan seluruh pipeline analisis sekaligus:
1. Memuat data dari PIHPS Bank Indonesia
2. Menghitung statistik deskriptif dan CV
3. Mengidentifikasi kejadian perubahan harga ekstrem
4. Membuat semua grafik

Jalankan dari root folder repositori:
    python main.py
"""

import sys
from pathlib import Path

# Tambahkan root ke sys.path agar import src.* bekerja
sys.path.insert(0, str(Path(__file__).parent))

from src.load_data import load_all
from src.statistics import compute_descriptive_stats, compute_yearly_stats
from src.extreme_events import identify_extreme_events, summarize_extreme_events
from src.charts import buat_semua_grafik


def main():
    print("=" * 65)
    print("ANALISIS VOLATILITAS HARGA PANGAN STRATEGIS INDONESIA")
    print("Periode: Januari 2023 – Desember 2025")
    print("Sumber data: PIHPS Bank Indonesia")
    print("=" * 65)

    # 1. Muat data
    print("\n[1/4] Memuat data dari folder data/...")
    df = load_all()
    print(f"      Berhasil: {len(df)} titik data bulanan")
    print(f"      Rentang: {df.index.min().strftime('%B %Y')} — "
          f"{df.index.max().strftime('%B %Y')}")

    # 2. Statistik deskriptif
    print("\n[2/4] Menghitung statistik deskriptif dan CV...")
    stats = compute_descriptive_stats(df)
    print("\nStatistik Deskriptif (Januari 2023 – Desember 2025):")
    print(stats.to_string())

    yearly = compute_yearly_stats(df)
    print("\nRingkasan Harga Per Tahun:")
    print(yearly.to_string(index=False))

    # 3. Kejadian ekstrem
    print("\n[3/4] Mengidentifikasi kejadian perubahan harga ekstrem (>±10%)...")
    events = identify_extreme_events(df)
    summary = summarize_extreme_events(df)
    print(f"\nTotal kejadian perubahan harga ekstrem: {len(events)}")
    print("\nRingkasan per komoditas:")
    print(summary.to_string(index=False))
    print("\nDaftar lengkap kejadian:")
    print(events.to_string(index=False))

    # 4. Grafik
    print("\n[4/4] Membuat grafik...")
    buat_semua_grafik(df)

    print("\n" + "=" * 65)
    print("Analisis selesai. Grafik tersimpan di folder outputs/")
    print("=" * 65)


if __name__ == "__main__":
    main()

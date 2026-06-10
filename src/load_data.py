"""
01_load_data.py
---------------
Membaca dan membersihkan file ekspor Excel dari dashboard PIHPS Bank Indonesia.

Setiap file PIHPS memiliki format:
- Baris 0: header (nama kolom berisi tanggal)
- Baris 1: data Semua Provinsi (nasional)
- Baris 2+: data per provinsi

Fungsi utama:
- load_pihps_file(): membaca satu file dan mengembalikan Series harga bulanan
- load_all(): memuat ketiga komoditas sekaligus
"""

from pathlib import Path
import numpy as np
import pandas as pd
import difflib
import re


DATA_DIR = Path(__file__).parent.parent / "data"

# Pemetaan nama file ke nama komoditas yang digunakan dalam analisis
COMMODITY_FILES = {
    "Beras Medium": "beras_medium.xlsx",
    "Cabai Rawit Merah": "cabai_rawit_merah.xlsx",
    "Daging Ayam Ras": "daging_ayam_ras.xlsx",
}


def _parse_price(value) -> float:
    """Mengubah nilai harga dari string format PIHPS ke float."""
    if pd.isna(value):
        return np.nan
    cleaned = str(value).replace(",", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return np.nan


def load_pihps_file(filepath: Path, commodity_name: str) -> pd.Series:
    """
    Membaca file ekspor Excel PIHPS dan mengembalikan Series harga bulanan
    untuk level nasional (Semua Provinsi).

    Parameters
    ----------
    filepath : Path
        Path ke file .xlsx hasil unduhan PIHPS.
    commodity_name : str
        Nama komoditas yang digunakan sebagai nama Series.

    Returns
    -------
    pd.Series
        Series dengan index DatetimeIndex (bulanan) dan nilai harga Rp/kg.
    """
    df = pd.read_excel(filepath, sheet_name=0, header=None)

    # Baris 0 berisi header: kolom 0-1 adalah label, kolom 2+ adalah tanggal
    header_row = df.iloc[0, 2:].tolist()

    # Baris 1 adalah data Semua Provinsi (nasional)
    price_row = df.iloc[1, 2:].tolist()

    # Parse tanggal
    dates = pd.to_datetime(header_row, dayfirst=True, errors="coerce")

    # Parse harga
    prices = [_parse_price(p) for p in price_row]

    series = pd.Series(prices, index=dates, name=commodity_name)
    series = series.dropna()
    series.index = pd.DatetimeIndex(series.index)
    series = series.sort_index()

    return series


def load_all() -> pd.DataFrame:
    """
    Memuat semua tiga komoditas dan menggabungkannya dalam satu DataFrame.

    Returns
    -------
    pd.DataFrame
        DataFrame dengan kolom untuk setiap komoditas dan index tanggal bulanan.
        Index diberi nama 'tanggal'.
    """
    def _locate_file(expected: str, commodity_name: str) -> Path:
        """Cari file sesuai `expected`; fallback mencari kecocokan di folder data."""
        expected_path = DATA_DIR / expected
        if expected_path.exists():
            return expected_path

        # Kumpulkan kandidat Excel di folder data
        candidates = [p for p in DATA_DIR.iterdir() if p.suffix.lower() in (".xlsx", ".xls")]
        if not candidates:
            raise FileNotFoundError(
                f"Tidak ada file .xlsx/.xls di folder data/.\n" \
                f"Letakkan file ekspor PIHPS di folder 'data/'."
            )

        # Normalisasi nama untuk perbandingan
        def norm(s: str) -> str:
            return re.sub(r"[^a-z0-9]", "", s.lower())

        target = norm(commodity_name)
        names = [p.name for p in candidates]

        # Coba cocokkan berdasarkan rasio kemiripan nama berkas
        ratios = [(p, difflib.SequenceMatcher(None, norm(p.stem), target).ratio()) for p in candidates]
        best, best_ratio = max(ratios, key=lambda x: x[1])
        if best_ratio > 0.25:
            return best

        # Jika belum yakin, cari kandidat yang mengandung kata kunci dari nama komoditas
        words = [w for w in re.split(r"\W+", commodity_name.lower()) if len(w) >= 3]
        for w in words:
            for p in candidates:
                if w in p.name.lower():
                    return p

        # Terakhir, pilih kandidat terdekat meskipun rendah rasio
        return best

    series_list = []

    for commodity, filename in COMMODITY_FILES.items():
        filepath = _locate_file(filename, commodity)
        if not filepath.exists():
            raise FileNotFoundError(
                f"File tidak ditemukan untuk komoditas '{commodity}'.\n"
                f"Cari file bernama seperti: {filename} di folder data/."
            )
        print(f"Menggunakan file untuk {commodity}: {filepath.name}")
        s = load_pihps_file(filepath, commodity)
        series_list.append(s)

    df = pd.concat(series_list, axis=1)
    df.index.name = "tanggal"

    return df


if __name__ == "__main__":
    df = load_all()
    print("Data berhasil dimuat.")
    print(f"Rentang: {df.index.min().strftime('%b %Y')} — {df.index.max().strftime('%b %Y')}")
    print(f"Jumlah titik data: {len(df)} bulan")
    print("\nContoh data (5 baris pertama):")
    print(df.head().to_string())

# Analisis Volatilitas Harga Pangan Strategis Indonesia 2023–2025

Repositori ini berisi kode Python untuk analisis data harga pangan yang digunakan dalam makalah Studium Generale KU4078 Institut Teknologi Bandung.

**Judul Makalah:** Dari Data ke Kebijakan: Pemanfaatan Data Harga Pangan sebagai Dasar Pengambilan Keputusan Publik di Indonesia  
**Penulis:** Fayyaz Akmal Lauda (13524076)  
**Program Studi:** Teknik Informatika, STEI — Institut Teknologi Bandung  
**Tahun:** 2026

---

## Deskripsi

Analisis ini mengkaji volatilitas harga tiga komoditas pangan strategis Indonesia, yaitu beras medium, cabai rawit merah, dan daging ayam ras, menggunakan data bulanan dari Pusat Informasi Harga Pangan Strategis Nasional (PIHPS) Bank Indonesia periode Januari 2023 hingga Desember 2025.

Metrik utama yang digunakan:
- **Koefisien Variasi (CV)** sebagai ukuran volatilitas relatif antarkomoditas
- **Statistik deskriptif** (minimum, maksimum, rata-rata, standar deviasi)
- **Identifikasi kejadian perubahan harga ekstrem** (kenaikan atau penurunan lebih dari 10 persen dalam satu bulan)
- **Analisis tren per tahun** untuk membandingkan kondisi 2023, 2024, dan 2025

---

## Sumber Data

Data diunduh secara langsung dari dashboard PIHPS Bank Indonesia:  
**https://www.bi.go.id/hargapangan/TabelHarga/PasarTradisionalKomoditas**

Pengaturan unduhan:
- Komoditas: Beras Kualitas Medium I, Cabai Rawit Merah, Daging Ayam Ras
- Tipe laporan: Laporan Bulanan
- Rentang: Januari 2023 — Desember 2025
- Provinsi: Semua (level nasional)

Letakkan file hasil unduhan di folder `data/` dengan nama:
```
data/beras_medium.xlsx
data/cabai_rawit_merah.xlsx
data/daging_ayam_ras.xlsx
```

---

## Struktur Repositori

```
├── data/                    # File Excel dari PIHPS 
├── outputs/                 # Grafik hasil analisis (.png)
├── src/
│   ├── 01_load_data.py      # Pembersihan dan normalisasi data
│   ├── 02_statistics.py     # Statistik deskriptif dan CV
│   ├── 03_extreme_events.py # Identifikasi kejadian perubahan harga ekstrem
│   └── 04_charts.py         # Pembuatan semua grafik
├── main.py                  # Jalankan seluruh analisis sekaligus
├── requirements.txt
└── README.md
```

---

## Cara Menjalankan

### 1. Install dependensi
```bash
pip install -r requirements.txt
```

### 2. Letakkan data di folder `data/`
Unduh dari PIHPS sesuai petunjuk di atas.

### 3. Jalankan analisis
```bash
python main.py
```

Grafik akan tersimpan di folder `outputs/`.

---

## Output yang Dihasilkan

| File | Keterangan |
|------|------------|
| `outputs/gambar1_tren_harga.png` | Tren harga bulanan tiga komoditas 2023–2025 |
| `outputs/gambar2_koefisien_variasi.png` | Perbandingan CV tiga komoditas |
| `outputs/gambar3_perubahan_cabai.png` | Perubahan harga bulanan cabai rawit merah |
| `outputs/gambar4_perbandingan_tahunan.png` | Perbandingan harga per tahun (min, rata-rata, maks) |

---

## Dependensi

- Python 3.9+
- pandas
- numpy
- matplotlib
- openpyxl

---

## Lisensi

Kode ini bebas digunakan untuk keperluan akademik dengan menyertakan atribusi.

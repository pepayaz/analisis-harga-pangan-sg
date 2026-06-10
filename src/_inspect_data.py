from pathlib import Path
import pandas as pd
from src.load_data import load_all


def main():
    df = load_all()
    print("DATA FRAME — ringkasan:")
    print(df.head().to_string())
    print("\nDescriptive statistics:")
    print(df.describe().to_string())

    print("\nKoefisien Variasi (CV) per komoditas (%):")
    for col in df.columns:
        s = df[col].dropna()
        cv = (s.std() / s.mean()) * 100
        print(f"- {col}: {cv:.2f}% (mean={s.mean():.0f}, std={s.std():.0f})")

    print("\nPerubahan bulanan terbesar (abs) per komoditas:")
    pct = df.pct_change() * 100
    for col in df.columns:
        series = pct[col].dropna()
        if series.empty:
            print(f"- {col}: tidak ada perubahan")
            continue
        mx = series.max()
        mn = series.min()
        print(f"- {col}: max +{mx:.1f}%, min {mn:.1f}%")


if __name__ == '__main__':
    main()

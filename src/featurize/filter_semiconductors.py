import os
import argparse
import pandas as pd

EG_MIN = 0.5
EG_MAX = 2.5
EHULL_MAX = 0.05
MAX_NELEMENTS = 4
MAX_NSITES = 60

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inp", default="data/raw/mp_candidates_raw.csv")
    ap.add_argument("--out", default="data/processed/candidates_semiconductor.csv")
    args = ap.parse_args()

    if not os.path.exists(args.inp):
        raise FileNotFoundError(f"Missing input file: {args.inp}")

    df = pd.read_csv(args.inp)
    df = df.dropna(subset=["band_gap_eV", "energy_above_hull_eV", "nelements", "nsites"]).copy()

    for col in ["band_gap_eV", "energy_above_hull_eV", "nelements", "nsites"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["band_gap_eV", "energy_above_hull_eV", "nelements", "nsites"]).copy()

    mask = (
        (df["energy_above_hull_eV"] <= EHULL_MAX) &
        (df["band_gap_eV"] >= EG_MIN) &
        (df["band_gap_eV"] <= EG_MAX) &
        (df["nelements"] <= MAX_NELEMENTS) &
        (df["nsites"] <= MAX_NSITES)
    )

    df_f = df.loc[mask].copy()
    df_f = df_f.sort_values(
        by=["energy_above_hull_eV", "band_gap_eV", "nelements", "nsites"],
        ascending=[True, True, True, True],
    ).reset_index(drop=True)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    df_f.to_csv(args.out, index=False)

    print("=== Filter Summary ===")
    print(f"Input: {args.inp}")
    print(f"Input rows: {len(df)}")
    print(f"Output rows: {len(df_f)}")
    print(f"Saved -> {args.out}")

if __name__ == "__main__":
    main()

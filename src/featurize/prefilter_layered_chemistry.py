import os
import pandas as pd

INP = "data/raw/mp_candidates_expanded_raw.csv"
OUT = "data/processed/candidates_prefilter_layered_chemistry.csv"

# Semiconductor/stability window (same idea as before)
EG_MIN = 0.5
EG_MAX = 2.5
EHULL_MAX = 0.05

# Chemistry heuristics for likely layered solids
EXCLUDE_ELEMENTS = {"O", "N"}  # dominated by 3D frameworks
LAYERED_FAVOR_ELEMENTS = {"S", "Se", "Te", "P", "As", "Sb", "Bi", "Cl", "Br", "I"}

def parse_elements(s):
    if pd.isna(s):
        return set()
    s = str(s).replace('"', '').replace(" ", "")
    return set([e for e in s.split(",") if e])

def main():
    if not os.path.exists(INP):
        raise FileNotFoundError(f"Missing {INP}")

    df = pd.read_csv(INP)

    # numeric cleanup
    for col in ["band_gap_eV", "energy_above_hull_eV", "nelements", "nsites"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["band_gap_eV", "energy_above_hull_eV", "nelements", "nsites", "elements"]).copy()

    # basic semiconductor + stability
    df = df[
        (df["band_gap_eV"] >= EG_MIN) &
        (df["band_gap_eV"] <= EG_MAX) &
        (df["energy_above_hull_eV"] <= EHULL_MAX)
    ].copy()

    keep_rows = []
    for idx, r in df.iterrows():
        els = parse_elements(r["elements"])
        if len(els & EXCLUDE_ELEMENTS) > 0:
            continue
        if len(els & LAYERED_FAVOR_ELEMENTS) == 0:
            continue
        keep_rows.append(idx)

    df2 = df.loc[keep_rows].copy().reset_index(drop=True)

    os.makedirs("data/processed", exist_ok=True)
    df2.to_csv(OUT, index=False)

    print("=== Prefilter Summary ===")
    print(f"Input (expanded): {len(pd.read_csv(INP))}")
    print(f"After Eg/Ehull:   {len(df)}")
    print(f"After chemistry:  {len(df2)}")
    print(f"Saved -> {OUT}")

if __name__ == "__main__":
    main()

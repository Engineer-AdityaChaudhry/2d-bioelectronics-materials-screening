import os
import pandas as pd
import numpy as np

INP = "data/processed/candidates_prefilter_layered_chemistry_layered_joined.csv"
OUT = "data/processed/candidates_layered_big_continuous.csv"

def main():
    if not os.path.exists(INP):
        raise FileNotFoundError(f"Missing {INP}. Run layeredness_score_cached.py first.")

    df = pd.read_csv(INP)

    # keep only layered candidates with valid counts
    df = df[df["is_layered_candidate"] == True].copy()

    for col in ["axis_bonds_a","axis_bonds_b","axis_bonds_c","band_gap_eV","energy_above_hull_eV",
                "formation_energy_per_atom_eV","density","nsites","nelements","layered_score"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["axis_bonds_a","axis_bonds_b","axis_bonds_c","band_gap_eV","energy_above_hull_eV",
                           "formation_energy_per_atom_eV","density","nsites","nelements"]).copy()

    a = df["axis_bonds_a"]; b = df["axis_bonds_b"]; c = df["axis_bonds_c"]
    tot = (a + b + c).replace(0, np.nan)
    weak = pd.concat([a,b,c], axis=1).min(axis=1)

    df["weak_axis_fraction"] = (weak / tot)
    df["layered_continuous"] = (1 - df["weak_axis_fraction"]).clip(0, 1)
    df["weak_axis"] = pd.concat([a,b,c], axis=1).idxmin(axis=1).str.replace("axis_bonds_", "", regex=False)

    os.makedirs("data/processed", exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"Saved -> {OUT}")
    print("Layered rows:", len(df))

if __name__ == "__main__":
    main()

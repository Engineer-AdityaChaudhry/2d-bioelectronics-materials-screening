import pandas as pd
import numpy as np
import os

INP = "data/processed/candidates_semiconductor_layered_v2.csv"
OUT = "data/processed/candidates_semiconductor_layered_v2_continuous.csv"

def main():
    df = pd.read_csv(INP)

    # Only compute where counts exist
    for col in ["axis_bonds_a", "axis_bonds_b", "axis_bonds_c"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    a = df["axis_bonds_a"]
    b = df["axis_bonds_b"]
    c = df["axis_bonds_c"]
    tot = a + b + c

    # Avoid division by zero
    tot_safe = tot.replace(0, np.nan)

    # Continuous "weak-axis fraction" layeredness
    weak = pd.concat([a, b, c], axis=1).min(axis=1)
    df["weak_axis_fraction"] = (weak / tot_safe).fillna(np.nan)
    df["layered_continuous"] = (1 - df["weak_axis_fraction"]).clip(0, 1)

    # Also record which axis is weak (may tie)
    df["weak_axis"] = pd.concat([a, b, c], axis=1).idxmin(axis=1).str.replace("axis_bonds_", "", regex=False)

    os.makedirs("data/processed", exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"Saved -> {OUT}")
    print("Layered candidates:", int(df["is_layered_candidate"].sum()), "Total:", len(df))

if __name__ == "__main__":
    main()

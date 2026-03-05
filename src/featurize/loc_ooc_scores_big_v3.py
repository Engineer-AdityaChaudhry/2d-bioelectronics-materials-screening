import os
import numpy as np
import pandas as pd

INP = "data/processed/top200_baseline_v3_big.csv"
OUT = "data/processed/top200_loc_ooc_scored_v3.csv"
OUT_TOP = "data/processed/top50_loc_ooc_robust_v3.csv"

IONIC_STRENGTHS = {"physio_0p15M": 0.15, "diluted_0p01M": 0.01}
DISTANCES_NM = {"2nm": 2.0, "5nm": 5.0, "10nm": 10.0}

C_EDL_uF_cm2 = 10.0
C_OX_uF_cm2 = 5.0

def debye_length_nm(I_M):
    return 0.304 / np.sqrt(I_M)

def attenuation(distance_nm, lambda_nm):
    return np.exp(-distance_nm / lambda_nm)

def gating_efficiency(C_edl, C_ox):
    return C_edl / (C_edl + C_ox)

def quantum_proxy(eg):
    return 1.0 / (1.0 + eg)

def dielectric_proxy(density):
    return 1.0 / density

def surface_proxy(nelements):
    return 1.0 / nelements

def main():
    if not os.path.exists(INP):
        raise FileNotFoundError(f"Missing {INP}. Run rank_big_baseline_v3.py first.")

    df = pd.read_csv(INP).copy()
    for col in ["band_gap_eV","density","nelements"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["band_gap_eV","density","nelements"]).copy()

    eta = gating_efficiency(C_EDL_uF_cm2, C_OX_uF_cm2)
    df["gating_efficiency_eta"] = eta
    df["quantum_proxy"] = df["band_gap_eV"].apply(quantum_proxy)
    df["dielectric_proxy"] = df["density"].apply(dielectric_proxy)
    df["surface_proxy"] = df["nelements"].apply(surface_proxy)

    score_cols = []
    for scen, I in IONIC_STRENGTHS.items():
        lam = debye_length_nm(I)
        df[f"debye_length_nm_{scen}"] = lam
        for dname, dist in DISTANCES_NM.items():
            A = attenuation(dist, lam)
            col = f"loc_ooc_score_{scen}_{dname}"
            df[col] = A * eta * df["quantum_proxy"] * df["dielectric_proxy"] * df["surface_proxy"]
            score_cols.append(col)

    # Robust score: worst-case across scenario grid (maximize the minimum)
    df["loc_ooc_score_robust_min"] = df[score_cols].min(axis=1)

    # Main scenario for comparison
    df["loc_ooc_score_main"] = df["loc_ooc_score_physio_0p15M_5nm"]

    df = df.sort_values("loc_ooc_score_robust_min", ascending=False).reset_index(drop=True)

    os.makedirs("data/processed", exist_ok=True)
    df.to_csv(OUT, index=False)

    top = df.head(50).copy()
    top.to_csv(OUT_TOP, index=False)

    print(f"Saved -> {OUT}")
    print(f"Saved top 50 robust -> {OUT_TOP}")
    print("Top 10 robust preview:")
    print(top[["material_id","formula","band_gap_eV","density","nelements","baseline_score_v3","loc_ooc_score_main","loc_ooc_score_robust_min"]].head(10))

if __name__ == "__main__":
    main()

import os
import numpy as np
import pandas as pd

INP = "data/processed/top20_baseline_v3.csv"
OUT = "data/processed/top20_loc_ooc_ranked_v3.csv"

# Scenario grid
IONIC_STRENGTHS = {
    "physio_0p15M": 0.15,
    "diluted_0p01M": 0.01,
}

DISTANCES_NM = {
    "2nm": 2.0,
    "5nm": 5.0,
    "10nm": 10.0,
}

# Electrolyte-gated coupling proxy (constant for now)
C_EDL_uF_cm2 = 10.0
C_OX_uF_cm2 = 5.0

def debye_length_nm(I_M):
    return 0.304 / np.sqrt(I_M)

def attenuation(distance_nm, lambda_nm):
    return np.exp(-distance_nm / lambda_nm)

def gating_efficiency(C_edl, C_ox):
    return C_edl / (C_edl + C_ox)

def quantum_proxy(eg):
    # bounded monotonic proxy: smaller Eg -> larger coupling proxy
    return 1.0 / (1.0 + eg)

def dielectric_proxy(density):
    # simple inverse density proxy (placeholder for dielectric screening)
    return 1.0 / density

def surface_proxy(nelements):
    return 1.0 / nelements

def main():
    if not os.path.exists(INP):
        raise FileNotFoundError(f"Missing input file: {INP}. Run rank_baseline_pareto_v3.py first.")

    df = pd.read_csv(INP).copy()

    # Ensure numeric
    for col in ["band_gap_eV", "density", "nelements"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    eta = gating_efficiency(C_EDL_uF_cm2, C_OX_uF_cm2)
    df["gating_efficiency_eta"] = eta

    df["quantum_proxy"] = df["band_gap_eV"].apply(quantum_proxy)
    df["dielectric_proxy"] = df["density"].apply(dielectric_proxy)
    df["surface_proxy"] = df["nelements"].apply(surface_proxy)

    # Compute scores for each scenario
    for scen, I in IONIC_STRENGTHS.items():
        lam = debye_length_nm(I)
        df[f"debye_length_nm_{scen}"] = lam
        for dname, dist in DISTANCES_NM.items():
            A = attenuation(dist, lam)
            col = f"loc_ooc_score_{scen}_{dname}"
            df[col] = (
                A
                * eta
                * df["quantum_proxy"]
                * df["dielectric_proxy"]
                * df["surface_proxy"]
            )

    # Choose a main scenario for ranking (physio + 5nm)
    main_col = "loc_ooc_score_physio_0p15M_5nm"
    df["loc_ooc_score_main"] = df[main_col]
    df["loc_ooc_rank_main"] = df["loc_ooc_score_main"].rank(ascending=False, method="min").astype(int)

    # Sort by main score
    df = df.sort_values("loc_ooc_score_main", ascending=False).reset_index(drop=True)

    os.makedirs("data/processed", exist_ok=True)
    df.to_csv(OUT, index=False)

    print(f"Saved -> {OUT}")
    print("Top 10 (main scenario: physio 0.15M + 5nm):")
    print(df[["material_id","formula","band_gap_eV","density","nelements","loc_ooc_score_main"]].head(10))

if __name__ == "__main__":
    main()

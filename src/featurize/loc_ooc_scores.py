import os
import numpy as np
import pandas as pd

# -----------------------------
# Project 1 - Module 5 (LoC/OoC)
# Compute electrolyte screening and electrolyte-gating proxy scores
# -----------------------------

INP = "data/processed/top20_baseline_v3.csv"
OUT = "data/processed/top20_loc_ooc_ranked.csv"

# --- Scenarios (tunable) ---
# Ionic strength (M)
IONIC_STRENGTHS = {
    "physio_0p15M": 0.15,
    "diluted_0p01M": 0.01,
}

# Effective sensing distance from channel (nm)
# ~1-2 nm: small molecule / very short linker
# ~5 nm: aptamer / small protein domain
# ~10 nm: antibody-scale
DISTANCES_NM = {
    "small_molecule_2nm": 2.0,
    "aptamer_5nm": 5.0,
    "antibody_10nm": 10.0,
}

# EDL capacitance (uF/cm^2) typical range 5-20; choose mid
C_EDL_uF_cm2 = 10.0

# Optional oxide/passivation capacitance (uF/cm^2)
# If you have a passivation oxide, C_ox can be comparable or lower.
# For direct electrolyte gating, set C_OX to a very large number or simply eta=1.
C_OX_uF_cm2 = 5.0

def debye_length_nm(I_M):
    # Approx for aqueous monovalent electrolyte at ~25C:
    # lambda_D (nm) ≈ 0.304 / sqrt(I(M))
    return 0.304 / np.sqrt(I_M)

def attenuation(distance_nm, lambda_nm):
    return float(np.exp(-distance_nm / lambda_nm))

def gating_efficiency(C_edl, C_ox):
    # eta = C_edl / (C_edl + C_ox)
    return float(C_edl / (C_edl + C_ox))

def main():
    if not os.path.exists(INP):
        raise FileNotFoundError(f"Missing input file: {INP}. Run rank_baseline_pareto_v3.py first.")

    df = pd.read_csv(INP).copy()

    # Gating efficiency proxy (same for all materials in this simple model)
    eta = gating_efficiency(C_EDL_uF_cm2, C_OX_uF_cm2)
    df["gating_efficiency_eta"] = eta

    # Compute scenario-specific LoC/OoC scores
    for scen, I in IONIC_STRENGTHS.items():
        lam = debye_length_nm(I)
        df[f"debye_length_nm_{scen}"] = lam
        for dname, dist in DISTANCES_NM.items():
            A = attenuation(dist, lam)
            # LoC/OoC feasibility proxy: attenuation * gating efficiency
            df[f"atten_{scen}_{dname}"] = A
            df[f"loc_ooc_score_{scen}_{dname}"] = A * eta

    # Choose a default "main scenario" for ranking:
    # Physio ionic strength + aptamer scale (5nm)
    main_score_col = "loc_ooc_score_physio_0p15M_aptamer_5nm"
    df["loc_ooc_score_main"] = df[main_score_col]

    # Rank shift: compare baseline score and LoC/OoC score
    # (baseline_score_v3 is already in the top20 file)
    df["loc_ooc_rank"] = df["loc_ooc_score_main"].rank(ascending=False, method="min").astype(int)

    # Sort by LoC/OoC main score
    df = df.sort_values("loc_ooc_score_main", ascending=False).reset_index(drop=True)

    os.makedirs("data/processed", exist_ok=True)
    df.to_csv(OUT, index=False)

    print(f"Saved -> {OUT}")
    print("Top 10 (LoC/OoC main scenario):")
    cols = ["material_id", "formula", "band_gap_eV", "energy_above_hull_eV", "formation_energy_per_atom_eV", "baseline_score_v3", "loc_ooc_score_main"]
    print(df[cols].head(10))

if __name__ == "__main__":
    main()

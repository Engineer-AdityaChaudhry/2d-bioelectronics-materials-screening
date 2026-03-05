import os
import pandas as pd
import numpy as np

INPUT = "data/processed/candidates_semiconductor_layered_v2_continuous.csv"
OUT_PARETO = "data/processed/pareto_front_baseline_v3.csv"
OUT_TOP = "data/processed/top20_baseline_v3.csv"

EG_TARGET = 1.5
EG_SIGMA = 0.6

def bandgap_target_score(eg):
    return float(np.exp(-0.5 * ((eg - EG_TARGET) / EG_SIGMA) ** 2))

def normalize(series, higher_is_better=True):
    s = pd.to_numeric(series, errors="coerce")
    s_min, s_max = np.nanmin(s), np.nanmax(s)
    if not np.isfinite(s_min) or not np.isfinite(s_max) or (s_max - s_min) < 1e-12:
        return pd.Series(np.ones(len(s)), index=series.index)
    x = (s - s_min) / (s_max - s_min)
    return x if higher_is_better else (1 - x)

def pareto_front(df, objectives):
    vals = df[objectives].to_numpy()
    n = vals.shape[0]
    is_p = np.ones(n, dtype=bool)
    for i in range(n):
        if not is_p[i]:
            continue
        dom = np.all(vals >= vals[i], axis=1) & np.any(vals > vals[i], axis=1)
        dom[i] = False
        if np.any(dom):
            is_p[i] = False
    return is_p

def main():
    if not os.path.exists(INPUT):
        raise FileNotFoundError(f"Missing input file: {INPUT}. Run add_layered_continuous_metrics.py first.")

    df = pd.read_csv(INPUT)

    # Keep only layered candidates with required fields
    df = df[df["is_layered_candidate"] == True].copy()
    df = df.dropna(subset=[
        "layered_continuous",
        "band_gap_eV",
        "energy_above_hull_eV",
        "formation_energy_per_atom_eV",
        "nsites",
        "nelements"
    ]).copy()
    df.reset_index(drop=True, inplace=True)

    # Scores
    df["eg_target_score"] = df["band_gap_eV"].apply(bandgap_target_score)

    # Normalize “higher is better” terms
    df["score_stability_norm"] = normalize(df["energy_above_hull_eV"], higher_is_better=False)
    df["score_eg_norm"] = normalize(df["eg_target_score"], higher_is_better=True)
    df["score_layered_norm"] = normalize(df["layered_continuous"], higher_is_better=True)

    # Formation energy: more negative is generally better (stronger bonding)
    df["score_formE_norm"] = normalize(df["formation_energy_per_atom_eV"], higher_is_better=False)

    # Complexity penalty (lower is better)
    # Simple proxy: more atoms + more elements increases difficulty
    df["complexity"] = df["nsites"] + 10 * df["nelements"]
    df["score_complexity_norm"] = normalize(df["complexity"], higher_is_better=False)

    # Weighted baseline score (integration-aware)
    w_stab, w_eg, w_layer, w_formE, w_complex = 0.30, 0.25, 0.15, 0.20, 0.10
    df["baseline_score_v3"] = (
        w_stab * df["score_stability_norm"] +
        w_eg * df["score_eg_norm"] +
        w_layer * df["score_layered_norm"] +
        w_formE * df["score_formE_norm"] +
        w_complex * df["score_complexity_norm"]
    )

    # Pareto objectives (all max-oriented)
    df["obj_stability"] = df["score_stability_norm"]
    df["obj_eg"] = df["eg_target_score"]
    df["obj_layered"] = df["layered_continuous"]
    df["obj_formE"] = df["score_formE_norm"]

    df["is_pareto"] = pareto_front(df, ["obj_stability", "obj_eg", "obj_layered", "obj_formE"])

    os.makedirs("data/processed", exist_ok=True)
    pareto_df = df[df["is_pareto"]].sort_values("baseline_score_v3", ascending=False).reset_index(drop=True)
    pareto_df.to_csv(OUT_PARETO, index=False)

    top_df = df.sort_values("baseline_score_v3", ascending=False).head(20).reset_index(drop=True)
    top_df.to_csv(OUT_TOP, index=False)

    print("=== Baseline Ranking v3 Summary ===")
    print(f"Layered candidates considered: {len(df)}")
    print(f"Pareto front size: {len(pareto_df)} -> {OUT_PARETO}")
    print(f"Top 20 saved -> {OUT_TOP}")
    print()
    print(top_df[['material_id','formula','band_gap_eV','energy_above_hull_eV','formation_energy_per_atom_eV','complexity','baseline_score_v3']].head(10))

if __name__ == "__main__":
    main()

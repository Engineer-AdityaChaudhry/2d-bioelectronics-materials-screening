import os
import pandas as pd
import numpy as np

# -----------------------------
# Project 1 - Module 3
# Baseline nanoelectronics ranking for layered 2D semiconductor candidates
# -----------------------------

INPUT = "data/processed/candidates_semiconductor_layered_v2.csv"
OUT_PARETO = "data/processed/pareto_front_baseline.csv"
OUT_TOP = "data/processed/top20_baseline.csv"

# Bandgap target for "useful semiconductor channel"
# We use a smooth preference curve (not a hard cutoff).
EG_TARGET = 1.5      # eV
EG_SIGMA = 0.6       # eV (width of preference)

def bandgap_target_score(eg):
    """
    Gaussian preference centered at EG_TARGET.
    Returns [0, 1], highest near EG_TARGET.
    """
    return float(np.exp(-0.5 * ((eg - EG_TARGET) / EG_SIGMA) ** 2))

def normalize(series, higher_is_better=True):
    s = series.astype(float)
    s_min, s_max = np.nanmin(s), np.nanmax(s)
    if s_max - s_min < 1e-12:
        return pd.Series(np.ones(len(s)), index=series.index)
    x = (s - s_min) / (s_max - s_min)
    return x if higher_is_better else (1 - x)

def pareto_front(df, objectives):
    """
    Compute a Pareto front for objectives where all are to be maximized.
    objectives: list of column names that are already oriented "higher is better".
    Returns boolean mask of non-dominated points.
    """
    vals = df[objectives].to_numpy()
    n = vals.shape[0]
    is_pareto = np.ones(n, dtype=bool)

    for i in range(n):
        if not is_pareto[i]:
            continue
        # A point j dominates i if it is >= in all objectives and > in at least one
        dominates = np.all(vals >= vals[i], axis=1) & np.any(vals > vals[i], axis=1)
        # Exclude self
        dominates[i] = False
        if np.any(dominates):
            is_pareto[i] = False

    return is_pareto

def main():
    if not os.path.exists(INPUT):
        raise FileNotFoundError(f"Missing input file: {INPUT}. Run layeredness_score_v2.py first.")

    df = pd.read_csv(INPUT)

    # Keep only layered candidates with valid scores
    df = df[df["is_layered_candidate"] == True].copy()
    df = df.dropna(subset=["layered_score", "band_gap_eV", "energy_above_hull_eV"]).copy()
    df.reset_index(drop=True, inplace=True)

    # Compute bandgap preference score
    df["eg_target_score"] = df["band_gap_eV"].apply(bandgap_target_score)

    # Normalize metrics for combined score (all "higher is better")
    df["score_layered_norm"] = normalize(df["layered_score"], higher_is_better=True)
    df["score_stability_norm"] = normalize(df["energy_above_hull_eV"], higher_is_better=False)  # lower ehull is better
    df["score_eg_norm"] = normalize(df["eg_target_score"], higher_is_better=True)

    # Explainable weighted score (baseline)
    # Stability matters a lot, then bandgap preference, then layeredness.
    w_stab, w_eg, w_layer = 0.45, 0.35, 0.20
    df["baseline_score"] = (
        w_stab * df["score_stability_norm"]
        + w_eg * df["score_eg_norm"]
        + w_layer * df["score_layered_norm"]
    )

    # Pareto objectives (all max-oriented):
    # - maximize stability_norm (i.e., low ehull)
    # - maximize eg_target_score
    # - maximize layered_score
    df["obj_stability"] = df["score_stability_norm"]
    df["obj_eg"] = df["eg_target_score"]
    df["obj_layered"] = df["layered_score"]

    pareto_mask = pareto_front(df, ["obj_stability", "obj_eg", "obj_layered"])
    df["is_pareto"] = pareto_mask

    os.makedirs("data/processed", exist_ok=True)

    pareto_df = df[df["is_pareto"]].sort_values("baseline_score", ascending=False).reset_index(drop=True)
    pareto_df.to_csv(OUT_PARETO, index=False)

    top_df = df.sort_values("baseline_score", ascending=False).head(20).reset_index(drop=True)
    top_df.to_csv(OUT_TOP, index=False)

    print("=== Baseline Ranking Summary ===")
    print(f"Layered candidates considered: {len(df)}")
    print(f"Pareto front size: {len(pareto_df)} -> {OUT_PARETO}")
    print(f"Top 20 saved -> {OUT_TOP}")
    print()
    print("Top 10 preview:")
    print(top_df[["material_id", "formula", "band_gap_eV", "energy_above_hull_eV", "layered_score", "baseline_score"]].head(10))

if __name__ == "__main__":
    main()

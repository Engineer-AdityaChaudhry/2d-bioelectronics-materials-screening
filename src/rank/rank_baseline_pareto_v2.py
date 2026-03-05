import os
import pandas as pd
import numpy as np

INPUT = "data/processed/candidates_semiconductor_layered_v2_continuous.csv"
OUT_PARETO = "data/processed/pareto_front_baseline_v2.csv"
OUT_TOP = "data/processed/top20_baseline_v2.csv"

EG_TARGET = 1.5
EG_SIGMA = 0.6

def bandgap_target_score(eg):
    return float(np.exp(-0.5 * ((eg - EG_TARGET) / EG_SIGMA) ** 2))

def normalize(series, higher_is_better=True):
    s = series.astype(float)
    s_min, s_max = np.nanmin(s), np.nanmax(s)
    if s_max - s_min < 1e-12:
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

    # Keep only layered candidates
    df = df[df["is_layered_candidate"] == True].copy()
    df = df.dropna(subset=["layered_continuous", "band_gap_eV", "energy_above_hull_eV"]).copy()
    df.reset_index(drop=True, inplace=True)

    df["eg_target_score"] = df["band_gap_eV"].apply(bandgap_target_score)

    # Normalized terms
    df["score_stability_norm"] = normalize(df["energy_above_hull_eV"], higher_is_better=False)
    df["score_eg_norm"] = normalize(df["eg_target_score"], higher_is_better=True)
    df["score_layered_norm"] = normalize(df["layered_continuous"], higher_is_better=True)

    # Weighted score (baseline)
    w_stab, w_eg, w_layer = 0.45, 0.35, 0.20
    df["baseline_score_v2"] = (
        w_stab * df["score_stability_norm"] +
        w_eg * df["score_eg_norm"] +
        w_layer * df["score_layered_norm"]
    )

    # Pareto objectives (max-oriented)
    df["obj_stability"] = df["score_stability_norm"]
    df["obj_eg"] = df["eg_target_score"]
    df["obj_layered"] = df["layered_continuous"]

    df["is_pareto"] = pareto_front(df, ["obj_stability", "obj_eg", "obj_layered"])

    os.makedirs("data/processed", exist_ok=True)
    pareto_df = df[df["is_pareto"]].sort_values("baseline_score_v2", ascending=False).reset_index(drop=True)
    pareto_df.to_csv(OUT_PARETO, index=False)

    top_df = df.sort_values("baseline_score_v2", ascending=False).head(20).reset_index(drop=True)
    top_df.to_csv(OUT_TOP, index=False)

    print("=== Baseline Ranking v2 Summary ===")
    print(f"Layered candidates considered: {len(df)}")
    print(f"Pareto front size: {len(pareto_df)} -> {OUT_PARETO}")
    print(f"Top 20 saved -> {OUT_TOP}")
    print()
    print(top_df[['material_id','formula','band_gap_eV','energy_above_hull_eV','layered_continuous','baseline_score_v2']].head(10))

if __name__ == "__main__":
    main()

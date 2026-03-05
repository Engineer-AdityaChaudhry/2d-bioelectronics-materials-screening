import os
import pandas as pd
import numpy as np

INP = "data/processed/candidates_layered_big_continuous.csv"
OUT_ALL = "data/processed/ranked_layered_big_baseline_v3.csv"
OUT_TOPK = "data/processed/top200_baseline_v3_big.csv"

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

def main():
    if not os.path.exists(INP):
        raise FileNotFoundError(f"Missing {INP}. Run add_layered_continuous_metrics_big.py first.")

    df = pd.read_csv(INP).copy()

    # bandgap preference
    df["eg_target_score"] = df["band_gap_eV"].apply(bandgap_target_score)

    # normalized terms
    df["score_stability_norm"] = normalize(df["energy_above_hull_eV"], higher_is_better=False)
    df["score_eg_norm"] = normalize(df["eg_target_score"], higher_is_better=True)
    df["score_layered_norm"] = normalize(df["layered_continuous"], higher_is_better=True)
    df["score_formE_norm"] = normalize(df["formation_energy_per_atom_eV"], higher_is_better=False)

    # complexity
    df["complexity"] = df["nsites"] + 10 * df["nelements"]
    df["score_complexity_norm"] = normalize(df["complexity"], higher_is_better=False)

    # weights (same as your v3)
    w_stab, w_eg, w_layer, w_formE, w_complex = 0.30, 0.25, 0.15, 0.20, 0.10
    df["baseline_score_v3"] = (
        w_stab * df["score_stability_norm"] +
        w_eg * df["score_eg_norm"] +
        w_layer * df["score_layered_norm"] +
        w_formE * df["score_formE_norm"] +
        w_complex * df["score_complexity_norm"]
    )

    df = df.sort_values("baseline_score_v3", ascending=False).reset_index(drop=True)

    os.makedirs("data/processed", exist_ok=True)
    df.to_csv(OUT_ALL, index=False)

    topk = df.head(200).copy()
    topk.to_csv(OUT_TOPK, index=False)

    print(f"Saved ranked set -> {OUT_ALL}")
    print(f"Saved top 200 -> {OUT_TOPK}")
    print("Top 10 preview:")
    print(topk[["material_id","formula","band_gap_eV","energy_above_hull_eV","layered_continuous","baseline_score_v3"]].head(10))

if __name__ == "__main__":
    main()

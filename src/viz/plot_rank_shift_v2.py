import os
import pandas as pd
import matplotlib.pyplot as plt

BASE_ALL = "data/processed/ranked_layered_big_baseline_v3.csv"
LOC      = "data/processed/top50_loc_ooc_robust_v3.csv"
OUT      = "figures/rank_shift_baseline_to_loc_ooc_v2.png"

def main():
    if not os.path.exists(BASE_ALL):
        raise FileNotFoundError(f"Missing {BASE_ALL} (run: make rank)")
    if not os.path.exists(LOC):
        raise FileNotFoundError(f"Missing {LOC} (run: make loc)")

    df_base = pd.read_csv(BASE_ALL).copy()
    df_loc = pd.read_csv(LOC).copy()

    # We expect these columns
    if "baseline_score_v3" not in df_base.columns:
        raise RuntimeError("baseline_score_v3 missing from ranked_layered_big_baseline_v3.csv")
    if "loc_ooc_score_robust_min" not in df_loc.columns:
        raise RuntimeError("loc_ooc_score_robust_min missing from top50_loc_ooc_robust_v3.csv")

    df = df_loc.merge(
        df_base[["material_id","formula","baseline_score_v3"]],
        on="material_id",
        how="left",
        suffixes=("", "_base")
    )

    df["formula_plot"] = df["formula"].fillna(df.get("formula_base"))

    os.makedirs("figures", exist_ok=True)

    plt.figure()
    plt.scatter(df["baseline_score_v3"], df["loc_ooc_score_robust_min"], s=60)

    for _, r in df.iterrows():
        if pd.notna(r["baseline_score_v3"]) and pd.notna(r["loc_ooc_score_robust_min"]):
            plt.text(r["baseline_score_v3"] + 0.0005, r["loc_ooc_score_robust_min"], str(r["formula_plot"]), fontsize=8)

    plt.title("Baseline vs LoC/OoC ranking (robust score)")
    plt.xlabel("Baseline score (nanoelectronics + stability + complexity)")
    plt.ylabel("LoC/OoC robust score (min across scenarios)")
    plt.tight_layout()
    plt.savefig(OUT, dpi=200)
    print(f"Saved -> {OUT}")

if __name__ == "__main__":
    main()

import os
import pandas as pd
import matplotlib.pyplot as plt

BASE = "data/processed/top200_baseline_v3_big.csv"
LOC  = "data/processed/top50_loc_ooc_robust_v3.csv"
OUT  = "figures/rank_shift_baseline_to_loc_ooc.png"

def main():
    if not os.path.exists(BASE):
        raise FileNotFoundError(f"Missing {BASE} (run: make rank)")
    if not os.path.exists(LOC):
        raise FileNotFoundError(f"Missing {LOC} (run: make loc)")

    df_base = pd.read_csv(BASE).copy()
    df_loc = pd.read_csv(LOC).copy()

    # Assign baseline rank (1..N)
    df_base = df_base.reset_index(drop=True)
    df_base["baseline_rank"] = df_base.index + 1

    # Assign LoC/OoC rank (1..N)
    df_loc = df_loc.reset_index(drop=True)
    df_loc["loc_rank"] = df_loc.index + 1

    # Join on material_id (most stable key)
    df = df_loc.merge(df_base[["material_id","baseline_rank","formula"]], on="material_id", how="left")

    # If formula missing on right, use left formula
    if "formula_x" in df.columns:
        df["formula_plot"] = df["formula_x"].fillna(df.get("formula_y"))
    else:
        df["formula_plot"] = df.get("formula", "")

    os.makedirs("figures", exist_ok=True)

    plt.figure()
    plt.scatter(df["baseline_rank"], df["loc_rank"], s=60)

    # annotate compactly
    for _, r in df.iterrows():
        if pd.notna(r["baseline_rank"]):
            plt.text(r["baseline_rank"] + 0.1, r["loc_rank"], str(r["formula_plot"]), fontsize=8)

    plt.title("Rank shift: baseline → LoC/OoC (Top50 robust)")
    plt.xlabel("Baseline rank (Top200 baseline)")
    plt.ylabel("LoC/OoC rank (Top50 robust)")
    plt.tight_layout()
    plt.savefig(OUT, dpi=200)
    print(f"Saved -> {OUT}")

if __name__ == "__main__":
    main()

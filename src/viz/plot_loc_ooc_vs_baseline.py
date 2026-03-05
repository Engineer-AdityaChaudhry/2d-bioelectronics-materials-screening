import os
import pandas as pd
import matplotlib.pyplot as plt

INP = "data/processed/top20_loc_ooc_ranked_v3_stacks.csv"
OUT = "figures/loc_ooc_vs_baseline.png"

def main():
    df = pd.read_csv(INP)

    os.makedirs("figures", exist_ok=True)

    plt.figure()
    plt.scatter(df["baseline_score_v3"], df["loc_ooc_score_main"])
    for _, r in df.iterrows():
        label = f"{r['formula']} ({r['integration_risk_level']})"
        plt.text(r["baseline_score_v3"] + 0.002, r["loc_ooc_score_main"], label, fontsize=7)

    plt.xlabel("Baseline score (nanoelectronics + stability + complexity)")
    plt.ylabel("LoC/OoC score (physio 0.15M + 5nm)")
    plt.title("Baseline vs LoC/OoC ranking with integration risk tags")
    plt.savefig(OUT, dpi=200, bbox_inches="tight")
    print(f"Saved -> {OUT}")

if __name__ == "__main__":
    main()

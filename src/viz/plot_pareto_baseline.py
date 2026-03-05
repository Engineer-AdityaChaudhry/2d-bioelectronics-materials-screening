import os
import pandas as pd
import matplotlib.pyplot as plt

ALL = "data/processed/ranked_layered_big_baseline_v3.csv"
TOP = "data/processed/top200_baseline_v3_big.csv"
OUT = "figures/pareto_baseline.png"

def main():
    if not os.path.exists(ALL):
        raise FileNotFoundError(f"Missing {ALL} (run: make rank)")
    if not os.path.exists(TOP):
        raise FileNotFoundError(f"Missing {TOP} (run: make rank)")

    df_all = pd.read_csv(ALL)
    df_top = pd.read_csv(TOP)

    os.makedirs("figures", exist_ok=True)

    plt.figure()
    plt.scatter(df_all["band_gap_eV"], df_all["energy_above_hull_eV"], s=12)
    plt.scatter(df_top["band_gap_eV"], df_top["energy_above_hull_eV"], s=40)

    plt.title("Layered semiconductors (BIG): baseline screening (top200 highlighted)")
    plt.xlabel("Band gap (eV)")
    plt.ylabel("Energy above hull (eV)")
    plt.tight_layout()
    plt.savefig(OUT, dpi=200)
    print(f"Saved -> {OUT}")

if __name__ == "__main__":
    main()

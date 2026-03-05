import os
import pandas as pd
import matplotlib.pyplot as plt

INPUT = "data/processed/top50_loc_ooc_robust_v3.csv"

OUT_CSV = "data/processed/project1_selected_materials.csv"
OUT_MD = "reports/project1_selected_materials.md"
OUT_PLOT = "figures/project1_selected_materials.png"


def main():

    if not os.path.exists(INPUT):
        raise FileNotFoundError(
            "Missing top50_loc_ooc_robust_v3.csv. Run full pipeline first."
        )

    df = pd.read_csv(INPUT).copy()

    # Select columns relevant for the report
    cols = [
        "material_id",
        "formula",
        "band_gap_eV",
        "density",
        "nelements",
        "baseline_score_v3",
        "loc_ooc_score_robust_min",
    ]

    cols = [c for c in cols if c in df.columns]

    df_sel = df[cols].copy()

    # Save clean dataset
    os.makedirs("data/processed", exist_ok=True)
    df_sel.to_csv(OUT_CSV, index=False)

    # Print Top 10
    print("\n=== Project 1: Selected Materials (Top 10) ===\n")
    print(df_sel.head(10).to_string(index=False))

    # Save Markdown table for the report
    os.makedirs("reports", exist_ok=True)

    with open(OUT_MD, "w") as f:

        f.write("# Project 1 — Selected 2D Materials for Bioelectronics\n\n")
        f.write(
            "Top materials identified by the screening framework for "
            "bio-integrated semiconductor platforms.\n\n"
        )

        f.write(df_sel.head(20).to_markdown(index=False))

    # Plot ranking score
    os.makedirs("figures", exist_ok=True)

    plt.figure()

    plt.barh(
        df_sel.head(15)["formula"],
        df_sel.head(15)["loc_ooc_score_robust_min"],
    )

    plt.xlabel("LoC/OoC Robustness Score")
    plt.title("Top Candidate 2D Materials for Bio-Integrated Electronics")

    plt.tight_layout()

    plt.savefig(OUT_PLOT, dpi=200)

    print("\nSaved outputs:")
    print("  CSV:", OUT_CSV)
    print("  Report:", OUT_MD)
    print("  Plot:", OUT_PLOT)


if __name__ == "__main__":
    main()
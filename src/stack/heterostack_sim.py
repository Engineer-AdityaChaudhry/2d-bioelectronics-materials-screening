import os
import numpy as np
import pandas as pd

INP_TOP = "data/processed/top50_loc_ooc_robust_v3.csv"
INP_EXT = "data/external/2dmatpedia_props.csv"
OUT_CSV = "data/processed/heterostacks_top50.csv"
OUT_MD  = "reports/heterostacks_top50.md"

# Contact work functions (eV) - editable placeholders for Tier-1
CONTACTS = {
    "graphene": 4.6,
    "Au": 5.1,
    "Ti": 4.3,
}

# Simple dielectric stack options (no band edges needed just to generate stack cards)
DIELECTRICS = [
    "hBN",
    "Al2O3",
    "HfO2",
]

def contact_classification(work_fn_eV, vbm_eV, cbm_eV):
    """
    Tier-1: Schottky-Mott style proximity test using vacuum-referenced band edges.
    Convention: VBM/CBM often negative vs vacuum; work function corresponds to Ef ~ -WF.
    We classify by which band edge is closer to Ef.
    """
    if pd.isna(vbm_eV) or pd.isna(cbm_eV) or pd.isna(work_fn_eV):
        return "unknown (missing band edges)"

    Ef = -float(work_fn_eV)
    dv = abs(Ef - float(vbm_eV))
    dc = abs(Ef - float(cbm_eV))

    if dc < dv:
        return "n-type favorable (Ef closer to CBM)"
    else:
        return "p-type favorable (Ef closer to VBM)"

def main():
    if not os.path.exists(INP_TOP):
        raise FileNotFoundError(f"Missing {INP_TOP}. Run loc_ooc_scores_big_v3.py first.")
    if not os.path.exists(INP_EXT):
        raise FileNotFoundError(
            f"Missing {INP_EXT}. Create it with src/external/parse_2dmatpedia.py"
        )

    top = pd.read_csv(INP_TOP).copy()
    ext = pd.read_csv(INP_EXT).copy()

    # Merge by formula (Tier-1). We'll improve matching later if needed.
    df = top.merge(ext, on="formula", how="left", suffixes=("", "_ext"))

    rows = []
    for _, r in df.iterrows():
        mid = r["material_id"]
        formula = r["formula"]
        vbm = r.get("vbm_eV", np.nan)
        cbm = r.get("cbm_eV", np.nan)

        # Contact evaluation rows
        for cname, wf in CONTACTS.items():
            rows.append({
                "material_id": mid,
                "formula": formula,
                "partner": cname,
                "partner_type": "contact",
                "partner_work_function_eV": wf,
                "vbm_eV": vbm,
                "cbm_eV": cbm,
                "contact_class": contact_classification(wf, vbm, cbm),
                "loc_ooc_score_robust_min": r.get("loc_ooc_score_robust_min", None),
                "baseline_score_v3": r.get("baseline_score_v3", None),
            })

        # Dielectric options (stack templates)
        for dname in DIELECTRICS:
            rows.append({
                "material_id": mid,
                "formula": formula,
                "partner": dname,
                "partner_type": "dielectric",
                "partner_work_function_eV": None,
                "vbm_eV": vbm,
                "cbm_eV": cbm,
                "contact_class": None,
                "loc_ooc_score_robust_min": r.get("loc_ooc_score_robust_min", None),
                "baseline_score_v3": r.get("baseline_score_v3", None),
            })

    out = pd.DataFrame(rows)

    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    out.to_csv(OUT_CSV, index=False)

    # Markdown report (compact)
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("# Module 10 — Heterostructure Stack Simulation (Tier-1)\n\n")
        f.write("This report evaluates contact tendency (graphene/Au/Ti) when vacuum band edges are available.\n")
        f.write("Dielectrics are listed as stack options.\n\n")
        f.write("## Coverage\n\n")
        coverage = out["contact_class"].notna().mean()
        f.write(f"- Rows: {len(out)}\n")
        f.write(f"- Band-edge based contact classification available for some rows.\n\n")
        f.write("## Sample rows\n\n")
        f.write(out.head(40).to_markdown(index=False))
        f.write("\n")

    print(f"Saved -> {OUT_CSV}")
    print(f"Saved -> {OUT_MD}")
    print(out.head(12))

if __name__ == "__main__":
    main()

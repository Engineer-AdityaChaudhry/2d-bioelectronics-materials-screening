import os
import pandas as pd
import numpy as np

INP_TOP = "data/processed/top50_loc_ooc_robust_v3.csv"
INP_EXT = "data/external/2dmatpedia_props.csv"
OUT_CSV = "data/processed/top50_multiphysics_tags.csv"
OUT_MD  = "reports/top50_multiphysics_summary.md"

# -------------------------
# Tier-1 thresholds (tune later)
# -------------------------
EG_PHOTONICS_MIN = 0.8
EG_PHOTONICS_MAX = 2.2
MAGMOM_THR = 0.5     # "magnetic candidate" if >= this
PIEZO_THR = 0.1      # "piezo/MEMS candidate" if >= this

# -------------------------
# Helpers for better matching
# -------------------------
def normalize_formula(s: str) -> str:
    """Basic cleanup for formula strings."""
    if s is None or (isinstance(s, float) and np.isnan(s)):
        return ""
    return str(s).strip().replace(" ", "")

def element_set_key_from_elements_col(elements_str: str) -> str:
    """
    elements column in your MP CSV is like: "K,Mo,S" (sometimes quoted)
    Return stable key: "K-Mo-S"
    """
    if elements_str is None or (isinstance(elements_str, float) and np.isnan(elements_str)):
        return ""
    s = str(elements_str).replace('"', '').replace(" ", "")
    parts = [p for p in s.split(",") if p]
    parts = sorted(set(parts))
    return "-".join(parts)

def reduced_formula_key(formula: str) -> str:
    """
    Use pymatgen to compute reduced formula if available.
    Fall back to normalized formula.
    """
    f = normalize_formula(formula)
    if not f:
        return ""
    try:
        from pymatgen.core import Composition
        return Composition(f).reduced_formula
    except Exception:
        # fallback: not truly reduced, but better than failing
        return f

def tristate_ge(x, thr: float) -> str:
    """Return 'yes' / 'no' / 'unknown' for threshold comparisons."""
    if pd.isna(x):
        return "unknown"
    try:
        return "yes" if float(x) >= thr else "no"
    except Exception:
        return "unknown"

def safe_numeric(df, cols):
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

# -------------------------
# Main
# -------------------------
def main():
    if not os.path.exists(INP_TOP):
        raise FileNotFoundError(f"Missing {INP_TOP}")
    if not os.path.exists(INP_EXT):
        raise FileNotFoundError(f"Missing {INP_EXT}. Create it with src/external/parse_2dmatpedia.py")

    top = pd.read_csv(INP_TOP).copy()
    ext = pd.read_csv(INP_EXT).copy()

    # Normalize formulas
    top["formula_norm"] = top["formula"].apply(normalize_formula)
    ext["formula_norm"] = ext["formula"].apply(normalize_formula)

    # Add reduced formula keys (better matching)
    top["formula_reduced"] = top["formula_norm"].apply(reduced_formula_key)
    ext["formula_reduced"] = ext["formula_norm"].apply(reduced_formula_key)

    # Add element-set keys if available
    # (Top50 from MP usually has "elements" column; ext may not.)
    if "elements" in top.columns:
        top["element_set_key"] = top["elements"].apply(element_set_key_from_elements_col)
    else:
        top["element_set_key"] = ""

    # If ext doesn't have an elements column, we can compute element set key from formula using pymatgen if available
    if "elements" in ext.columns:
        ext["element_set_key"] = ext["elements"].apply(element_set_key_from_elements_col)
    else:
        def elem_key_from_formula(formula):
            f = normalize_formula(formula)
            if not f:
                return ""
            try:
                from pymatgen.core import Composition
                els = sorted([el.symbol for el in Composition(f).elements])
                return "-".join(els)
            except Exception:
                return ""
        ext["element_set_key"] = ext["formula_norm"].apply(elem_key_from_formula)

    # Numeric coercion for external props
    ext = safe_numeric(ext, ["band_gap_eV_ext", "vbm_eV", "cbm_eV", "work_function_eV",
                            "magmom", "piezo_proxy", "dielectric_proxy", "elastic_proxy"])

    # -------------------------
    # Merge strategy (most to least reliable):
    # 1) reduced_formula + element_set_key
    # 2) reduced_formula
    # 3) raw normalized formula
    # -------------------------
    # (1)
    df = top.merge(
        ext,
        on=["formula_reduced", "element_set_key"],
        how="left",
        suffixes=("", "_ext"),
        indicator=True
    )

    # Rows not matched in (1)
    unmatched = df[df["_merge"] == "left_only"].copy()
    matched = df[df["_merge"] != "left_only"].copy()
    unmatched = unmatched.drop(columns=[c for c in unmatched.columns if c.endswith("_ext")] + ["_merge"], errors="ignore")

    # (2) reduced formula only
    df2 = unmatched.merge(
        ext.drop_duplicates(subset=["formula_reduced"]),
        on=["formula_reduced"],
        how="left",
        suffixes=("", "_ext2"),
        indicator=True
    )
    # Keep original columns + bring in ext columns where missing
    # We’ll harmonize by preferring columns from merge 1, else from merge 2
    def coalesce(col):
        a = df2.get(col)
        b = df2.get(col + "_ext2")
        if a is None and b is None:
            return None
        if a is None:
            return b
        if b is None:
            return a
        return a.where(a.notna(), b)

    # Coalesce key external columns
    for col in ["band_gap_eV_ext", "vbm_eV", "cbm_eV", "work_function_eV",
                "magmom", "piezo_proxy", "dielectric_proxy", "elastic_proxy", "ext_id", "ext_source", "formula"]:
        if col in df2.columns or (col + "_ext2") in df2.columns:
            base = df2[col] if col in df2.columns else pd.Series([np.nan]*len(df2))
            alt  = df2[col + "_ext2"] if (col + "_ext2") in df2.columns else pd.Series([np.nan]*len(df2))
            df2[col] = base.where(base.notna(), alt)

    df2 = df2.drop(columns=[c for c in df2.columns if c.endswith("_ext2")] + ["_merge"], errors="ignore")

    # Combine back matched + df2
    df = pd.concat([matched.drop(columns=["_merge"], errors="ignore"), df2], ignore_index=True)

    # -------------------------
    # Use MP bandgap if available; fallback to external
    # -------------------------
    df = safe_numeric(df, ["band_gap_eV", "loc_ooc_score_robust_min"])
    df["eg_used"] = df["band_gap_eV"]
    df.loc[df["eg_used"].isna(), "eg_used"] = df.get("band_gap_eV_ext", np.nan)

    # -------------------------
    # Tags: photonics boolean, magnetic/piezo tri-state
    # -------------------------
    df["tag_photonics"] = df["eg_used"].between(EG_PHOTONICS_MIN, EG_PHOTONICS_MAX, inclusive="both")

    df["tag_magnetic"] = df["magmom"].apply(lambda x: tristate_ge(x, MAGMOM_THR)) if "magmom" in df.columns else "unknown"
    df["tag_piezo_MEMS"] = df["piezo_proxy"].apply(lambda x: tristate_ge(x, PIEZO_THR)) if "piezo_proxy" in df.columns else "unknown"

    # Bio robustness (top quartile inside Top50)
    thr = df["loc_ooc_score_robust_min"].quantile(0.75)
    df["tag_bio_robust"] = df["loc_ooc_score_robust_min"] >= thr

    # Coverage metrics (how many have actual values)
    df["has_magmom"] = df["magmom"].notna() if "magmom" in df.columns else False
    df["has_piezo"] = df["piezo_proxy"].notna() if "piezo_proxy" in df.columns else False

    def pack_tags(r):
        tags = []
        if r["tag_bio_robust"]:
            tags.append("bio-robust")
        if r["tag_photonics"]:
            tags.append("photonics")

        # magnetic tri-state
        if r["tag_magnetic"] == "yes":
            tags.append("magnetic")
        elif r["tag_magnetic"] == "unknown":
            tags.append("magnetic:unknown")

        # piezo tri-state
        if r["tag_piezo_MEMS"] == "yes":
            tags.append("piezo/MEMS")
        elif r["tag_piezo_MEMS"] == "unknown":
            tags.append("piezo/MEMS:unknown")

        if not tags:
            tags.append("baseline-only")
        return ",".join(tags)

    df["multiphysics_tags"] = df.apply(pack_tags, axis=1)

    # Save outputs
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    df.to_csv(OUT_CSV, index=False)

    # Markdown report with coverage summary
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("# Module 11 — Multi-physics Classification (Top50 robust LoC/OoC)\n\n")
        f.write("Magnetics and piezo tags are tri-state: yes/no/unknown (unknown means missing external data).\n\n")
        f.write("## Coverage\n\n")
        f.write(f"- magmom available: {int(df['has_magmom'].sum())} / {len(df)}\n")
        f.write(f"- piezo available: {int(df['has_piezo'].sum())} / {len(df)}\n\n")
        f.write("## Tag definitions\n")
        f.write(f"- photonics: {EG_PHOTONICS_MIN} ≤ Eg ≤ {EG_PHOTONICS_MAX}\n")
        f.write(f"- magnetic: magmom ≥ {MAGMOM_THR} (else no; NaN → unknown)\n")
        f.write(f"- piezo/MEMS: piezo_proxy ≥ {PIEZO_THR} (else no; NaN → unknown)\n")
        f.write(f"- bio-robust: robust_min in top quartile of Top50\n\n")

        show_cols = [
            "material_id", "formula", "eg_used", "magmom", "piezo_proxy",
            "loc_ooc_score_robust_min", "multiphysics_tags"
        ]
        existing = [c for c in show_cols if c in df.columns]
        f.write(df[existing].to_markdown(index=False))
        f.write("\n")

    print(f"Saved -> {OUT_CSV}")
    print(f"Saved -> {OUT_MD}")
    print("=== External property coverage ===")
    print("magmom available:", int(df["has_magmom"].sum()), "/", len(df))
    print("piezo available:", int(df["has_piezo"].sum()), "/", len(df))
    print(df[["formula", "multiphysics_tags"]].head(15))


if __name__ == "__main__":
    main()
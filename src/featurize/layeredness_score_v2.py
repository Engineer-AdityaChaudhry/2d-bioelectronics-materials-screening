import os
import pandas as pd
from tqdm import tqdm

from mp_api.client import MPRester
from pymatgen.analysis.local_env import CrystalNN
from pymatgen.core.structure import Structure

AXES = ["a", "b", "c"]

# Threshold for considering a bond crosses an axis in fractional coordinates
# 0.35–0.45 are typical; higher = stricter.
FRAC_THRESHOLD = 0.40

# Safety thresholds to avoid "all-zero bonds => layered" artifacts
MIN_TOTAL_BONDS = 20          # minimum total neighbor edges counted across all sites
MIN_INPLANE_BONDS = 10        # require some bonding in a and b
LAYERED_SCORE_THRESHOLD = 0.60

def wrapped_frac_delta(fi, fj):
    df = fj - fi
    return df - df.round()

def axis_bond_counts(struct: Structure, cnn: CrystalNN, frac_threshold: float = FRAC_THRESHOLD):
    """
    Count axis-crossing bonds + total bonds.
    We count a bond when |Δf_axis| > threshold.
    Returns counts dict + total_bonds.
    """
    counts = {ax: 0 for ax in AXES}
    total_bonds = 0

    for i in range(len(struct)):
        try:
            neighs = cnn.get_nn_info(struct, i)
        except Exception:
            continue

        fi = struct[i].frac_coords
        for n in neighs:
            j = n["site_index"]
            fj = struct[j].frac_coords
            df = wrapped_frac_delta(fi, fj)

            total_bonds += 1

            if abs(df[0]) > frac_threshold:
                counts["a"] += 1
            if abs(df[1]) > frac_threshold:
                counts["b"] += 1
            if abs(df[2]) > frac_threshold:
                counts["c"] += 1

    return counts, total_bonds

def layered_metrics(counts, total_bonds):
    """
    Compute layeredness metrics with safety guards.
    """
    a, b, c = counts["a"], counts["b"], counts["c"]
    vals = [a, b, c]
    vmax = max(vals)
    vmin = min(vals)

    # If bonding info is too weak or missing, mark invalid
    if total_bonds < MIN_TOTAL_BONDS:
        return None, None, None, "too_few_total_bonds"
    if (a + b) < MIN_INPLANE_BONDS:
        return None, None, None, "too_few_inplane_bonds"
    if vmax == 0:
        return None, None, None, "no_axis_crossing_bonds"

    anis = vmin / vmax
    score = 1.0 - anis
    layer_axis = AXES[vals.index(vmin)]
    return score, anis, layer_axis, None

def main():
    api_key = os.environ.get("MP_API_KEY")
    if not api_key:
        raise RuntimeError("MP_API_KEY not found. Export it first.")

    inp = "data/processed/candidates_semiconductor.csv"
    if not os.path.exists(inp):
        raise FileNotFoundError(f"Missing input file: {inp}. Run filter_semiconductors.py first.")

    df = pd.read_csv(inp)
    cnn = CrystalNN()

    results = []
    with MPRester(api_key) as mpr:
        for mid in tqdm(df["material_id"].tolist(), desc="Layeredness v2"):
            try:
                struct = mpr.get_structure_by_material_id(mid)
                if struct is None:
                    raise ValueError("No structure returned")

                counts, total_bonds = axis_bond_counts(struct, cnn)
                score, anis, axis, reason = layered_metrics(counts, total_bonds)

                results.append({
                    "material_id": mid,
                    "layered_score": score,
                    "anisotropy_ratio": anis,
                    "layer_axis": axis,
                    "axis_bonds_a": counts["a"],
                    "axis_bonds_b": counts["b"],
                    "axis_bonds_c": counts["c"],
                    "total_bonds": total_bonds,
                    "layered_invalid_reason": reason
                })

            except Exception as e:
                results.append({
                    "material_id": mid,
                    "layered_score": None,
                    "anisotropy_ratio": None,
                    "layer_axis": None,
                    "axis_bonds_a": None,
                    "axis_bonds_b": None,
                    "axis_bonds_c": None,
                    "total_bonds": None,
                    "layered_invalid_reason": f"error:{str(e)[:160]}"
                })

    df_res = pd.DataFrame(results)
    df_out = df.merge(df_res, on="material_id", how="left")

    df_out["is_layered_candidate"] = df_out["layered_score"].fillna(-1) >= LAYERED_SCORE_THRESHOLD

    # Sort layered candidates first
    df_out = df_out.sort_values(
        by=["is_layered_candidate", "layered_score", "energy_above_hull_eV", "band_gap_eV"],
        ascending=[False, False, True, True],
    ).reset_index(drop=True)

    os.makedirs("data/processed", exist_ok=True)
    out = "data/processed/candidates_semiconductor_layered_v2.csv"
    df_out.to_csv(out, index=False)

    layered_count = int(df_out["is_layered_candidate"].sum())
    valid_count = int(df_out["layered_score"].notna().sum())

    print(f"Saved -> {out}")
    print(f"Valid layeredness scores: {valid_count}/{len(df_out)}")
    print(f"Layered candidates (score>={LAYERED_SCORE_THRESHOLD}): {layered_count}/{len(df_out)}")

if __name__ == "__main__":
    main()

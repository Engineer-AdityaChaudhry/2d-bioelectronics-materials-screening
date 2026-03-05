import os
import pandas as pd
from tqdm import tqdm

from mp_api.client import MPRester
from pymatgen.analysis.local_env import CrystalNN
from pymatgen.core.structure import Structure


# -----------------------------
# Project 1 - Module 2
# Layeredness / 2D-likeliness scoring using a bond-graph anisotropy proxy.
#
# Idea:
#   - Find neighbors (bonds) via CrystalNN.
#   - For each bond, compute the fractional displacement vector between sites.
#   - Count how many bonds have significant component along each lattice axis.
#   - Layered materials tend to have far fewer bonds along one axis (usually c-axis).
#
# Outputs:
#   layered_score in [0, 1]  (higher = more layered-like)
#   layer_axis = axis with weakest bonding (a/b/c)
#   anisotropy_ratio = min(axis_bonds) / max(axis_bonds)  (lower = more anisotropic)
# -----------------------------


AXES = ["a", "b", "c"]


def axis_bond_counts(struct: Structure, cnn: CrystalNN, frac_threshold: float = 0.35):
    """
    Count bonds that have significant projection on each fractional axis.
    frac_threshold: if |Δf_axis| > threshold, consider that bond 'crosses' that axis.
    Returns dict: { 'a': count, 'b': count, 'c': count }
    """
    counts = {ax: 0 for ax in AXES}

    for i in range(len(struct)):
        try:
            neighs = cnn.get_nn_info(struct, i)
        except Exception:
            # If neighbor finding fails for a site, skip it (rare)
            continue

        fi = struct[i].frac_coords
        for n in neighs:
            j = n["site_index"]
            fj = struct[j].frac_coords

            # Fractional displacement (wrap into [-0.5, 0.5])
            df = fj - fi
            df = df - df.round()

            # Count axis crossings
            if abs(df[0]) > frac_threshold:
                counts["a"] += 1
            if abs(df[1]) > frac_threshold:
                counts["b"] += 1
            if abs(df[2]) > frac_threshold:
                counts["c"] += 1

    return counts


def layered_score_from_counts(counts):
    """
    Convert axis bond counts -> layered score.
    Heuristic:
      - If one axis has much fewer bonds than the others, it's more layered-like.
      - anisotropy_ratio = min / max
      - layered_score = 1 - anisotropy_ratio  (clipped to [0, 1])
    """
    vals = [counts["a"], counts["b"], counts["c"]]
    vmax = max(vals) if max(vals) > 0 else 1
    vmin = min(vals)
    anis = vmin / vmax
    score = 1.0 - anis
    score = max(0.0, min(1.0, score))
    layer_axis = AXES[vals.index(vmin)]
    return score, anis, layer_axis


def main():
    api_key = os.environ.get("MP_API_KEY")
    if not api_key:
        raise RuntimeError("MP_API_KEY not found. Export it first.")

    inp = "data/processed/candidates_semiconductor.csv"
    if not os.path.exists(inp):
        raise FileNotFoundError(f"Missing input file: {inp}. Run filter_semiconductors.py first.")

    df = pd.read_csv(inp)

    # Neighbor finder: robust and common in materials workflows
    cnn = CrystalNN()

    results = []
    with MPRester(api_key) as mpr:
        for mid in tqdm(df["material_id"].tolist(), desc="Scoring layeredness"):
            try:
                # Fetch structure
                struct = mpr.get_structure_by_material_id(mid)
                if struct is None:
                    raise ValueError("No structure returned")

                counts = axis_bond_counts(struct, cnn)
                score, anis, axis = layered_score_from_counts(counts)

                results.append({
                    "material_id": mid,
                    "layered_score": score,
                    "anisotropy_ratio": anis,
                    "layer_axis": axis,
                    "axis_bonds_a": counts["a"],
                    "axis_bonds_b": counts["b"],
                    "axis_bonds_c": counts["c"],
                })

            except Exception as e:
                # Keep going; log failures
                results.append({
                    "material_id": mid,
                    "layered_score": None,
                    "anisotropy_ratio": None,
                    "layer_axis": None,
                    "axis_bonds_a": None,
                    "axis_bonds_b": None,
                    "axis_bonds_c": None,
                    "error": str(e)[:200],
                })

    df_res = pd.DataFrame(results)
    df_out = df.merge(df_res, on="material_id", how="left")

    # Simple classification threshold (tune later)
    df_out["is_layered_candidate"] = df_out["layered_score"].fillna(0) >= 0.6

    # Sort: layered first, then stable, then bandgap in-range
    df_out = df_out.sort_values(
        by=["is_layered_candidate", "layered_score", "energy_above_hull_eV", "band_gap_eV"],
        ascending=[False, False, True, True],
    ).reset_index(drop=True)

    os.makedirs("data/processed", exist_ok=True)
    out = "data/processed/candidates_semiconductor_layered.csv"
    df_out.to_csv(out, index=False)

    print(f"Saved -> {out}")
    print("Layered candidates (score>=0.6):", int(df_out["is_layered_candidate"].sum()))
    print("Total candidates:", len(df_out))


if __name__ == "__main__":
    main()

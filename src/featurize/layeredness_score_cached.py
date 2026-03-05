import os
import time
import json
import gzip
from typing import Optional, Dict, Tuple

import pandas as pd
from tqdm import tqdm

from mp_api.client import MPRester
from pymatgen.analysis.local_env import CrystalNN
from pymatgen.core.structure import Structure

# -----------------------------
# Layeredness v3: cached + resumable
# Input: candidates_prefilter_layered_chemistry.csv (or any CSV with material_id)
# Output: candidates_prefilter_layered_chemistry_layered.csv
# Cache: data/cache/structures/<material_id>.json.gz
# -----------------------------

INP = "data/processed/candidates_prefilter_layered_chemistry.csv"
OUT = "data/processed/candidates_prefilter_layered_chemistry_layered.csv"

CACHE_DIR = "data/cache/structures"
PARTIAL_DIR = "data/cache/partials"
PARTIAL_EVERY = 250  # write partial CSV every N materials

# Axis-crossing threshold
FRAC_THRESHOLD = 0.40

# Validity guards
MIN_TOTAL_BONDS = 20
MIN_INPLANE_BONDS = 10

# Layered threshold (tune later)
LAYERED_SCORE_THRESHOLD = 0.60

AXES = ["a", "b", "c"]


def cache_path(material_id: str) -> str:
    return os.path.join(CACHE_DIR, f"{material_id}.json.gz")


def save_structure_to_cache(material_id: str, struct: Structure) -> None:
    os.makedirs(CACHE_DIR, exist_ok=True)
    d = struct.as_dict()
    with gzip.open(cache_path(material_id), "wt", encoding="utf-8") as f:
        json.dump(d, f)


def load_structure_from_cache(material_id: str) -> Optional[Structure]:
    p = cache_path(material_id)
    if not os.path.exists(p):
        return None
    with gzip.open(p, "rt", encoding="utf-8") as f:
        d = json.load(f)
    return Structure.from_dict(d)


def mp_fetch_structure(mpr: MPRester, material_id: str, retries: int = 4) -> Structure:
    delay = 1.0
    last_err = None
    for _ in range(retries):
        try:
            s = mpr.get_structure_by_material_id(material_id)
            if s is None:
                raise ValueError("No structure returned")
            return s
        except Exception as e:
            last_err = e
            time.sleep(delay)
            delay *= 2
    raise RuntimeError(f"Failed to fetch structure after retries: {material_id} ({last_err})")


def wrapped_frac_delta(fi, fj):
    df = fj - fi
    return df - df.round()


def axis_bond_counts(struct: Structure, cnn: CrystalNN, frac_threshold: float = FRAC_THRESHOLD) -> Tuple[Dict[str, int], int]:
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


def layered_metrics(counts: Dict[str, int], total_bonds: int):
    a, b, c = counts["a"], counts["b"], counts["c"]
    vals = [a, b, c]
    vmax = max(vals)
    vmin = min(vals)

    if total_bonds < MIN_TOTAL_BONDS:
        return None, None, None, "too_few_total_bonds"
    if (a + b) < MIN_INPLANE_BONDS and (a + c) < MIN_INPLANE_BONDS and (b + c) < MIN_INPLANE_BONDS:
        # require at least one "plane" to be reasonably bonded
        return None, None, None, "too_few_inplane_bonds"
    if vmax == 0:
        return None, None, None, "no_axis_crossing_bonds"

    anis = vmin / vmax
    score = 1.0 - anis

    # axis with weakest bonding (ties possible)
    layer_axis = AXES[vals.index(vmin)]
    return score, anis, layer_axis, None


def write_partial(df_out: pd.DataFrame, tag: str) -> None:
    os.makedirs(PARTIAL_DIR, exist_ok=True)
    p = os.path.join(PARTIAL_DIR, f"layered_partial_{tag}.csv")
    df_out.to_csv(p, index=False)


def main():
    api_key = os.environ.get("MP_API_KEY")
    if not api_key:
        raise RuntimeError("MP_API_KEY not found. Export it first.")

    if not os.path.exists(INP):
        raise FileNotFoundError(f"Missing input file: {INP}")

    df = pd.read_csv(INP)
    if "material_id" not in df.columns:
        raise ValueError("Input CSV must contain material_id column")

    # If OUT exists, resume by skipping material_ids already scored
    done = set()
    if os.path.exists(OUT):
        try:
            existing = pd.read_csv(OUT)
            if "material_id" in existing.columns:
                done = set(existing["material_id"].astype(str).tolist())
                print(f"Resume: found {len(done)} already scored in {OUT}")
        except Exception:
            pass

    cnn = CrystalNN()

    rows = []
    with MPRester(api_key) as mpr:
        for idx, mid in enumerate(tqdm(df["material_id"].astype(str).tolist(), desc="Layeredness cached")):
            if mid in done:
                continue

            try:
                struct = load_structure_from_cache(mid)
                if struct is None:
                    struct = mp_fetch_structure(mpr, mid)
                    save_structure_to_cache(mid, struct)

                counts, total_bonds = axis_bond_counts(struct, cnn)
                score, anis, axis, reason = layered_metrics(counts, total_bonds)

                rows.append({
                    "material_id": mid,
                    "layered_score": score,
                    "anisotropy_ratio": anis,
                    "layer_axis": axis,
                    "axis_bonds_a": counts["a"],
                    "axis_bonds_b": counts["b"],
                    "axis_bonds_c": counts["c"],
                    "total_bonds": total_bonds,
                    "layered_invalid_reason": reason,
                })

            except Exception as e:
                rows.append({
                    "material_id": mid,
                    "layered_score": None,
                    "anisotropy_ratio": None,
                    "layer_axis": None,
                    "axis_bonds_a": None,
                    "axis_bonds_b": None,
                    "axis_bonds_c": None,
                    "total_bonds": None,
                    "layered_invalid_reason": f"error:{str(e)[:160]}",
                })

            # Periodically merge and write partial outputs for safety
            if (idx + 1) % PARTIAL_EVERY == 0:
                df_new = pd.DataFrame(rows)
                # Merge with any existing OUT so resume stays consistent
                if os.path.exists(OUT):
                    base = pd.read_csv(OUT)
                    merged = pd.concat([base, df_new], ignore_index=True).drop_duplicates(subset=["material_id"])
                else:
                    merged = df_new
                merged.to_csv(OUT, index=False)
                write_partial(merged, tag=str(idx + 1))
                rows = []

    # Final write
    if rows:
        df_new = pd.DataFrame(rows)
        if os.path.exists(OUT):
            base = pd.read_csv(OUT)
            merged = pd.concat([base, df_new], ignore_index=True).drop_duplicates(subset=["material_id"])
        else:
            merged = df_new
        merged.to_csv(OUT, index=False)

    # Join layeredness back onto input table for a full dataset
    layered = pd.read_csv(OUT)
    df_full = df.merge(layered, on="material_id", how="left")
    df_full["is_layered_candidate"] = df_full["layered_score"].fillna(-1) >= LAYERED_SCORE_THRESHOLD

    final_out = OUT.replace(".csv", "_joined.csv")
    df_full.to_csv(final_out, index=False)

    print(f"Saved layeredness table -> {OUT}")
    print(f"Saved joined dataset -> {final_out}")
    print("Layered candidates:", int(df_full["is_layered_candidate"].sum()), "out of", len(df_full))


if __name__ == "__main__":
    main()

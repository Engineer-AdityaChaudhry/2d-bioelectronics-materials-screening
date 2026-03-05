import os
import pandas as pd
from mp_api.client import MPRester

# Expanded search: property-based, not element-pair based.
# Goal: include canonical 2D semiconductors + related layered candidates.

FIELDS = [
    "material_id",
    "formula_pretty",
    "elements",
    "nelements",
    "band_gap",
    "energy_above_hull",
    "formation_energy_per_atom",
    "density",
    "nsites",
]

# Tunable constraints (keep manageable for layeredness step)
EG_MIN = 0.3
EG_MAX = 3.0
EHULL_MAX = 0.08
MAX_NELEMENTS = 4
MAX_NSITES = 60

def main():
    api_key = os.environ.get("MP_API_KEY")
    if not api_key:
        raise RuntimeError("MP_API_KEY not found. Export it first.")

    with MPRester(api_key) as mpr:
        docs = mpr.materials.summary.search(
            band_gap=(EG_MIN, EG_MAX),
            energy_above_hull=(0, EHULL_MAX),
            nelements=(1, MAX_NELEMENTS),
            nsites=(1, MAX_NSITES),
            fields=FIELDS,
        )

    rows = []
    for d in docs:
        rows.append({
            "material_id": d.material_id,
            "formula": d.formula_pretty,
            "elements": ",".join([e.symbol for e in d.elements]) if d.elements else None,
            "nelements": d.nelements,
            "band_gap_eV": d.band_gap,
            "energy_above_hull_eV": d.energy_above_hull,
            "formation_energy_per_atom_eV": d.formation_energy_per_atom,
            "density": d.density,
            "nsites": d.nsites,
        })

    df = pd.DataFrame(rows).drop_duplicates(subset=["material_id"]).reset_index(drop=True)

    os.makedirs("data/raw", exist_ok=True)
    out = "data/raw/mp_candidates_expanded_raw.csv"
    df.to_csv(out, index=False)

    print(f"Saved {len(df)} rows -> {out}")
    print("Filters:")
    print(f"  band_gap: {EG_MIN}–{EG_MAX} eV")
    print(f"  energy_above_hull: <= {EHULL_MAX} eV")
    print(f"  nelements <= {MAX_NELEMENTS}, nsites <= {MAX_NSITES}")

if __name__ == "__main__":
    main()

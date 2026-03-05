import os
from mp_api.client import MPRester
import pandas as pd
from tqdm import tqdm

# ---------
# Purpose:
# Pull candidate materials from Materials Project and save a reproducible raw CSV.
# ---------

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

# A practical starting query set for 2D semiconductor families:
# - TMD-like: (Mo, W) with (S, Se, Te)
# - Add a few layered semiconductor families commonly discussed: InSe / GaSe style
QUERY_SETS = [
    # TMD core families
    {"elements": ["Mo", "S"], "label": "Mo-S"},
    {"elements": ["Mo", "Se"], "label": "Mo-Se"},
    {"elements": ["Mo", "Te"], "label": "Mo-Te"},
    {"elements": ["W", "S"], "label": "W-S"},
    {"elements": ["W", "Se"], "label": "W-Se"},
    {"elements": ["W", "Te"], "label": "W-Te"},
    # Layered III-VI semiconductors (often relevant for optoelectronics)
    {"elements": ["In", "Se"], "label": "In-Se"},
    {"elements": ["Ga", "Se"], "label": "Ga-Se"},
]


def main():
    api_key = os.environ.get("MP_API_KEY")
    if not api_key:
        raise RuntimeError(
            "MP_API_KEY not found in environment. Export it first, e.g.\n"
            'export MP_API_KEY="YOUR_KEY"'
        )

    rows = []
    with MPRester(api_key) as mpr:
        for q in tqdm(QUERY_SETS, desc="Querying MP"):
            docs = mpr.materials.summary.search(
                elements=q["elements"],
                fields=FIELDS,
            )
            for d in docs:
                # d.elements can contain pymatgen Element objects -> convert to symbols for CSV
                element_symbols = ",".join([e.symbol for e in d.elements]) if d.elements else None

                rows.append(
                    {
                        "query_label": q["label"],
                        "material_id": d.material_id,
                        "formula": d.formula_pretty,
                        "elements": element_symbols,
                        "nelements": d.nelements,
                        "band_gap_eV": d.band_gap,
                        "energy_above_hull_eV": d.energy_above_hull,
                        "formation_energy_per_atom_eV": d.formation_energy_per_atom,
                        "density": d.density,
                        "nsites": d.nsites,
                    }
                )

    df = pd.DataFrame(rows).drop_duplicates(subset=["material_id"]).reset_index(drop=True)

    os.makedirs("data/raw", exist_ok=True)
    out = "data/raw/mp_candidates_raw.csv"
    df.to_csv(out, index=False)
    print(f"Saved {len(df)} rows -> {out}")


if __name__ == "__main__":
    main()
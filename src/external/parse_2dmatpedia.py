import os
import io
import json
import gzip
import zipfile
import pandas as pd

# Accept any of these names (we'll pick the first that exists)
CANDIDATES = [
    "data/external/2dmatpedia.zip",
    "data/external/2dmatpedia.json.gz",
    "data/external/2dmatpedia.json",
]

OUT = "data/external/2dmatpedia_props.csv"

def read_magic(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read(4)

def load_json_autodetect(path: str):
    magic = read_magic(path)

    # ZIP: starts with PK\x03\x04 (or PK..)
    if magic[:2] == b"PK":
        with zipfile.ZipFile(path, "r") as z:
            names = [n for n in z.namelist() if n.lower().endswith(".json")]
            if not names:
                # sometimes it's compressed as .jsonl or without extension
                names = z.namelist()
            # choose the largest file (most likely the dataset)
            names_sorted = sorted(names, key=lambda n: z.getinfo(n).file_size, reverse=True)
            target = names_sorted[0]
            with z.open(target) as f:
                return json.load(io.TextIOWrapper(f, encoding="utf-8"))

    # GZIP: 1f 8b
    if magic[:2] == b"\x1f\x8b":
        with gzip.open(path, "rt", encoding="utf-8") as f:
            return json.load(f)

    # Plain JSON: likely starts with { or [
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def safe_get(d, keys, default=None):
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur

def main():
    inp = None
    for p in CANDIDATES:
        if os.path.exists(p):
            inp = p
            break
    if inp is None:
        raise FileNotFoundError("2DMatPedia file not found in data/external/. Run the downloader first.")

    data = load_json_autodetect(inp)

    if isinstance(data, dict):
        records = list(data.values())
    elif isinstance(data, list):
        records = data
    else:
        raise ValueError(f"Unexpected JSON root type: {type(data)}")

    rows = []
    for r in records:
        formula = r.get("formula") or r.get("pretty_formula") or r.get("formula_pretty")

        # Best-effort field extraction (varies by release)
        eg  = r.get("band_gap") or r.get("gap") or safe_get(r, ["electronic", "band_gap"])
        vbm = r.get("vbm") or safe_get(r, ["electronic", "vbm"])
        cbm = r.get("cbm") or safe_get(r, ["electronic", "cbm"])
        wf  = r.get("work_function") or safe_get(r, ["electronic", "work_function"])

        magmom = r.get("magmom") or r.get("total_magnetic_moment") or safe_get(r, ["magnetic", "magmom"])
        piezo  = safe_get(r, ["piezoelectric", "dij_max"]) or r.get("piezo")
        eps    = safe_get(r, ["dielectric", "epsilon_static"]) or r.get("dielectric")
        elastic = safe_get(r, ["elastic", "c11"]) or r.get("elastic")

        rows.append({
            "ext_source": "2dmatpedia",
            "ext_id": r.get("material_id") or r.get("_id") or r.get("id"),
            "formula": formula,
            "band_gap_eV_ext": eg,
            "vbm_eV": vbm,
            "cbm_eV": cbm,
            "work_function_eV": wf,
            "magmom": magmom,
            "piezo_proxy": piezo,
            "dielectric_proxy": eps,
            "elastic_proxy": elastic,
        })

    df = pd.DataFrame(rows).dropna(subset=["formula"]).drop_duplicates(subset=["ext_source", "ext_id"])

    os.makedirs("data/external", exist_ok=True)
    df.to_csv(OUT, index=False)

    print(f"Loaded records: {len(records)} from {inp}")
    print(f"Saved -> {OUT} ({len(df)} rows)")
    print(df.head(5))

if __name__ == "__main__":
    main()

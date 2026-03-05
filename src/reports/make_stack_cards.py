import os
import pandas as pd

INP = "data/processed/top50_loc_ooc_robust_v3.csv"
OUT_MD = "reports/stack_cards_top50.md"
OUT_CSV = "data/processed/stack_cards_top50.csv"

ALKALI = {"Li","Na","K","Rb","Cs","Fr"}
HALOGEN = {"F","Cl","Br","I","At"}
TOXIC_HEAVY = {"Hg","Cd","Pb","As"}

def parse_elements(elements_str):
    if pd.isna(elements_str):
        return set()
    s = str(elements_str).replace('"','').replace(" ","")
    return set([e for e in s.split(",") if e])

def risk_level(elements):
    risk = "low"
    reasons = []
    if elements & TOXIC_HEAVY:
        risk = "high"
        reasons.append(f"heavy/toxic: {sorted(list(elements & TOXIC_HEAVY))}")
    if elements & HALOGEN and risk != "high":
        risk = "medium"
        reasons.append(f"halogen: {sorted(list(elements & HALOGEN))}")
    if elements & ALKALI and risk != "high":
        risk = "medium" if risk == "low" else risk
        reasons.append(f"alkali: {sorted(list(elements & ALKALI))}")
    if not reasons:
        reasons = ["no obvious reactive/toxic flags (Tier-1 heuristic)"]
    return risk, "; ".join(reasons)

def stack_template(risk):
    base = "CMOS readout → interconnect → 2D channel"
    contacts = "contacts: graphene or Ti/Au (contact engineering TBD)"
    microfluidics = "microfluidics: PDMS/glass channel + Ag/AgCl reference"
    if risk in {"medium","high"}:
        passivation = "passivation: hBN or ALD Al2O3/SiNx with sensing window"
        return f"{base} + {contacts} + {passivation} + {microfluidics}"
    return f"{base} + {contacts} + {microfluidics}"

def mitigation(risk, elements):
    items = []
    if elements & ALKALI:
        items.append("encapsulation strongly recommended (ion migration / moisture sensitivity)")
    if elements & HALOGEN:
        items.append("process compatibility check (corrosion / etch chemistry)")
    if elements & TOXIC_HEAVY:
        items.append("cleanroom restrictions likely (contamination control)")
    if not items:
        items.append("standard encapsulation and surface functionalization workflow")
    return "; ".join(items)

def main():
    if not os.path.exists(INP):
        raise FileNotFoundError(f"Missing {INP}. Run loc_ooc_scores_big_v3.py first.")

    df = pd.read_csv(INP).copy()

    # Build stack cards table
    cards = []
    for _, r in df.iterrows():
        els = parse_elements(r.get("elements",""))
        risk, reason = risk_level(els)
        cards.append({
            "material_id": r["material_id"],
            "formula": r["formula"],
            "elements": r.get("elements",""),
            "band_gap_eV": r.get("band_gap_eV", None),
            "energy_above_hull_eV": r.get("energy_above_hull_eV", None),
            "baseline_score_v3": r.get("baseline_score_v3", None),
            "loc_ooc_score_main": r.get("loc_ooc_score_main", None),
            "loc_ooc_score_robust_min": r.get("loc_ooc_score_robust_min", None),
            "integration_risk_level": risk,
            "integration_risk_reason": reason,
            "suggested_stack": stack_template(risk),
            "risk_mitigation_notes": mitigation(risk, els),
        })

    dfc = pd.DataFrame(cards)
    os.makedirs("data/processed", exist_ok=True)
    dfc.to_csv(OUT_CSV, index=False)

    # Write markdown report
    os.makedirs("reports", exist_ok=True)
    lines = []
    lines.append("# Stack Cards: Top50 Robust LoC/OoC Candidates\n")
    lines.append("This report is auto-generated from the computational pipeline.\n")
    lines.append("Columns: baseline score (nanoelectronics), LoC/OoC main score (physio 0.15M + 5nm), robust min score (worst-case across scenarios).\n")

    for i, row in dfc.iterrows():
        lines.append(f"## {i+1}. {row['formula']} ({row['material_id']})\n")
        lines.append(f"- **Band gap (eV):** {row['band_gap_eV']}\n")
        lines.append(f"- **Energy above hull (eV):** {row['energy_above_hull_eV']}\n")
        lines.append(f"- **Baseline score v3:** {row['baseline_score_v3']}\n")
        lines.append(f"- **LoC/OoC main score:** {row['loc_ooc_score_main']}\n")
        lines.append(f"- **LoC/OoC robust-min:** {row['loc_ooc_score_robust_min']}\n")
        lines.append(f"- **Integration risk:** {row['integration_risk_level']} — {row['integration_risk_reason']}\n")
        lines.append(f"- **Suggested stack:** {row['suggested_stack']}\n")
        lines.append(f"- **Mitigation notes:** {row['risk_mitigation_notes']}\n")
        lines.append("\n")

    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Saved CSV -> {OUT_CSV}")
    print(f"Saved report -> {OUT_MD}")
    print(dfc[["formula","integration_risk_level","loc_ooc_score_robust_min"]].head(10))

if __name__ == "__main__":
    main()

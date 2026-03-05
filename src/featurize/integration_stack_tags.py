import os
import pandas as pd

INP = "data/processed/top20_loc_ooc_ranked_v3.csv"
OUT = "data/processed/top20_loc_ooc_ranked_v3_stacks.csv"

ALKALI = {"Li", "Na", "K", "Rb", "Cs", "Fr"}
HALOGEN = {"F", "Cl", "Br", "I", "At"}
TOXIC_HEAVY = {"Hg", "Cd", "Pb", "As"}  # As is debatable; include as "process caution"

def parse_elements(elements_str):
    # elements column is like "Mo,K,S" or may be quoted with spaces
    if pd.isna(elements_str):
        return set()
    s = str(elements_str).replace('"', '').replace(" ", "")
    return set([e for e in s.split(",") if e])

def integration_risk(elements):
    # Simple transparent rubric
    risk = "low"
    reasons = []

    if len(elements & TOXIC_HEAVY) > 0:
        risk = "high"
        reasons.append(f"contains heavy/toxic: {sorted(list(elements & TOXIC_HEAVY))}")

    if len(elements & HALOGEN) > 0 and risk != "high":
        risk = "medium"
        reasons.append(f"contains halogen: {sorted(list(elements & HALOGEN))}")

    if len(elements & ALKALI) > 0 and risk != "high":
        # alkali often implies moisture sensitivity / ion migration
        risk = "medium" if risk == "low" else risk
        reasons.append(f"contains alkali: {sorted(list(elements & ALKALI))}")

    if not reasons:
        reasons.append("no obvious reactive/toxic flags (Tier-1 heuristic)")

    return risk, "; ".join(reasons)

def encapsulation_needed(risk, elements):
    # Recommend encapsulation if medium/high risk OR if alkali present
    if risk in {"medium", "high"}:
        return True
    if len(elements & ALKALI) > 0:
        return True
    return False

def suggested_stack(elements, encap):
    # Generic stack templates for bio-integrated 2D FETs
    # We keep it short and realistic.
    base = "CMOS readout → interconnect → 2D channel"
    contacts = "graphene or Ti/Au contacts (depending on work function matching)"
    passivation = "hBN or ALD Al2O3/SiNx passivation with sensing window"
    microfluidics = "PDMS/glass microfluidic channel + reference electrode"

    if encap:
        return f"{base} + {contacts} + {passivation} + {microfluidics}"
    else:
        return f"{base} + {contacts} + microfluidics (optional thin passivation)"

def module_tags(df_row):
    # Very light tags based on Eg range (photonics), chemistry (magnetics not inferable here)
    eg = df_row.get("band_gap_eV", None)
    tags = ["bioFET/LoC-OoC"]

    try:
        eg = float(eg)
        if 0.8 <= eg <= 2.2:
            tags.append("photonics-compatible")
    except Exception:
        pass

    return ",".join(tags)

def main():
    if not os.path.exists(INP):
        raise FileNotFoundError(f"Missing input file: {INP}. Run loc_ooc_scores_v3.py first.")

    df = pd.read_csv(INP).copy()

    risks = []
    for _, r in df.iterrows():
        elements = parse_elements(r.get("elements", ""))
        risk, reason = integration_risk(elements)
        encap = encapsulation_needed(risk, elements)

        risks.append({
            "integration_risk_level": risk,
            "integration_risk_reason": reason,
            "encapsulation_recommended": encap,
            "suggested_stack_template": suggested_stack(elements, encap),
            "module_tags": module_tags(r),
        })

    df2 = pd.concat([df, pd.DataFrame(risks)], axis=1)

    os.makedirs("data/processed", exist_ok=True)
    df2.to_csv(OUT, index=False)
    print(f"Saved -> {OUT}")
    print(df2[["formula","integration_risk_level","encapsulation_recommended","module_tags"]].head(10))

if __name__ == "__main__":
    main()

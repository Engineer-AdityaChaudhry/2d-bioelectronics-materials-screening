import os
import numpy as np
import pandas as pd

INP = "data/processed/top20_baseline_v3.csv"
OUT = "data/processed/top20_loc_ooc_ranked_v2.csv"

IONIC_STRENGTH = 0.15
DISTANCE_NM = 5.0

C_EDL = 10
C_OX = 5


def debye_length(I):
    return 0.304 / np.sqrt(I)


def attenuation(d, lam):
    return np.exp(-d / lam)


def gating_efficiency():
    return C_EDL / (C_EDL + C_OX)


def main():

    df = pd.read_csv(INP)

    lam = debye_length(IONIC_STRENGTH)
    A = attenuation(DISTANCE_NM, lam)
    eta = gating_efficiency()

    df["attenuation"] = A
    df["gating_efficiency"] = eta

    # Quantum capacitance proxy
    df["quantum_proxy"] = 1 / df["band_gap_eV"]

    # Dielectric screening proxy
    df["dielectric_proxy"] = 1 / df["density"]

    # Surface chemistry proxy
    df["surface_proxy"] = 1 / df["nelements"]

    df["loc_ooc_score_v2"] = (
        A
        * eta
        * df["quantum_proxy"]
        * df["dielectric_proxy"]
        * df["surface_proxy"]
    )

    df["loc_ooc_rank"] = df["loc_ooc_score_v2"].rank(
        ascending=False, method="min"
    )

    df = df.sort_values("loc_ooc_score_v2", ascending=False)

    df.to_csv(OUT, index=False)

    print("Top 10 LoC/OoC candidates:")
    print(
        df[
            [
                "material_id",
                "formula",
                "band_gap_eV",
                "density",
                "nelements",
                "loc_ooc_score_v2",
            ]
        ].head(10)
    )


if __name__ == "__main__":
    main()
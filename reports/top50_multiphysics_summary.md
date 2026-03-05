# Module 11 — Multi-physics Classification (Top50 robust LoC/OoC)

Magnetics and piezo tags are tri-state: yes/no/unknown (unknown means missing external data).

## Coverage

- magmom available: 0 / 50
- piezo available: 0 / 50

## Tag definitions
- photonics: 0.8 ≤ Eg ≤ 2.2
- magnetic: magmom ≥ 0.5 (else no; NaN → unknown)
- piezo/MEMS: piezo_proxy ≥ 0.1 (else no; NaN → unknown)
- bio-robust: robust_min in top quartile of Top50

| material_id   | formula    |   eg_used |   magmom |   piezo_proxy |   loc_ooc_score_robust_min | multiphysics_tags                                        |
|:--------------|:-----------|----------:|---------:|--------------:|---------------------------:|:---------------------------------------------------------|
| mp-9921       | ZrS3       |    1.1133 |      nan |           nan |                1.28116e-07 | bio-robust,photonics,magnetic:unknown,piezo/MEMS:unknown |
| mp-1211088    | LiCaP      |    1.3987 |      nan |           nan |                1.20121e-07 | bio-robust,photonics,magnetic:unknown,piezo/MEMS:unknown |
| mp-36330      | Li2VCl4    |    1.2285 |      nan |           nan |                1.18222e-07 | bio-robust,photonics,magnetic:unknown,piezo/MEMS:unknown |
| mp-684        | BaS2       |    1.5982 |      nan |           nan |                1.01813e-07 | bio-robust,photonics,magnetic:unknown,piezo/MEMS:unknown |
| mp-22956      | K2PdCl4    |    1.4279 |      nan |           nan |                1.00993e-07 | bio-robust,photonics,magnetic:unknown,piezo/MEMS:unknown |
| mp-1186991    | ScI3       |    1.6942 |      nan |           nan |                9.90377e-08 | bio-robust,photonics,magnetic:unknown,piezo/MEMS:unknown |
| mp-541289     | Y2S3       |    1.5992 |      nan |           nan |                9.87942e-08 | bio-robust,photonics,magnetic:unknown,piezo/MEMS:unknown |
| mp-7475       | La2S3      |    1.0358 |      nan |           nan |                9.741e-08   | bio-robust,photonics,magnetic:unknown,piezo/MEMS:unknown |
| mp-17597      | Ca(ScS2)2  |    1.2863 |      nan |           nan |                9.69536e-08 | bio-robust,photonics,magnetic:unknown,piezo/MEMS:unknown |
| mp-22887      | EuCl2      |    1.2144 |      nan |           nan |                9.05776e-08 | bio-robust,photonics,magnetic:unknown,piezo/MEMS:unknown |
| mp-569309     | RbMnCl3    |    1.3133 |      nan |           nan |                9.04071e-08 | bio-robust,photonics,magnetic:unknown,piezo/MEMS:unknown |
| mp-28328      | RbI3       |    1.6271 |      nan |           nan |                8.78859e-08 | bio-robust,photonics,magnetic:unknown,piezo/MEMS:unknown |
| mp-1103889    | Eu(AlS2)2  |    1.1797 |      nan |           nan |                8.70392e-08 | bio-robust,photonics,magnetic:unknown,piezo/MEMS:unknown |
| mp-573763     | Cs2Te      |    1.774  |      nan |           nan |                8.63905e-08 | photonics,magnetic:unknown,piezo/MEMS:unknown            |
| mp-22876      | CsI3       |    1.6766 |      nan |           nan |                8.61927e-08 | photonics,magnetic:unknown,piezo/MEMS:unknown            |
| mp-9843       | Sr3(AlP2)2 |    1.3365 |      nan |           nan |                8.55427e-08 | photonics,magnetic:unknown,piezo/MEMS:unknown            |
| mp-19795      | InS        |    1.3508 |      nan |           nan |                8.44723e-08 | photonics,magnetic:unknown,piezo/MEMS:unknown            |
| mp-27138      | K2PdBr4    |    1.2049 |      nan |           nan |                8.44358e-08 | photonics,magnetic:unknown,piezo/MEMS:unknown            |
| mp-1209449    | Rb3LuCl6   |    1.3029 |      nan |           nan |                8.34829e-08 | photonics,magnetic:unknown,piezo/MEMS:unknown            |
| mp-18612      | Rb2MoS4    |    1.575  |      nan |           nan |                8.32838e-08 | photonics,magnetic:unknown,piezo/MEMS:unknown            |
| mp-17678      | Sr(ScS2)2  |    1.357  |      nan |           nan |                8.30104e-08 | photonics,magnetic:unknown,piezo/MEMS:unknown            |
| mp-8965       | K2Sn2S5    |    1.4063 |      nan |           nan |                8.28043e-08 | photonics,magnetic:unknown,piezo/MEMS:unknown            |
| mp-1211440    | K2PbCl6    |    1.6065 |      nan |           nan |                8.08789e-08 | photonics,magnetic:unknown,piezo/MEMS:unknown            |
| mp-27181      | KAuCl4     |    1.4257 |      nan |           nan |                7.97264e-08 | photonics,magnetic:unknown,piezo/MEMS:unknown            |
| mp-1102093    | EuI2       |    1.3259 |      nan |           nan |                7.93712e-08 | photonics,magnetic:unknown,piezo/MEMS:unknown            |
| mp-1025201    | Rb2PdCl4   |    1.7485 |      nan |           nan |                7.78e-08    | photonics,magnetic:unknown,piezo/MEMS:unknown            |
| mp-1211293    | La(YS2)3   |    1.0838 |      nan |           nan |                7.58865e-08 | photonics,magnetic:unknown,piezo/MEMS:unknown            |
| mp-558121     | K4Ba(VS4)2 |    1.5514 |      nan |           nan |                7.52264e-08 | photonics,magnetic:unknown,piezo/MEMS:unknown            |
| mp-18642      | Ca(YS2)2   |    1.5361 |      nan |           nan |                7.43565e-08 | photonics,magnetic:unknown,piezo/MEMS:unknown            |
| mp-568986     | KAuCl4     |    1.4211 |      nan |           nan |                7.3298e-08  | photonics,magnetic:unknown,piezo/MEMS:unknown            |
| mp-1223847    | K2PdBrCl3  |    1.4958 |      nan |           nan |                7.17988e-08 | photonics,magnetic:unknown,piezo/MEMS:unknown            |
| mp-1078085    | Cs2PdCl4   |    1.839  |      nan |           nan |                7.08373e-08 | photonics,magnetic:unknown,piezo/MEMS:unknown            |
| mp-22934      | K2PtCl4    |    1.8196 |      nan |           nan |                6.83847e-08 | photonics,magnetic:unknown,piezo/MEMS:unknown            |
| mp-574040     | K2SnBr6    |    1.6124 |      nan |           nan |                6.73351e-08 | photonics,magnetic:unknown,piezo/MEMS:unknown            |
| mp-1079673    | ThSe3      |    1.2728 |      nan |           nan |                6.65995e-08 | photonics,magnetic:unknown,piezo/MEMS:unknown            |
| mp-1173753    | Na2Ga2Se3  |    1.3627 |      nan |           nan |                6.63024e-08 | photonics,magnetic:unknown,piezo/MEMS:unknown            |
| mp-1146       | ThS2       |    1.0336 |      nan |           nan |                6.62491e-08 | photonics,magnetic:unknown,piezo/MEMS:unknown            |
| mp-1223861    | K2PdBr3Cl  |    1.3535 |      nan |           nan |                6.60952e-08 | photonics,magnetic:unknown,piezo/MEMS:unknown            |
| mp-1079264    | Nb(SBr)2   |    1.4107 |      nan |           nan |                6.60588e-08 | photonics,magnetic:unknown,piezo/MEMS:unknown            |
| mp-1095291    | Li2SnSe3   |    1.4797 |      nan |           nan |                6.59972e-08 | photonics,magnetic:unknown,piezo/MEMS:unknown            |
| mp-878        | Ho2S3      |    1.4613 |      nan |           nan |                6.56556e-08 | photonics,magnetic:unknown,piezo/MEMS:unknown            |
| mp-7219       | Na2ZrSe3   |    1.3166 |      nan |           nan |                6.48605e-08 | photonics,magnetic:unknown,piezo/MEMS:unknown            |
| mp-29084      | Ba2GdCl7   |    1.5615 |      nan |           nan |                6.46682e-08 | photonics,magnetic:unknown,piezo/MEMS:unknown            |
| mp-27243      | K2PtBr4    |    1.477  |      nan |           nan |                6.39447e-08 | photonics,magnetic:unknown,piezo/MEMS:unknown            |
| mp-2234       | Er2S3      |    1.4691 |      nan |           nan |                6.37759e-08 | photonics,magnetic:unknown,piezo/MEMS:unknown            |
| mp-1227892    | BaNaVS4    |    1.5001 |      nan |           nan |                6.30727e-08 | photonics,magnetic:unknown,piezo/MEMS:unknown            |
| mp-32689      | Pr2Se3     |    1.4751 |      nan |           nan |                6.26838e-08 | photonics,magnetic:unknown,piezo/MEMS:unknown            |
| mp-32798      | La2Se3     |    1.58   |      nan |           nan |                6.26483e-08 | photonics,magnetic:unknown,piezo/MEMS:unknown            |
| mp-675237     | Na3GdI6    |    1.5496 |      nan |           nan |                6.12439e-08 | photonics,magnetic:unknown,piezo/MEMS:unknown            |
| mp-29035      | Sr(YS2)2   |    1.8122 |      nan |           nan |                6.10373e-08 | photonics,magnetic:unknown,piezo/MEMS:unknown            |

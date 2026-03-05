# Module 10 — Heterostructure Stack Simulation (Tier-1)

This report evaluates contact tendency (graphene/Au/Ti) when vacuum band edges are available.
Dielectrics are listed as stack options.

## Coverage

- Rows: 300
- Band-edge based contact classification available for some rows.

## Sample rows

| material_id   | formula   | partner   | partner_type   |   partner_work_function_eV |   vbm_eV |   cbm_eV | contact_class                |   loc_ooc_score_robust_min |   baseline_score_v3 |
|:--------------|:----------|:----------|:---------------|---------------------------:|---------:|---------:|:-----------------------------|---------------------------:|--------------------:|
| mp-9921       | ZrS3      | graphene  | contact        |                        4.6 |      nan |      nan | unknown (missing band edges) |                1.28116e-07 |            0.81094  |
| mp-9921       | ZrS3      | Au        | contact        |                        5.1 |      nan |      nan | unknown (missing band edges) |                1.28116e-07 |            0.81094  |
| mp-9921       | ZrS3      | Ti        | contact        |                        4.3 |      nan |      nan | unknown (missing band edges) |                1.28116e-07 |            0.81094  |
| mp-9921       | ZrS3      | hBN       | dielectric     |                      nan   |      nan |      nan | nan                          |                1.28116e-07 |            0.81094  |
| mp-9921       | ZrS3      | Al2O3     | dielectric     |                      nan   |      nan |      nan | nan                          |                1.28116e-07 |            0.81094  |
| mp-9921       | ZrS3      | HfO2      | dielectric     |                      nan   |      nan |      nan | nan                          |                1.28116e-07 |            0.81094  |
| mp-1211088    | LiCaP     | graphene  | contact        |                        4.6 |      nan |      nan | unknown (missing band edges) |                1.20121e-07 |            0.830575 |
| mp-1211088    | LiCaP     | Au        | contact        |                        5.1 |      nan |      nan | unknown (missing band edges) |                1.20121e-07 |            0.830575 |
| mp-1211088    | LiCaP     | Ti        | contact        |                        4.3 |      nan |      nan | unknown (missing band edges) |                1.20121e-07 |            0.830575 |
| mp-1211088    | LiCaP     | hBN       | dielectric     |                      nan   |      nan |      nan | nan                          |                1.20121e-07 |            0.830575 |
| mp-1211088    | LiCaP     | Al2O3     | dielectric     |                      nan   |      nan |      nan | nan                          |                1.20121e-07 |            0.830575 |
| mp-1211088    | LiCaP     | HfO2      | dielectric     |                      nan   |      nan |      nan | nan                          |                1.20121e-07 |            0.830575 |
| mp-36330      | Li2VCl4   | graphene  | contact        |                        4.6 |      nan |      nan | unknown (missing band edges) |                1.18222e-07 |            0.826539 |
| mp-36330      | Li2VCl4   | Au        | contact        |                        5.1 |      nan |      nan | unknown (missing band edges) |                1.18222e-07 |            0.826539 |
| mp-36330      | Li2VCl4   | Ti        | contact        |                        4.3 |      nan |      nan | unknown (missing band edges) |                1.18222e-07 |            0.826539 |
| mp-36330      | Li2VCl4   | hBN       | dielectric     |                      nan   |      nan |      nan | nan                          |                1.18222e-07 |            0.826539 |
| mp-36330      | Li2VCl4   | Al2O3     | dielectric     |                      nan   |      nan |      nan | nan                          |                1.18222e-07 |            0.826539 |
| mp-36330      | Li2VCl4   | HfO2      | dielectric     |                      nan   |      nan |      nan | nan                          |                1.18222e-07 |            0.826539 |
| mp-684        | BaS2      | graphene  | contact        |                        4.6 |      nan |      nan | unknown (missing band edges) |                1.01813e-07 |            0.880987 |
| mp-684        | BaS2      | Au        | contact        |                        5.1 |      nan |      nan | unknown (missing band edges) |                1.01813e-07 |            0.880987 |
| mp-684        | BaS2      | Ti        | contact        |                        4.3 |      nan |      nan | unknown (missing band edges) |                1.01813e-07 |            0.880987 |
| mp-684        | BaS2      | hBN       | dielectric     |                      nan   |      nan |      nan | nan                          |                1.01813e-07 |            0.880987 |
| mp-684        | BaS2      | Al2O3     | dielectric     |                      nan   |      nan |      nan | nan                          |                1.01813e-07 |            0.880987 |
| mp-684        | BaS2      | HfO2      | dielectric     |                      nan   |      nan |      nan | nan                          |                1.01813e-07 |            0.880987 |
| mp-22956      | K2PdCl4   | graphene  | contact        |                        4.6 |      nan |      nan | unknown (missing band edges) |                1.00993e-07 |            0.857927 |
| mp-22956      | K2PdCl4   | Au        | contact        |                        5.1 |      nan |      nan | unknown (missing band edges) |                1.00993e-07 |            0.857927 |
| mp-22956      | K2PdCl4   | Ti        | contact        |                        4.3 |      nan |      nan | unknown (missing band edges) |                1.00993e-07 |            0.857927 |
| mp-22956      | K2PdCl4   | hBN       | dielectric     |                      nan   |      nan |      nan | nan                          |                1.00993e-07 |            0.857927 |
| mp-22956      | K2PdCl4   | Al2O3     | dielectric     |                      nan   |      nan |      nan | nan                          |                1.00993e-07 |            0.857927 |
| mp-22956      | K2PdCl4   | HfO2      | dielectric     |                      nan   |      nan |      nan | nan                          |                1.00993e-07 |            0.857927 |
| mp-1186991    | ScI3      | graphene  | contact        |                        4.6 |      nan |      nan | unknown (missing band edges) |                9.90377e-08 |            0.851315 |
| mp-1186991    | ScI3      | Au        | contact        |                        5.1 |      nan |      nan | unknown (missing band edges) |                9.90377e-08 |            0.851315 |
| mp-1186991    | ScI3      | Ti        | contact        |                        4.3 |      nan |      nan | unknown (missing band edges) |                9.90377e-08 |            0.851315 |
| mp-1186991    | ScI3      | hBN       | dielectric     |                      nan   |      nan |      nan | nan                          |                9.90377e-08 |            0.851315 |
| mp-1186991    | ScI3      | Al2O3     | dielectric     |                      nan   |      nan |      nan | nan                          |                9.90377e-08 |            0.851315 |
| mp-1186991    | ScI3      | HfO2      | dielectric     |                      nan   |      nan |      nan | nan                          |                9.90377e-08 |            0.851315 |
| mp-541289     | Y2S3      | graphene  | contact        |                        4.6 |      nan |      nan | unknown (missing band edges) |                9.87942e-08 |            0.881851 |
| mp-541289     | Y2S3      | Au        | contact        |                        5.1 |      nan |      nan | unknown (missing band edges) |                9.87942e-08 |            0.881851 |
| mp-541289     | Y2S3      | Ti        | contact        |                        4.3 |      nan |      nan | unknown (missing band edges) |                9.87942e-08 |            0.881851 |
| mp-541289     | Y2S3      | hBN       | dielectric     |                      nan   |      nan |      nan | nan                          |                9.87942e-08 |            0.881851 |

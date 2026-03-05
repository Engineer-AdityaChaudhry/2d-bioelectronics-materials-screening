# Results

This document summarizes the results obtained from the **2D Bioelectronics Materials Screening Framework**.

The pipeline screened thousands of materials and identified a shortlist of layered semiconductor candidates potentially suitable for bio-integrated electronic systems.

---

# Dataset Reduction

The screening pipeline progressively reduced the dataset:

| Stage | Materials Remaining |
|------|--------------------|
Raw materials retrieved | 23,073 |
After semiconductor filtering | 5,707 |
Layered structure candidates | 1,963 |
Top ranked shortlist | 200 |
Final bioelectronics candidates | 50 |

This reduction highlights the **selective filtering capability of the framework**.

---

# Layered Materials Discovery

The layered structure detection algorithm identified **1,963 materials** with strong bonding anisotropy.

These materials are promising because layered crystals may be:

- exfoliable
- mechanically flexible
- compatible with nanoscale device architectures

Many known layered materials fall into this category, including transition-metal chalcogenides.

---

# Multi-Objective Ranking Results

The ranking algorithm identified materials with favorable combinations of:

- semiconductor band gaps
- thermodynamic stability
- layered bonding structure
- moderate structural complexity

This ranking produced a **top 200 candidate list**.

---

# Bioelectronics Robustness Ranking

Materials were further evaluated using the **LoC/OoC robustness scoring system**.

This scoring system estimates compatibility with:

- electrolyte environments
- nanoscale sensor geometries
- bio-integrated device operation

From the ranked list:

**50 materials were identified as robust candidates.**

---

# Example Candidate Materials

Top candidate materials include:

| Material | Band Gap (eV) |
|--------|---------------|
ZrS₃ | 1.11 |
LiCaP | 1.40 |
Li₂VCl₄ | 1.23 |
BaS₂ | 1.60 |
K₂PdCl₄ | 1.43 |

These materials represent **layered semiconductor candidates with promising electronic properties**.

---

# Device Integration Analysis

Heterostructure simulations were performed for the top materials using common device components.

Contacts tested:

- graphene
- gold
- titanium

Dielectrics tested:

- hBN
- Al₂O₃
- HfO₂

These simulations help evaluate **device compatibility and integration feasibility**.

---

# Multiphysics Classification

The candidate materials were categorized according to potential application areas.

Example tags include:

- bio-robust electronics
- photonic sensing
- magnetic materials (when data available)
- piezoelectric / MEMS materials (when data available)

This classification helps guide **future device-oriented research**.

---

# Visualization Outputs

The pipeline generates several visualizations:

### Pareto optimization

Shows trade-offs between stability, band gap, and layeredness.

### Ranking shift plots

Shows how materials move in ranking when bioelectronics robustness is considered.

### Candidate summary plots

Displays the final shortlisted materials.

---

# Limitations

Several limitations should be noted:

1. Not all materials are confirmed exfoliable 2D materials.
2. Magnetic and piezoelectric properties were unavailable for many candidates.
3. Device simulations are simplified approximations.

Future work will address these limitations using **DFT simulations and specialized 2D materials databases**.

---

# Implications

The results demonstrate that **materials informatics pipelines can efficiently screen large materials databases to identify promising candidates for emerging semiconductor applications.**

This framework provides a **starting point for further electronic structure analysis and experimental validation**.

These next steps are addressed in:

**Project 2 — Electronic Structure Analysis of 2D Biosensing Materials.**


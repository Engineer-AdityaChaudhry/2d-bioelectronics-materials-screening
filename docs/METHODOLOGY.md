# Methodology

This document describes the computational methodology used in the **2D Bioelectronics Materials Screening Framework**.

The goal of the framework is to identify **layered semiconductor materials that may be suitable for bio-integrated electronic devices** such as biosensors, BioFETs, and Lab-on-Chip systems.

The screening pipeline integrates **materials databases, structural analysis, multi-objective ranking, and device-oriented scoring**.

---

# 1. Data Source

The starting point of the pipeline is the **Materials Project database**, which contains computational materials data generated using density functional theory (DFT).

The database provides properties such as:

- crystal structure
- band gap
- formation energy
- thermodynamic stability
- density
- elemental composition

Materials are retrieved programmatically using the Materials Project API.

Initial filtering constraints:

- band gap: **0.3 – 3.0 eV**
- energy above hull: **≤ 0.08 eV**
- number of elements: **≤ 4**
- number of atomic sites: **≤ 60**

This query produced approximately **23,000 candidate materials**.

---

# 2. Semiconductor Pre-Filtering

Materials were filtered based on electronic and thermodynamic criteria to identify semiconductor candidates.

Filtering criteria:

- suitable band gap range for electronic devices
- thermodynamic stability
- moderate structural complexity

After this filtering stage:

**23,073 → 5,707 materials**

---

# 3. Layered Structure Identification

Layered materials are promising because they can often be **exfoliated into two-dimensional (2D) sheets**.

The framework estimates layeredness using **bond connectivity anisotropy**.

Procedure:

1. Crystal structures are analyzed using pymatgen.
2. Bond networks are computed along the three crystallographic axes.
3. Bond density anisotropy is calculated.
4. Materials with strong directional bonding are identified as layered candidates.

Outputs:

- layered score
- anisotropy ratio
- dominant layer axis

After layered filtering:

**5,707 → 1,963 layered candidates**

---

# 4. Multi-Objective Material Ranking

Candidate materials are ranked using a **multi-objective scoring function**.

The ranking considers:

### Band gap suitability
Materials with band gaps close to the target range for electronic sensors are favored.

### Thermodynamic stability
Lower formation energies and lower energy above hull values indicate higher stability.

### Layered structure strength
Higher layered scores indicate stronger anisotropic bonding.

### Structural complexity
Materials with moderate complexity are favored for fabrication feasibility.

These factors are combined into a **baseline ranking score**.

---

# 5. Bioelectronics Environment Scoring

For bio-integrated devices, materials must function in environments such as:

- electrolyte solutions
- physiological buffers
- nanoscale device geometries

A **Lab-on-Chip / Organ-on-Chip score (LoC/OoC score)** was defined.

The score considers:

- density
- elemental complexity
- device scaling assumptions

A **robustness score** is calculated across several simulated conditions.

This produces a **robust LoC/OoC compatibility metric**.

---

# 6. Candidate Selection

After ranking and robustness evaluation:

- Top **200 materials** are retained
- Top **50 materials** are selected as **bioelectronics candidates**

These materials represent **layered semiconductors with favorable electronic properties and environmental robustness**.

---

# 7. Heterostructure Integration Simulation

Candidate materials were evaluated for compatibility with common semiconductor device stacks.

Simulated components include:

Contacts:
- graphene
- gold (Au)
- titanium (Ti)

Dielectrics:
- hexagonal boron nitride (hBN)
- aluminum oxide (Al₂O₃)
- hafnium oxide (HfO₂)

These simulations evaluate potential **device integration scenarios**.

---

# 8. Multiphysics Classification

The framework also performs **application-oriented tagging**.

Materials are classified according to possible physical functionality:

- photonic sensing
- bio-robust electronics
- magnetic behavior (when data available)
- piezoelectric / MEMS potential (when data available)

External databases were used when available for these properties.

---

# 9. Reproducibility

The entire workflow is automated using a **Makefile-based pipeline**.

Execution order:

```

expanded → prefilter → layered → rank → loc → stacks → multiphysics → reports

```

Running the full pipeline:

```

make all

```

This ensures the analysis can be reproduced from raw data.

---

# Summary

The methodology integrates:

- materials database mining
- structural analysis
- multi-objective ranking
- device environment scoring
- integration simulation

This pipeline enables **large-scale discovery of layered semiconductor candidates for bio-integrated electronic devices**.



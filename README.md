# 2D Bioelectronics Materials Screening Framework

Computational pipeline for **discovering layered semiconductor candidates for bio-integrated electronics** within **More-than-Moore semiconductor platforms**.

This repository implements a **materials informatics workflow** that screens thousands of materials to identify layered semiconductor candidates suitable for:

* biosensors
* BioFET devices
* Lab-on-Chip (LoC) platforms
* Organ-on-Chip (OoC) systems

The framework integrates **materials databases, structural analysis, device-oriented ranking, and heterogeneous integration simulations**.

---

# Research Motivation

Traditional semiconductor technologies rely heavily on silicon CMOS. However, emerging **More-than-Moore technologies** require materials that support additional functions such as sensing, photonics, and bio-interfaces.

Bio-integrated electronics require materials that are:

* atomically thin or easily exfoliable
* sensitive to surface charge
* chemically stable in liquid environments
* compatible with heterogeneous semiconductor integration

Layered crystals are particularly promising because they can often be **exfoliated into two-dimensional (2D) materials** suitable for nanoelectronic sensing devices.

This project builds a **computational screening pipeline** to identify such materials from large crystal structure databases.

---

# Pipeline Overview

The pipeline processes thousands of materials and progressively narrows down promising candidates.

```
Materials Project database (~23k materials)
            ↓
Semiconductor filtering
            ↓
Layered structure detection
            ↓
Device suitability ranking
            ↓
LoC / OoC environment scoring
            ↓
Top candidate materials
```

The result is a **ranked dataset of layered semiconductor candidates potentially suitable for 2D bioelectronics applications**.

---

# Dataset Reduction

| Stage                              | Materials Remaining |
| ---------------------------------- | ------------------- |
| Raw materials retrieved            | ~23,073             |
| After semiconductor filtering      | 5,707               |
| Layered structure candidates       | 1,963               |
| Top ranked semiconductor shortlist | 200                 |
| Bio-robust materials shortlist     | 50                  |

These 50 materials form the **final candidate set for further electronic-structure analysis**.

---

# Key Analysis Modules

## 1. Materials Database Mining

Materials are retrieved from the **Materials Project database** using the MP API.

Properties extracted include:

* band gap
* formation energy per atom
* energy above hull
* density
* atomic composition

These properties are used for initial filtering and ranking.

---

## 2. Semiconductor Filtering

Materials are filtered using constraints such as:

* band gap window
* thermodynamic stability
* compositional complexity

This step identifies materials potentially suitable for **electronic device applications**.

---

## 3. Layered Structure Detection

A structural analysis algorithm identifies materials with **anisotropic bonding**, suggesting layered crystal structures.

Layered materials are promising because they may be **exfoliable into 2D sheets**.

---

## 4. Multi-Objective Ranking

Candidate materials are ranked using multiple criteria:

* band gap suitability
* thermodynamic stability
* structural layeredness
* chemical complexity

This produces a **baseline ranking of semiconductor candidates**.

---

## 5. Bio-Environment Scoring

Materials are evaluated for **robustness in bio-integrated environments**, including:

* electrolyte screening conditions
* nanoscale channel thickness scenarios

A **LoC/OoC robustness score** identifies materials potentially suitable for bioelectronic devices.

---

## 6. Heterogeneous Integration Simulation

Potential device stacks are simulated using common semiconductor interfaces:

* graphene contacts
* Au / Ti electrodes
* hBN dielectric layers
* oxide gate materials

This step evaluates **device integration compatibility**.

---

## 7. Multiphysics Tagging

Materials are categorized for potential applications such as:

* photonic sensing
* bio-robust electronics
* magnetics or piezoelectric devices (when data available)

---

# Final Outputs

The pipeline generates multiple datasets and reports.

## Ranked candidate materials

```
data/processed/top50_loc_ooc_robust_v3.csv
```

Top materials suitable for **bio-integrated semiconductor systems**.

---

## Heterostructure stack simulations

```
data/processed/heterostacks_top50.csv
reports/heterostacks_top50.md
```

Potential device architectures for the candidate materials.

---

## Multiphysics classification

```
data/processed/top50_multiphysics_tags.csv
reports/top50_multiphysics_summary.md
```

Categorization of materials by potential physical applications.

---

## Selected materials summary

```
data/processed/project1_selected_materials.csv
reports/project1_selected_materials.md
figures/project1_selected_materials.png
```

Final shortlist of materials produced by the screening framework.

---

# Example Top Candidate Materials

Example materials identified by the pipeline:

* ZrS₃
* LiCaP
* Li₂VCl₄
* BaS₂
* K₂PdCl₄

These materials represent **layered semiconductor candidates potentially suitable for 2D bioelectronics applications**.

---

# Installation

Create a Python environment using Conda or Mamba.

```bash
mamba create -n mtm2d python=3.11
mamba activate mtm2d
```

Install dependencies:

```bash
pip install pandas numpy matplotlib tqdm
pip install pymatgen mp-api ase
```

---

# Setup

Export your Materials Project API key:

```bash
export MP_API_KEY="YOUR_API_KEY"
```

---

# Running the Pipeline

The entire workflow can be executed using the Makefile.

Run the full pipeline:

```bash
make all
```

Pipeline stages:

```
expanded → prefilter → layered → rank → loc → stacks → multiphysics → reports
```

---

# Repository Structure

```
2d-mtm-atlas
│
├── data
│   ├── raw
│   ├── processed
│   └── external
│
├── figures
│
├── reports
│
├── src
│   ├── fetch
│   ├── featurize
│   ├── rank
│   ├── stack
│   ├── viz
│   └── reports
│
└── Makefile
```

---

# Research Context

This project supports research into **More-than-Moore semiconductor technologies**, where new materials enable:

* biosensing devices
* flexible electronics
* heterogeneous integration
* nanoelectronic sensors

The framework demonstrates how **materials informatics can accelerate the discovery of layered semiconductor candidates for bio-integrated systems**.

---

# Future Work

Planned extensions include:

* DFT electronic structure simulations
* exfoliation energy estimation
* device-level sensor simulations
* integration with dedicated 2D materials databases

These extensions form the basis of:

**Project 2 — Electronic Structure Analysis of 2D Biosensing Materials**

---

# Author

Aditya Chaudhry
Computational Materials Research Portfolio

---

# 2d-bioelectronics-materials-screening
# 2d-bioelectronics-materials-screening

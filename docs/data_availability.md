# Data Availability Statement

**Project:** ATS CV Optimizer  
**Version:** 1.1  
**Date:** 2025-12-29

---

## Summary

All data required to reproduce the results of this research are included in the `research_package/` directory. The dataset is **synthetically generated** by this project and does not depend on any external data sources.

---

## Dataset Type

**Type:** Synthetic benchmark dataset  
**Generation:** AI-assisted using ChatGPT/OpenAI for text content, structured via [`benchmark_dataset.py`](../benchmark_dataset.py)  
**Purpose:** Validate ATS and JobFit scoring algorithms across multiple domains  
**Rights:** Authors affirm ownership of synthetic outputs; inputs contained no third-party copyrighted material.

> [!NOTE]
> This is NOT a collection of real CVs or job descriptions. All CV-JD pairs are fabricated for testing purposes.

---

## What IS Shared

### ✅ Included in This Repository

1. **Synthetic Benchmark Dataset**
   - Location: [`research_package/benchmark_dataset_v1.json`](../research_package/benchmark_dataset_v1.json)
   - Format: JSON (Pydantic schema)
   - Size: 1 CV-JD pair (expandable to 50+)
   - Domains: Software Engineering, Data Science, Marketing, Healthcare, Education

2. **Dataset Generation Script**
   - Location: [`benchmark_dataset.py`](../benchmark_dataset.py)
   - Purpose: Allows researchers to regenerate or extend the dataset
   - Usage: `python benchmark_dataset.py`

3. **Evaluation Results**
   - Location: [`research_package/experiments/cv_jd_eval_before_after_20251226_v01.csv`](../research_package/experiments/cv_jd_eval_before_after_20251226_v01.csv)
   - Content: Aggregated metrics (ATS scores, JobFit scores, deltas)
   - Privacy: No raw CV/JD text; only scores and metadata

4. **Ablation Study Results**
   - Format: CSV with component-level score breakdowns
   - Purpose: Demonstrate impact of individual scoring components

5. **Configuration Files**
   - Location: [`research_package/configs/`](../research_package/configs/)
   - Content: Scoring weights, thresholds, word lists
   - Purpose: Exact reproducibility of scoring algorithms

6. **Complete Source Code**
   - Location: Repository root
   - Modules: Parsers, scorers, rewriting engine, validators
   - Documentation: [`docs/`](../docs/) directory

7. **Reproducibility Manifest**
   - Location: [`research_package/REPRODUCIBILITY_MANIFEST.json`](../research_package/REPRODUCIBILITY_MANIFEST.json)
   - Content: Environment details, package versions, checksums

---

## What is NOT Shared

### ❌ Not Included (Privacy/Licensing)

1. **User-Uploaded CVs**
   - **Reason:** Privacy constraints
   - **Mitigation:** Users upload CVs via Streamlit app for their own use; raw data is not stored or redistributed
   - **Alternative:** Synthetic benchmark dataset provided for validation

2. **External Datasets**
   - **Reason:** None used
   - **Note:** This project does NOT use Kaggle datasets, GitHub datasets, or any third-party data sources

3. **Raw User Session Data**
   - **Reason:** Privacy
   - **What's shared instead:** Aggregated evaluation metrics from experiments

---

## Data Access

### How to Access the Data

**Option 1: Clone the Repository**

```bash
git clone <repository-url>
cd ats-cv-optimizer
```

All data is included in the `research_package/` directory.

**Option 2: Download Research Package Only**

```bash
# Navigate to research_package/
cd research_package/

# View dataset
cat benchmark_dataset_v1.json

# View evaluation results
cat experiments/cv_jd_eval_before_after_20251226_v01.csv
```

### Reproducing Results

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Load scoring configuration
# Configuration automatically loaded from research_package/configs/

# 3. Run benchmark scoring
python scripts/benchmark_scoring.py

# 4. Compare results
diff experiments/benchmark_scores.csv research_package/experiments/cv_jd_eval_before_after_20251226_v01.csv
```

---

## Dataset License

**Status:** **Definitive**  
**License:** **CC0 1.0 Universal**  
**Statement:** The dataset is released under the **CC0 1.0 Universal** public domain dedication.

> [!NOTE]
> The project (code and data) runs under the CC0 1.0 Universal license.

---

## External Dependencies

**External Datasets Required:** None  
**External APIs Required:** Gemini API (for CV rewriting; not required for scoring validation)  
**Data Download Required:** None

All necessary data for reproducibility is included in this repository.

---

## Privacy and Ethics

- **No real PII:** All benchmark CV/JD pairs are synthetically generated
- **User data not redistributed:** User-uploaded CVs are processed locally and not shared
- **IRB approval:** Not applicable (no human subjects research)
- **Ethical review:** Not required (synthetic data only)

See [`docs/ETHICS_STATEMENT.md`](./ETHICS_STATEMENT.md) for full details.

---

## Data Provenance

For complete provenance documentation, including:
- Source verification
- Collection methodology
- PII handling procedures
- Licensing details

See [`docs/dataset_provenance.md`](./dataset_provenance.md)

---

## Contact

For questions about data access or reproducibility, please contact the project maintainers.

**Last Updated:** 2025-12-29

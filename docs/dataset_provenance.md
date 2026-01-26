# Dataset Provenance Documentation

**Version:** 1.1  
**Last Updated:** 2025-12-29  
**Status:** Verified and Approved

---

## 1. Source

### Primary Data Source

**Type:** Synthetically generated benchmark dataset  
**Generation Method:** In-house programmatic creation  
**Generation Script:** [`benchmark_dataset.py`](../benchmark_dataset.py)

> [!IMPORTANT]
> This dataset is **NOT** sourced from Kaggle, GitHub, or any external platform. All CV-JD pairs are **synthetically generated** by this research project.

### AI-Generated Content Rights

**Generator:** ChatGPT (OpenAI)  
**Ownership:** The project authors explicitly affirm ownership of the generated synthetic outputs used in this dataset, in accordance with OpenAI's Terms of Use.  
**Input Constraints:** The prompts and inputs used for generation did **not** include any third-party copyrighted text or proprietary data.

### Provenance Metadata

To ensure reproducibility and transparency:

- **Generator Model:** OpenAI GPT-4 / GPT-3.5 (via ChatGPT interface)
- **Generation Date:** November 2025
- **Prompt Templates:** Located in [`modules/prompt_builder.py`](../modules/prompt_builder.py)
- **Randomness:** Manual review and selection was applied to generated outputs to ensure quality.
- **Script Version:** v1.0 (commit SHA: `initial`)

### Dataset Characteristics

- **Format:** JSON (Pydantic schema-based)
- **Schema:** `CVJDPair` and `BenchmarkDataset` models
- **Current Version:** 1.0 (created 2025-11-29)
- **Current Size:** 1 CV-JD pair
- **Target Size:** 50+ pairs across 5 domains (planned expansion)
- **Domains:** 
  - Software Engineering
  - Data Science
  - Marketing
  - Healthcare
  - Education

---

## 2. Collection Procedure

### Generation Methodology

**Collection Method:** Not applicable (no human data collection)  
**Generation Method:** AI-assisted synthetic text generation using ChatGPT/OpenAI

#### Process:

1. **Schema Definition**: Pydantic models define strict data structure
2. **AI-Assisted Content Generation**: CV and JD texts generated using ChatGPT (OpenAI) with human review and editing
3. **Domain Stratification**: Examples created across 5 professional domains
4. **Quality Labeling**: Match quality assigned based on keyword overlap
5. **Score Annotation**: Expected score ranges estimated manually
6. **Serialization**: Saved as `benchmark_dataset_v1.json`
7. **AI Tool Used**: ChatGPT (OpenAI) for generating realistic CV and JD text content

#### Reproducibility:

```bash
# Regenerate the dataset
python benchmark_dataset.py
# Output: research_package/benchmark_dataset_v1.json
```

---

## 3. Licensing and Terms

### Code License

**Status:** CC0 1.0 Universal  
**Current State:** LICENSE file exists in the repository root  

> [!NOTE]
> Project code is dedicated to the public domain under CC0 1.0 Universal.

### Dataset License

**Status:** **Definitive**  
**License:** **CC0 1.0 Universal**  
**Statement:** The dataset is released under the **CC0 1.0 Universal** public domain dedication. You can copy, modify, distribute, and perform the work, even for commercial purposes, all without asking permission.  
**Constraints:** None (no third-party data dependencies)

### Third-Party Dependencies

**External Datasets:** None  
**Data Sources:** None  
**Licensing Constraints:** None

---

## 4. PII Handling and Anonymization

### Synthetic Benchmark Data

**PII Status:** No real PII exists in the benchmark dataset

All personally identifiable information in `benchmark_dataset_v1.json` is **fabricated**:
- Names generated programmatically by developers
- Email addresses are fake (e.g., alex@email.com)
- Phone numbers are fabricated
- Locations are generic
- Companies are fictional or anonymized

**Privacy Risk:** None (data is entirely synthetic)

### User-Uploaded Data (Streamlit App)

When users upload real CVs through the Streamlit application, PII is handled via the [`PIIRedactor`](../modules/pii_redactor.py) module.

#### PIIRedactor Capabilities:

**Detection and Redaction:**
- **NAME**: Regex pattern matching + first-line heuristics
- **EMAIL**: Email regex pattern (`[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}`)
- **PHONE**: Phone number patterns (various formats)
- **LOCATION**: City/state information

**Anonymization Method:**
- **Library:** Faker (Python library for generating fake data)
- **Seed:** Deterministic seed (42) for reproducible anonymization
- **Replacement:** Original PII replaced with plausible fake values

**Example:**
```python
from modules.pii_redactor import PIIRedactor

redactor = PIIRedactor(seed=42)
anonymized_text, redaction_map = redactor.redact_cv_text(cv_text)
```

### Privacy Mitigation Measures

1. **User-uploaded CVs are NOT redistributed**
   - Raw user data stays local or in user session
   - Only aggregated evaluation metrics are exported

2. **Evaluation CSVs contain aggregated data**
   - Example: `cv_jd_eval_before_after_20251226_v01.csv`
   - Contains scores, not raw CV/JD texts
   - Pair IDs are anonymized (e.g., `132126ed`, `bc7e3947`)

3. **Research package excludes user data**
   - Only synthetic benchmark pairs are included
   - No user-uploaded CVs in `research_package/`

4. **Redaction mapping is reversible** (for internal use only)
   - `RedactionMap` stores original ↔ anonymized mappings
   - Maps are NOT shared publicly
   - Used only for internal validation

---

## 5. Data Availability

See [`docs/data_availability.md`](./data_availability.md) for detailed data access information.

**Summary:**
- ✅ Synthetic benchmark dataset: Included in `research_package/`
- ✅ Generation script: Included (`benchmark_dataset.py`)
- ✅ Evaluation results: Included (`research_package/experiments/`)
- ❌ User-uploaded CVs: NOT redistributed (privacy)

---

## 6. Ethics Statement

See [`docs/ETHICS_STATEMENT.md`](./ETHICS_STATEMENT.md) for full ethics documentation.

**Key Points:**
- No human subjects research
- No real PII in research dataset
- No IRB approval required
- User data not redistributed

---

## 7. Provenance Evidence

Supporting evidence and documentation:

- **Generation Script:** [`benchmark_dataset.py`](../benchmark_dataset.py)
- **Schema Definitions:** `CVJDPair`, `BenchmarkDataset` (Pydantic models)
- **PIIRedactor Module:** [`modules/pii_redactor.py`](../modules/pii_redactor.py)
- **Test Suite:** [`modules/_smoke_pii_redactor.py`](../modules/_smoke_pii_redactor.py)
- **Evidence Directory:** [`docs/provenance_evidence/`](./provenance_evidence/)

---

## 8. Provenance Checklist

| Criterion | Status | Evidence |
|-----------|--------|----------|
| **Source documented** | ✅ VERIFIED | Synthetic generation via `benchmark_dataset.py` |
| **Collection procedure** | ✅ VERIFIED | Programmatic schema-based creation |
| **Methodology reproducible** | ✅ VERIFIED | Full script provided |
| **Code license** | ✅ VERIFIED | CC0 1.0 Universal |
| **Dataset license** | ✅ VERIFIED | CC0 1.0 Universal |
| **External dependencies** | ✅ VERIFIED | None (no external datasets) |
| **PII (synthetic data)** | ✅ N/A | Fabricated data, no real PII |
| **PII (user data)** | ✅ VERIFIED | PIIRedactor module with Faker |
| **User data redistribution** | ✅ NOT REDISTRIBUTED | Only aggregated metrics shared |
| **Ethics approval** | ✅ N/A | No human subjects; no IRB needed |

---

## Contact

For questions about dataset provenance, contact the project maintainers.

**Last Verified:** 2025-12-29

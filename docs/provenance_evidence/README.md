# Provenance Evidence Directory

This directory contains supporting evidence and documentation for dataset provenance claims.

---

## Contents

### 1. Dataset Generation

**Primary Evidence:**
- Main script: [`../../benchmark_dataset.py`](file:///Users/kaushikkarmakar/Downloads/cv%20maker/cv%20maker%203%20suggestions%20working/ats-cv-optimizer/benchmark_dataset.py)
- Output: [`../../research_package/benchmark_dataset_v1.json`](file:///Users/kaushikkarmakar/Downloads/cv%20maker/cv%20maker%203%20suggestions%20working/ats-cv-optimizer/research_package/benchmark_dataset_v1.json)

**Schema Documentation:**

The dataset uses Pydantic models for strict schema enforcement:

```python
class CVJDPair(BaseModel):
    """Single CV-JD pair with metadata and annotations."""
    
    pair_id: str  # Unique identifier (e.g., 'swe_001')
    domain: str   # Domain category
    cv_text: str  # Fabricated CV text
    jd_text: str  # Fabricated JD text
    match_quality: str  # poor, fair, good, excellent
    expected_ats_range: List[float]
    expected_jobfit_range: List[float]
```

**Generation Process:**

1. Developer authors CV/JD text manually
2. `CVJDPair` object created with metadata
3. Added to `BenchmarkDataset` collection
4. Serialized to JSON via `dataset.save()`

---

### 2. PII Handling Evidence

**PIIRedactor Module:**
- Implementation: [`../../modules/pii_redactor.py`](file:///Users/kaushikkarmakar/Downloads/cv%20maker/cv%20maker%203%20suggestions%20working/ats-cv-optimizer/modules/pii_redactor.py)
- Test suite: [`../../modules/_smoke_pii_redactor.py`](file:///Users/kaushikkarmakar/Downloads/cv%20maker/cv%20maker%203%20suggestions%20working/ats-cv-optimizer/modules/_smoke_pii_redactor.py)
- Schema: [`../../modules/schemas.py`](file:///Users/kaushikkarmakar/Downloads/cv%20maker/cv%20maker%203%20suggestions%20working/ats-cv-optimizer/modules/schemas.py) (PIIEntity, RedactionMap, AnonymizedCV)

**Detection Capabilities:**
- EMAIL: Regex pattern `[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}`
- PHONE: Various phone number formats
- NAME: First-line heuristics + capitalization patterns
- LOCATION: City/state extraction

**Anonymization Method:**
- Library: Faker (Python package)
- Seed: Deterministic (42) for reproducibility
- Replacement: Plausible fake values

---

### 3. Dataset Characteristics

**Version:** 1.0  
**Created:** 2025-11-29T21:05:29.865721  
**Current Size:** 1 CV-JD pair  
**Target Size:** 50+ pairs (planned)

**Domains Covered:**
1. Software Engineering
2. Data Science
3. Marketing
4. Healthcare
5. Education

**Match Quality Distribution (Current):**
- Excellent: 1 pair
- Good: 0 pairs
- Fair: 0 pairs
- Poor: 0 pairs

**Examples of Synthetic Data:**

```text
Name: ALEX JOHNSON (fabricated)
Email: alex@email.com (fabricated)
Company: Tech Solutions Inc (fabricated)
LinkedIn: linkedin.com/in/alexj (fabricated)
```

---

### 4. Verification

**No External Data Sources:**

Run these checks to verify no external dependencies:

```bash
# Check for Kaggle references
grep -r "kaggle" ../../research_package/
# Expected: No results (or only in test files referring to Kaggle as an example skill)

# Check for external URLs in dataset
cat ../../research_package/benchmark_dataset_v1.json | grep -E "http|www\."
# Expected: Only fabricated URLs (linkedin.com/in/alexj)

# Verify dataset generation is reproducible
python ../../benchmark_dataset.py
diff ../../research_package/benchmark_dataset_v1.json <output-file>
# Expected: Identical (deterministic generation)
```

---

### 5. License Evidence

**Current State:** No LICENSE file exists in repository root

```bash
# Verify no LICENSE file
ls -la ../../LICENSE
# Expected: No such file or directory
```

**README Claims:**
- Main README: Does not explicitly claim a license
- Research package README: Claims "MIT License - See LICENSE file for details" (line 33)
- **Discrepancy:** README references non-existent LICENSE file

**Resolution Needed:**
- Add LICENSE file with chosen license (MIT, Apache 2.0, etc.)
- OR update README to state "License: Not specified"

---

### 6. Privacy Verification

**Benchmark Dataset PII Check:**

```bash
# Verify no real email domains in dataset
cat ../../research_package/benchmark_dataset_v1.json | grep -oE "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
# Expected: alex@email.com (fabricated generic email)

# Check for real phone numbers (none should exist)
cat ../../research_package/benchmark_dataset_v1.json | grep -oE "\+1[0-9]{10}"
# Expected: No results or fabricated formats
```

**Evaluation CSV PII Check:**

```bash
# Verify no raw CV text in evaluation results
head -20 ../../research_package/experiments/cv_jd_eval_before_after_20251226_v01.csv
# Expected: Only scores, IDs, metadata (no raw text)
```

---

## Provenance Claim Verification Checklist

| Claim | Evidence | Verification Method |
|-------|----------|---------------------|
| Dataset is synthetic | `benchmark_dataset.py` | Code review of generation script |
| No external data sources | Codebase search | `grep -r "kaggle\|huggingface\|github.com"` |
| PII is fabricated | Dataset inspection | Manual review of names/emails |
| PIIRedactor exists | Module files | Test suite execution |
| No LICENSE file | File system | `ls LICENSE` (returns not found) |
| Generation is reproducible | Script execution | Re-run and diff output |

---

## Supporting References

1. **Dataset Provenance:** [`../dataset_provenance.md`](file:///Users/kaushikkarmakar/Downloads/cv%20maker/cv%20maker%203%20suggestions%20working/ats-cv-optimizer/docs/dataset_provenance.md)
2. **Data Availability:** [`../data_availability.md`](file:///Users/kaushikkarmakar/Downloads/cv%20maker/cv%20maker%203%20suggestions%20working/ats-cv-optimizer/docs/data_availability.md)
3. **Ethics Statement:** [`../ETHICS_STATEMENT.md`](file:///Users/kaushikkarmakar/Downloads/cv%20maker/cv%20maker%203%20suggestions%20working/ats-cv-optimizer/docs/ETHICS_STATEMENT.md)

---

**Last Updated:** 2025-12-28

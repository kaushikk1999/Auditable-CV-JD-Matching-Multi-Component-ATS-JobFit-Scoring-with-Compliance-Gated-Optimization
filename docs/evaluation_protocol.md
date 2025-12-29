# Evaluation Protocol: EmbeddingCosine_After

This document outlines the handling of the `EmbeddingCosine_After` metric.

## 1. Computation
**Status:** Manual / Offline
`EmbeddingCosine_After` is computed offline as part of a manual evaluation workflow external to the repository; the repository codebase does not currently implement or export this column.

## 2. Missingness Causes
**Status:** Unknown / Unlogged
Missing values occur when `EmbeddingCosine_After` was not computed or not recorded during the offline evaluation step; no per-row failure reason is logged in the available artifacts.

## 3. Handling Rule
**Action:** Exclude missing rows for analyses involving EmbeddingCosine_After & report valid-N (no imputation).
For analyses that use `EmbeddingCosine_After`, rows with missing values are excluded from the aggregate computation, and the number of non-missing observations (valid-N) is reported. No imputation is performed.

*Scope:* This rule applies to any summary statistic or plot involving `EmbeddingCosine_After`; per-row values remain missing in the evaluation sheet.

## 4. Traceability & Representation
*   **Evaluation Sheet:** `research_package/experiments/cv_jd_eval_before_after_20251226_v01.csv` (last modified: 2025-12-28).
*   **Missing Value Representation:** Missing values are stored as **blank cells** (empty strings) in the evaluation sheet.

## 5. Evidence / References
*   **Source:** Manual protocol definition.
*   **Code Reference:** None (external process).

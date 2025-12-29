# Scoring Weights & Configuration Report

**Version:** 1.0  
**Configuration File:** `config/scoring_config.yaml`

---

## 1. ATS Score Weights (Total: 100%)
The **ATS Score** evaluates the parser-friendliness and keyword optimzation of the CV.

| Component | Weight | Description |
| :--- | :--- | :--- |
| **Lexical Coverage** | **30%** | Exact match percentage of JD keywords found in CV. |
| **TF-IDF Relevance** | **25%** | Weighted importance of matched keywords (rare keywords count more). |
| **TF-IDF Cosine Similarity** | **20%** | Overall semantic similarity between full CV and JD text. |
| **Fuzzy Coverage** | **15%** | Matches for misspelled or slightly varied keywords. |
| **Section Distribution** | **10%** | Quality of keyword placement across Summary, Skills, and Experience. |

---

## 2. Job-Compatibility (JobFit) Weights (Total: 100%)
The **JobFit Score** evaluates the semantic alignment of the candidate's experience and skills with the specific role.

| Component | Weight | Description |
| :--- | :--- | :--- |
| **Experience Alignment** | **35%** | Semantic match between CV impact bullets and JD responsibilities. |
| **Skills Alignment** | **25%** | Weighted match of Required (70%) and Preferred (30%) skills. |
| **Summary Similarity** | **20%** | Semantic alignment of the CV Professional Summary with Result Summary. |
| **Education Match** | **10%** | Verification of required degree levels. |
| **Domain Relevance** | **10%** | Semantic match of experience context with specific industry domain keywords. |

---

## 3. Score Thresholds (Bands)
Used to generate qualitative feedback and color-coded status indicators.

| Band Name | Range (Inclusive-Exclusive) | Interpretation |
| :--- | :--- | :--- |
| **Poor** | 0 - 50 | Significant gaps found. High risk of rejection. |
| **Medium** | 50 - 75 | Partial match. Needs optimization to pass strict filters. |
| **Strong** | 75 - 90 | Good match. Likely to pass initial screening. |
| **Excellent** | 90 - 100 | Ideal match. Highly optimized for this specific role. |

---

## 4. System Settings

### Models
- **Embedding Model:** `sentence-transformers/all-MiniLM-L6-v2`
- **Device:** `cpu`
- **Fuzzy Match Threshold:** `90.0` (Minimum similarity ratio to count as a fuzzy match)

### Pre-processing
- **Tokenization:** Lowercase, Remove Punctuation.
- **Stopwords:** Kept for TF-IDF calculations to preserve phrase context, removed for simple counts.

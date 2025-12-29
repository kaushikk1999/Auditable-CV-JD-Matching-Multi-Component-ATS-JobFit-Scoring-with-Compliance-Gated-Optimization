# Scoring Equations – Phase 5

## 1. ATS Score

The **ATS Score** measures how well a CV's keywords and structure align with the target JD for automated parsing and ranking systems.

### Components:

#### 1.1 Lexical Coverage (C_lex)
Exact keyword match recall.

Let:
- K_JD = set of keywords extracted from JD (required_skills + ats_keywords)
- K_CV = set of keywords extracted from CV (skills + experience terms)


C_lex = |K_JD ∩ K_CV| / |K_JD|
text

Range: [0, 1]

#### 1.2 Fuzzy Coverage (C_fuzzy)
Keywords matched with ≥90% string similarity (rapidfuzz).

Let:
- K_JD_unmatched = K_JD \ K_CV (keywords not exactly matched)
- For each k ∈ K_JD_unmatched, find best fuzzy match k' ∈ K_CV
- F = {k : max_similarity(k, K_CV) ≥ 0.90}


C_fuzzy = |F| / |K_JD_unmatched|
text

Range: [0, 1]

#### 1.3 TF-IDF Weighted Relevance (R_tfidf)
Importance-weighted keyword coverage.

Let:
- TF-IDF(k, JD) = term frequency-inverse document frequency of keyword k in JD
- w_k = TF-IDF(k, JD) / max(TF-IDF(*, JD))  (normalized importance weight)


R_tfidf = Σ_{k ∈ K_JD ∩ K_CV} w_k / Σ_{k ∈ K_JD} w_k
text

Range: [0, 1]

#### 1.4 TF-IDF Cosine Similarity (S_tfidfcos)
Two-document similarity baseline suitable for CV-JD pair comparison.

S_tfidfcos = cosine(TF-IDF(CV_text), TF-IDF(JD_text))

Normalized to [0, 1] via min-max scaling over benchmark dataset.

#### 1.5 Section Distribution Quality (Q_section)
Penalizes keyword concentration in a single section (e.g., skills only).

Let:
- K_summary, K_experience, K_skills = keywords found in each CV section
- Entropy H = -Σ p_i log(p_i), where p_i = |K_section_i| / |K_CV|


Q_section = H / log(3) (normalized by max entropy for 3 sections)
text

Range: [0, 1], higher is better (uniform distribution)

### Final ATS Score:


ATS = w1·C_lex + w2·C_fuzzy + w3·R_tfidf + w4·S_tfidfcos + w5·Q_section
text

Default weights (configurable):
- w1 = 0.30 (lexical coverage most critical)
- w2 = 0.15 (fuzzy fallback)
- w3 = 0.25 (importance-weighted)
- w4 = 0.20 (two-document similarity baseline)
- w5 = 0.10 (distribution quality)

Σ w_i = 1.0

**Range:** [0, 1], convert to [0, 100] for display.

---

## 2. Job-Compatibility Score

The **Job-Compatibility Score** measures semantic alignment between CV content and JD requirements using embeddings and structured field matching.

### Components:

#### 2.1 Summary Similarity (S_summary)
Cosine similarity between CV summary and JD role summary embeddings.


S_summary = cosine(embed(CV_summary), embed(JD_role_summary))
text

Range: [-1, 1], shift to [0, 1] via (S + 1) / 2

#### 2.2 Experience-Responsibility Alignment (A_exp)
Average maximum similarity between CV experience bullets and JD responsibilities.

Let:
- B = set of CV experience bullet embeddings
- R = set of JD responsibility embeddings

For each r ∈ R, find max similarity with bullets:
align(r) = max_{b ∈ B} cosine(b, r)
A_exp = (1/|R|) Σ_{r ∈ R} align(r)
text

Range: [0, 1]

#### 2.3 Skills Alignment (A_skills)
Weighted match rate for required vs. preferred skills.

Let:
- S_req = JD required skills
- S_pref = JD preferred skills
- S_CV = CV skills


A_skills = 0.7 · (|S_req ∩ S_CV| / |S_req|) + 0.3 · (|S_pref ∩ S_CV| / |S_pref|)
text

Range: [0, 1]

#### 2.4 Education Match (M_edu)
Binary/partial match for education requirements.


M_edu = 1.0 if CV degree level ≥ JD required degree level
0.5 if CV degree level = JD preferred degree level
0.0 otherwise
text

#### 2.5 Domain Relevance (D_domain)
Cosine similarity between average CV experience embeddings and JD domain keywords.


D_domain = cosine(mean(B), embed(JD_domain_keywords))
text

Range: [0, 1]

### Final Job-Compatibility Score:


JobFit = u1·S_summary + u2·A_exp + u3·A_skills + u4·M_edu + u5·D_domain
text

Default weights (configurable):
- u1 = 0.20 (summary alignment)
- u2 = 0.35 (experience-responsibility alignment most critical)
- u3 = 0.25 (skills match)
- u4 = 0.10 (education)
- u5 = 0.10 (domain relevance)

Σ u_i = 1.0

**Range:** [0, 1], convert to [0, 100] for display.

---

## 3. Score Interpretation Bands

| Score Range | Label      | Interpretation |
|-------------|------------|----------------|
| [0, 50)     | Poor       | Major gaps, requires significant rewriting |
| [50, 75)    | Medium     | Moderate alignment, targeted improvements needed |
| [75, 90)    | Strong     | Good match, minor refinements recommended |
| [90, 100]   | Excellent  | High alignment, minimal changes needed |

---

## 4. Reproducibility Protocol

- **TF-IDF:** scikit-learn 1.4.0, default parameters
- **Embeddings:** sentence-transformers 2.3.1, model='all-MiniLM-L6-v2' (frozen)
- **Fuzzy Matching:** rapidfuzz 3.6.1, scorer=fuzz.ratio
- **Random Seed:** 42 (for any stochastic preprocessing)
- **Tokenization:** lowercase, alphanumeric only, min_length=2
1.2 This document serves as the formal specification for implementation and will be referenced in research outputs.

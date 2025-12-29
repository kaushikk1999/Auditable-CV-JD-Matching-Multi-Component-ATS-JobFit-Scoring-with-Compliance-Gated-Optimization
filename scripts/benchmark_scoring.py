"""
Benchmark Scoring Script

Scores all CV-JD pairs in the benchmark dataset and exports results.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.scoring_pipeline import ScoringPipeline
from modules.storage import Storage
import pandas as pd
import json
from tqdm import tqdm

def load_benchmark_pairs(benchmark_dir: Path):
    """Load all CV-JD pairs from benchmark directory."""
    pairs = []
    
    # Assume structure: benchmark/cvs/*.json, benchmark/jds/*.json
    cv_dir = benchmark_dir / "cvs"
    jd_dir = benchmark_dir / "jds"
    
    if not cv_dir.exists() or not jd_dir.exists():
        print(f"Warning: Benchmark directories not found at {benchmark_dir}")
        return pairs
    
    cv_files = list(cv_dir.glob("*.json"))
    jd_files = list(jd_dir.glob("*.json"))
    
    # Create all combinations
    for cv_file in cv_files:
        for jd_file in jd_files:
            pairs.append({
                "cv_file": cv_file,
                "jd_file": jd_file,
                "cv_id": cv_file.stem,
                "jd_id": jd_file.stem
            })
    
    return pairs

def score_benchmark_dataset(benchmark_dir: Path, output_path: Path):
    """Score all pairs and export to CSV."""
    print("Loading benchmark pairs...")
    pairs = load_benchmark_pairs(benchmark_dir)
    
    if not pairs:
        print("No benchmark pairs found. Exiting.")
        return
    
    print(f"Found {len(pairs)} CV-JD pairs to score.")
    
    # Initialize pipeline
    pipeline = ScoringPipeline()
    
    # Score all pairs
    results = []
    
    for pair in tqdm(pairs, desc="Scoring pairs"):
        try:
            # Load CV
            with open(pair["cv_file"], 'r') as f:
                cv_data = json.load(f)
            cv_structured = cv_data.get("data", {})
            cv_raw = cv_data.get("raw_text", "")
            
            # Load JD
            with open(pair["jd_file"], 'r') as f:
                jd_data = json.load(f)
            jd_enhanced = jd_data.get("data", {})
            jd_raw = jd_data.get("raw_text", "")
            
            # Score
            report = pipeline.score_cv_jd_pair(
                cv_structured, jd_enhanced, cv_raw, jd_raw
            )
            
            # Extract results
            results.append({
                "cv_id": pair["cv_id"],
                "jd_id": pair["jd_id"],
                "ats_score": report["ats_score"],
                "jobfit_score": report["jobfit_score"],
                "ats_band": report["interpretation"]["ats_band"],
                "jobfit_band": report["interpretation"]["jobfit_band"],
                **{f"ats_{k}": v for k, v in report["ats_components"].items()},
                **{f"jobfit_{k}": v for k, v in report["jobfit_components"].items()}
            })
        
        except Exception as e:
            print(f"Error scoring {pair['cv_id']} × {pair['jd_id']}: {e}")
            continue
    
    # Convert to DataFrame
    df = pd.DataFrame(results)
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    print(f"\n✅ Saved results to {output_path}")
    
    # Print summary statistics
    print("\n=== Summary Statistics ===")
    print(f"Mean ATS Score: {df['ats_score'].mean():.2f}")
    print(f"Mean JobFit Score: {df['jobfit_score'].mean():.2f}")
    print(f"\nATS Band Distribution:")
    print(df['ats_band'].value_counts())
    print(f"\nJobFit Band Distribution:")
    print(df['jobfit_band'].value_counts())

if __name__ == "__main__":
    from config.settings import BASE_DIR
    
    benchmark_dir = BASE_DIR / "benchmark"
    output_path = BASE_DIR / "experiments" / "benchmark_scores.csv"
    output_path.parent.mkdir(exist_ok=True)
    
    score_benchmark_dataset(benchmark_dir, output_path)

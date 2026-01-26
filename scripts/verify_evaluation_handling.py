import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add project root to path to allow importing modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from modules.evaluation_utils import load_and_preprocess_evaluation_data, get_valid_embedding_cosine_stats

def verify_evaluation_handling():
    # Path to the evaluation CSV matches the one cited in the protocol
    csv_path = Path("research_package/experiments/cv_jd_eval_before_after_20251226_v01.csv")
    
    if not csv_path.exists():
        print(f"❌ Error: Evaluation CSV not found at {csv_path}")
        return

    print(f"Loading evaluation data from: {csv_path}")
    
    try:
        # Use centralized loader
        df = load_and_preprocess_evaluation_data(csv_path)
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return
    
    print("\n=== Debugging Columns (Fixed) ===")
    print(df.columns.tolist())
    
    if "EmbeddingCosine_After" not in df.columns:
        print("❌ Error: EmbeddingCosine_After column missing.")
        return

    print("\n=== EmbeddingCosine_After Head ===")
    print(df["EmbeddingCosine_After"].head(10))
    
    # 1. Check for Missing Values
    total_rows = len(df)
    missing_mask = df["EmbeddingCosine_After"].isna()
    missing_count = missing_mask.sum()
    valid_count_calc_here = total_rows - missing_count
    
    print("\n=== Missing Value analysis ===")
    print(f"Total Rows: {total_rows}")
    print(f"Missing EmbeddingCosine_After: {missing_count}")
    print(f"Valid EmbeddingCosine_After: {valid_count_calc_here}")
    
    # 2. Implement Policy: Exclude missing rows for aggregation
    print("\n=== Implementing Handling Policy (Exclude Missing) ===")
    
    valid_count, mean_score, valid_df = get_valid_embedding_cosine_stats(df)
    
    print(f"Aggregation (Mean of {valid_count} valid rows): {mean_score:.4f}")
    
    # Verify no NaNs in calculation (unless all were NaN, which returns NaN)
    if valid_count > 0 and np.isnan(mean_score):
         print("❌ Error: Mean calculation resulted in NaN (Handling broken)")
    elif valid_count == 0:
         print("⚠️ Warning: No valid rows found.")
    else:
         print("✅ Success: Mean calculated correctly ignoring missing values.")

if __name__ == "__main__":
    verify_evaluation_handling()

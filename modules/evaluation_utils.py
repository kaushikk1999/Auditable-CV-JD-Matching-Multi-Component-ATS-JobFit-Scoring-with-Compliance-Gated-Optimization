import pandas as pd
import numpy as np
from pathlib import Path
import logging

def load_and_preprocess_evaluation_data(csv_path: Path) -> pd.DataFrame:
    """
    Loads evaluation CSV and enforces missing value handling for EmbeddingCosine_After.
    
    POLICY:
    1. Read CSV.
    2. Coerce 'EmbeddingCosine_After' to numeric, turning errors/blanks into NaN.
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"Evaluation CSV not found at {csv_path}")

    # Load CSV - explicit index_col=False to prevent misalignment
    # standardizing na_values handling could also be done here, but coercing is safer for the specific column
    df = pd.read_csv(csv_path, index_col=False)
    
    # Enforce numeric coercion for EmbeddingCosine_After
    # This handles: "", " ", "NaN", "nan", "N/A", "any_string" -> NaN
    if "EmbeddingCosine_After" in df.columns:
        df["EmbeddingCosine_After"] = pd.to_numeric(df["EmbeddingCosine_After"], errors='coerce')
    else:
        logging.warning("Column 'EmbeddingCosine_After' not found in evaluation CSV.")

    return df

def get_valid_embedding_cosine_stats(df: pd.DataFrame):
    """
     returns (valid_count, mean_score, valid_df)
    """
    if "EmbeddingCosine_After" not in df.columns:
        return 0, np.nan, pd.DataFrame()

    missing_mask = df["EmbeddingCosine_After"].isna()
    valid_df = df[~missing_mask]
    valid_count = len(valid_df)
    
    if valid_count > 0:
        mean_score = valid_df["EmbeddingCosine_After"].mean()
    else:
        mean_score = np.nan
        
    return valid_count, mean_score, valid_df

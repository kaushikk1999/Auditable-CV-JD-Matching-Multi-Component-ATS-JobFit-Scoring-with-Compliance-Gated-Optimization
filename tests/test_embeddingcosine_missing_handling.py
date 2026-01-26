import sys
from pathlib import Path
import pytest
import pandas as pd
import numpy as np

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from modules.evaluation_utils import load_and_preprocess_evaluation_data, get_valid_embedding_cosine_stats

def test_embeddingcosine_missing_handling(tmp_path):
    # 1. Create a tiny inline CSV with mixed valid/invalid values
    csv_content = """id,EmbeddingCosine_After
1,0.9
2,
3, 
4,nan
5,NaN
6,text_value
7,0.1
"""
    csv_file = tmp_path / "test_eval.csv"
    csv_file.write_text(csv_content, encoding='utf-8')

    # 2. Load using the helper
    df = load_and_preprocess_evaluation_data(csv_file)

    # 3. Assertions on specific rows
    # Row 1: 0.9 -> 0.9
    assert df.loc[df['id'] == 1, 'EmbeddingCosine_After'].iloc[0] == 0.9
    
    # Row 2: "" -> NaN
    assert np.isnan(df.loc[df['id'] == 2, 'EmbeddingCosine_After'].iloc[0])
    
    # Row 3: " " -> NaN
    assert np.isnan(df.loc[df['id'] == 3, 'EmbeddingCosine_After'].iloc[0])
    
    # Row 4: "nan" -> NaN
    assert np.isnan(df.loc[df['id'] == 4, 'EmbeddingCosine_After'].iloc[0])

    # Row 6: "text_value" -> NaN
    assert np.isnan(df.loc[df['id'] == 6, 'EmbeddingCosine_After'].iloc[0])

    # Row 7: 0.1 -> 0.1
    assert df.loc[df['id'] == 7, 'EmbeddingCosine_After'].iloc[0] == 0.1

    # 4. Verify aggregation
    valid_count, mean_score, valid_df = get_valid_embedding_cosine_stats(df)
    
    # We expect 2 valid rows (id 1 and 7)
    assert valid_count == 2
    
    # Mean of 0.9 and 0.1 is 0.5
    assert np.isclose(mean_score, 0.5)
    
    # Verify valid_df contents
    assert len(valid_df) == 2
    assert set(valid_df['id']) == {1, 7}

    print("\n✅ Test Passed: Missing/Blank/Invalid values coerced to NaN, stats correct.")

"""
Package all research artifacts for reproducibility.

Creates a research_package/ folder with:
- Benchmark dataset (anonymized)
- Experiment logs
- Configuration snapshots
- Reproducibility documentation
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import BASE_DIR
import shutil
import json
from datetime import datetime

def package_artifacts():
    """Package all research artifacts."""
    
    package_dir = BASE_DIR / "research_package"
    package_dir.mkdir(exist_ok=True)
    
    print("Packaging research artifacts...")
    
    # 1. Copy benchmark dataset
    print("1. Copying benchmark dataset...")
    benchmark_src = BASE_DIR / "benchmark"
    benchmark_dst = package_dir / "benchmark"
    
    if benchmark_src.exists():
        shutil.copytree(benchmark_src, benchmark_dst, dirs_exist_ok=True)
        print(f"   ✓ Copied {len(list(benchmark_dst.rglob('*')))} files")
    
    # 2. Copy experiments logs
    print("2. Copying experiment logs...")
    experiments_src = BASE_DIR / "experiments"
    experiments_dst = package_dir / "experiments"
    
    if experiments_src.exists():
        shutil.copytree(experiments_src, experiments_dst, dirs_exist_ok=True)
        print(f"   ✓ Copied experiment runs")
    
    # 3. Copy configuration files
    print("3. Copying configurations...")
    config_dst = package_dir / "configs"
    config_dst.mkdir(exist_ok=True)
    
    config_files = [
        BASE_DIR / "config" / "scoring_config.yaml",
        BASE_DIR / "config" / "settings.py",
        BASE_DIR / "config" / "word_lists.py"
    ]
    
    for config_file in config_files:
        if config_file.exists():
            shutil.copy(config_file, config_dst / config_file.name)
    
    print(f"   ✓ Copied {len(list(config_dst.iterdir()))} config files")
    
    # 4. Copy scoring equations documentation
    print("4. Copying documentation...")
    docs_src = BASE_DIR / "docs"
    docs_dst = package_dir / "docs"
    
    if docs_src.exists():
        shutil.copytree(docs_src, docs_dst, dirs_exist_ok=True)
    
    # 5. Create reproducibility manifest
    print("5. Creating reproducibility manifest...")
    
    manifest = {
        "created_at": datetime.now().isoformat(),
        "project": "ATS CV Optimizer",
        "version": "1.0",
        "phases_completed": "1-7",
        "python_version": "3.12+",
        "key_dependencies": {
            "streamlit": "1.32.0",
            "sentence-transformers": "2.3.1",
            "scikit-learn": "1.4.0",
            "google-generativeai": "0.4.0"
        },
        "scoring_config": "configs/scoring_config.yaml",
        "benchmark_dataset": "benchmark/",
        "experiment_logs": "experiments/",
        "documentation": "docs/scoring_equations.md",
        "reproducibility_protocol": {
            "random_seed": 42,
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "deterministic": True
        }
    }
    
    manifest_path = package_dir / "REPRODUCIBILITY_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    
    print(f"   ✓ Manifest saved to {manifest_path}")
    
    # 6. Create README
    print("6. Creating README...")
    
    readme_content = """
# ATS CV Optimizer - Research Package

This package contains all artifacts needed to reproduce the ATS CV Optimizer results.

## Contents

- `benchmark/`: Anonymized CV-JD dataset (PII redacted)
- `experiments/`: Experiment run logs with scores and features
- `configs/`: Configuration files (weights, thresholds, word lists)
- `docs/`: Scoring equations and methodology
- `REPRODUCIBILITY_MANIFEST.json`: Environment and versioning details

## Reproducibility

1. Install dependencies: `pip install -r requirements.txt`
2. Load scoring config: `configs/scoring_config.yaml`
3. Run benchmark: `python scripts/benchmark_scoring.py`
4. Compare results with `experiments/benchmark_scores.csv`

## Citation

If you use this optimizer in your research, please cite:


ATS CV Optimizer v1.0 (2024)
7-Phase Pipeline for Job-Compatibility CV Optimization
Achieving 95+ ATS and Job-Compatibility Scores
text

## License

MIT License - See LICENSE file for details.
"""
    
    readme_path = package_dir / "README.md"
    readme_path.write_text(readme_content)
    
    print(f"   ✓ README created")
    
    # 7. Copy requirements
    print("7. Copying requirements...")
    req_src = BASE_DIR / "requirements.txt"
    if req_src.exists():
        shutil.copy(req_src, package_dir / "requirements.txt")
    
    print(f"\n✅ Research package created at: {package_dir}")
    print(f"   Total size: {sum(f.stat().st_size for f in package_dir.rglob('*') if f.is_file()) / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    package_artifacts()

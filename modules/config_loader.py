import yaml
from pathlib import Path
from config.scoring_schemas import ScoringConfig
from config.settings import BASE_DIR

def load_scoring_config(config_path: Path = None) -> ScoringConfig:
    """Load and validate scoring configuration."""
    if config_path is None:
        config_path = BASE_DIR / "config" / "scoring_config.yaml"
    
    with open(config_path, 'r') as f:
        config_dict = yaml.safe_load(f)
    
    # Validate with Pydantic
    config = ScoringConfig(**config_dict)
    return config

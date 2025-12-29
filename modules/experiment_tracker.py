import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from modules.schemas import RunConfig, RunMetrics, AnalysisReport
from config.settings import BASE_DIR

class ExperimentTracker:
    """Tracks analysis runs for reproducibility."""
    
    def __init__(self, experiments_dir: Optional[Path] = None):
        """
        Args:
            experiments_dir: Directory to store experiment runs
        """
        self.experiments_dir = experiments_dir or (BASE_DIR / "experiments")
        self.experiments_dir.mkdir(exist_ok=True)
    
    def start_run(self, cv_file: str, jd_file: str, parameters: Dict = None) -> str:
        """
        Initialize a new experiment run.
        
        Returns:
            run_id (UUID string)
        """
        run_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Create run directory
        run_dir = self.experiments_dir / run_id
        run_dir.mkdir(exist_ok=True)
        
        # Save run config
        config = RunConfig(
            run_id=run_id,
            timestamp=timestamp,
            cv_file=cv_file,
            jd_file=jd_file,
            parameters=parameters or {}
        )
        
        config_path = run_dir / "config.json"
        config_path.write_text(config.model_dump_json(indent=2))
        
        return run_id
    
    def log_analysis(self, run_id: str, analysis_report: AnalysisReport):
        """Save analysis report to run directory."""
        run_dir = self.experiments_dir / run_id
        if not run_dir.exists():
            raise ValueError(f"Run {run_id} not found")
        
        report_path = run_dir / "analysis_report.json"
        report_path.write_text(analysis_report.model_dump_json(indent=2))
    
    def log_metrics(self, run_id: str, metrics: RunMetrics):
        """Save metrics to run directory."""
        run_dir = self.experiments_dir / run_id
        if not run_dir.exists():
            raise ValueError(f"Run {run_id} not found")
        
        metrics_path = run_dir / "metrics.json"
        metrics_path.write_text(metrics.model_dump_json(indent=2))
    
    def log_artifact(self, run_id: str, artifact_name: str, content: Any):
        """Save arbitrary artifact (dict, list, string) to run directory."""
        run_dir = self.experiments_dir / run_id
        if not run_dir.exists():
            raise ValueError(f"Run {run_id} not found")
        
        artifact_path = run_dir / f"{artifact_name}.json"
        
        if isinstance(content, (dict, list)):
            artifact_path.write_text(json.dumps(content, indent=2))
        elif isinstance(content, str):
            artifact_path.write_text(content)
        else:
            artifact_path.write_text(json.dumps(str(content), indent=2))
    
    def get_run_config(self, run_id: str) -> RunConfig:
        """Load run configuration."""
        config_path = self.experiments_dir / run_id / "config.json"
        if not config_path.exists():
            raise FileNotFoundError(f"Config not found for run {run_id}")
        
        data = json.loads(config_path.read_text())
        return RunConfig(**data)
    
    def get_analysis_report(self, run_id: str) -> AnalysisReport:
        """Load analysis report."""
        report_path = self.experiments_dir / run_id / "analysis_report.json"
        if not report_path.exists():
            raise FileNotFoundError(f"Analysis report not found for run {run_id}")
        
        data = json.loads(report_path.read_text())
        return AnalysisReport(**data)
    
    def list_runs(self) -> list:
        """List all experiment runs."""
        runs = []
        for run_dir in self.experiments_dir.iterdir():
            if run_dir.is_dir():
                config_path = run_dir / "config.json"
                if config_path.exists():
                    config_data = json.loads(config_path.read_text())
                    runs.append({
                        "run_id": config_data["run_id"],
                        "timestamp": config_data["timestamp"],
                        "cv_file": config_data["cv_file"],
                        "jd_file": config_data["jd_file"]
                    })
        
        # Sort by timestamp (newest first)
        runs.sort(key=lambda x: x["timestamp"], reverse=True)
        return runs

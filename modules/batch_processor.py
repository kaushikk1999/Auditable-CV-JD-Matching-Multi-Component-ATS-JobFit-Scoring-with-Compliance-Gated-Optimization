import pandas as pd
from pathlib import Path
from typing import List, Dict
from modules.schemas import StructuredCV, EnhancedJD, AnalysisReport
from modules.gap_analyzer import KeywordGapAnalyzer, ExperienceAligner
from modules.pii_redactor import PIIRedactor
from modules.experiment_tracker import ExperimentTracker
from modules.storage import Storage
import time
import uuid

class BatchProcessor:
    """Process multiple CV-JD pairs for benchmarking and validation."""
    
    def __init__(self, tracker: ExperimentTracker):
        self.analyzer = KeywordGapAnalyzer()
        self.aligner = ExperienceAligner()
        self.redactor = PIIRedactor()
        self.tracker = tracker
    
    def process_pair(self, cv: StructuredCV, jd: EnhancedJD, 
                     cv_filename: str, jd_filename: str,
                     anonymize: bool = False) -> AnalysisReport:
        """
        Analyze a single CV-JD pair.
        
        Returns:
            AnalysisReport with gap analysis, alignments, and coverage table
        """
        start_time = time.time()
        
        # Perform gap analysis
        gap_analysis = self.analyzer.analyze(cv, jd)
        
        # Build coverage table
        coverage_table = self.analyzer.build_coverage_table(gap_analysis, jd)
        
        # Align experiences
        experience_alignments = self.aligner.align(cv, jd, gap_analysis)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            gap_analysis, experience_alignments, coverage_table
        )
        
        # Initialize run in tracker to create directory
        run_id = str(self.tracker.start_run(
            cv_file=cv_filename,
            jd_file=jd_filename,
            parameters={"anonymize": anonymize}
        ))
        
        # Create report
        report = AnalysisReport(
            run_id=run_id,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            cv_filename=cv_filename,
            jd_filename=jd_filename,
            gap_analysis=gap_analysis,
            experience_alignments=experience_alignments,
            keyword_coverage_table=coverage_table,
            recommendations=recommendations
        )
        
        processing_time = time.time() - start_time
        
        # Log to experiment tracker
        self.tracker.log_analysis(report.run_id, report)
        
        return report
    
    def process_batch(self, cv_jd_pairs: List[Dict]) -> pd.DataFrame:
        """
        Process multiple CV-JD pairs and return summary DataFrame.
        
        Args:
            cv_jd_pairs: List of dicts with keys "cv", "jd", "cv_file", "jd_file"
        
        Returns:
            DataFrame with summary statistics
        """
        results = []
        
        for idx, pair in enumerate(cv_jd_pairs):
            logging.info(f"Processing pair {idx+1}/{len(cv_jd_pairs)}...")
            
            report = self.process_pair(
                cv=pair["cv"],
                jd=pair["jd"],
                cv_filename=pair["cv_file"],
                jd_filename=pair["jd_file"]
            )
            
            # Extract summary stats
            stats = report.gap_analysis.coverage_stats
            results.append({
                "run_id": report.run_id,
                "cv_file": pair["cv_file"],
                "jd_file": pair["jd_file"],
                "overall_coverage": stats["overall_coverage"],
                "required_coverage": stats["required_coverage"],
                "preferred_coverage": stats["preferred_coverage"],
                "keywords_present": len(report.gap_analysis.present_keywords),
                "keywords_missing": len(report.gap_analysis.missing_keywords),
                "top_experience_relevance": report.experience_alignments[0].relevance_score if report.experience_alignments else 0.0
            })
        
        return pd.DataFrame(results)
    
    def _generate_recommendations(self, gap_analysis, alignments, coverage_table) -> List[str]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []
        
        # Coverage recommendations
        stats = gap_analysis.coverage_stats
        if stats["required_coverage"] < 0.8:
            recommendations.append(
                f"Critical: Only {stats['required_present']}/{stats['required_total']} required skills present. "
                f"Add missing required skills to skills section and experience bullets."
            )
        
        # Missing keyword recommendations
        high_priority_missing = [
            kw for kw in gap_analysis.missing_keywords 
            if kw.jd_priority == "required"
        ]
        if high_priority_missing:
            top_5 = [kw.keyword for kw in high_priority_missing[:5]]
            recommendations.append(
                f"Add these high-priority keywords: {', '.join(top_5)}"
            )
        
        # Experience relevance recommendations
        if alignments:
            low_relevance = [a for a in alignments if a.relevance_score < 0.3]
            if low_relevance:
                recommendations.append(
                    f"{len(low_relevance)} experience(s) have low relevance to target role. "
                    f"Consider condensing or removing to save space."
                )
        
        # Irrelevant keyword recommendations
        if len(gap_analysis.irrelevant_keywords) > 10:
            recommendations.append(
                f"{len(gap_analysis.irrelevant_keywords)} skills in CV are not relevant to JD. "
                f"Remove or replace with JD-aligned skills."
            )
        
        return recommendations

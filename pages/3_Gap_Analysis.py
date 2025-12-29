import streamlit as st
from modules.storage import Storage
from modules.gap_analyzer import KeywordGapAnalyzer, ExperienceAligner
from modules.experiment_tracker import ExperimentTracker
from modules.schemas import AnalysisReport, RunMetrics
import pandas as pd
import time

st.set_page_config(page_title="Phase 3: Gap Analysis", layout="wide")

st.title("🔍 Phase 3: Keyword Gap Analysis & Alignment")
st.markdown("**Day 3 Deliverable:** Identify keyword gaps and map CV to JD requirements")

# Initialize
if "analysis_report" not in st.session_state:
    st.session_state.analysis_report = None

tracker = ExperimentTracker()

# Check prerequisites
try:
    cv = Storage.load_structured_cv()
    jd = Storage.load_enhanced_jd()
except FileNotFoundError:
    st.error("⚠️ Please complete Phase 1 and Phase 2 first")
    st.stop()

# ===== ANALYSIS EXECUTION =====
st.header("🚀 Step 1: Run Gap Analysis")

col1, col2 = st.columns([2, 1])

with col1:
    fuzzy_threshold = st.slider(
        "Fuzzy Match Threshold (%)",
        min_value=70,
        max_value=100,
        value=80,
        help="Minimum similarity score for fuzzy keyword matching"
    )

with col2:
    if st.button("▶️ Analyze", type="primary", use_container_width=True):
        with st.spinner("Running keyword gap analysis..."):
            start_time = time.time()
            
            # Start experiment run
            run_id = tracker.start_run(
                cv_file="cv_structured.json",
                jd_file="jd_enhanced.json",
                parameters={"fuzzy_threshold": fuzzy_threshold}
            )
            
            # Run analysis
            analyzer = KeywordGapAnalyzer(fuzzy_threshold=fuzzy_threshold)
            gap_analysis = analyzer.analyze(cv, jd)
            coverage_table = analyzer.build_coverage_table(gap_analysis, jd)
            
            # Align experiences
            aligner = ExperienceAligner()
            alignments = aligner.align(cv, jd, gap_analysis)
            
            # Create report
            st.session_state.analysis_report = AnalysisReport(
                run_id=run_id,
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                cv_filename="cv_structured.json",
                jd_filename="jd_enhanced.json",
                gap_analysis=gap_analysis,
                experience_alignments=alignments,
                keyword_coverage_table=coverage_table,
                recommendations=[]
            )
            
            # Log metrics
            processing_time = time.time() - start_time
            metrics = RunMetrics(
                run_id=run_id,
                keyword_coverage=gap_analysis.coverage_stats["overall_coverage"],
                experience_alignment_avg=sum(a.relevance_score for a in alignments) / len(alignments) if alignments else 0,
                processing_time_seconds=processing_time,
                keywords_present=len(gap_analysis.present_keywords),
                keywords_missing=len(gap_analysis.missing_keywords)
            )
            tracker.log_metrics(run_id, metrics)
            tracker.log_analysis(run_id, st.session_state.analysis_report)
            
            # Save to storage
            Storage.save_analysis_report(st.session_state.analysis_report)
            
            st.success(f"✅ Analysis complete! (Run ID: {run_id[:8]}...)")
            st.info(f"Processing time: {processing_time:.2f}s")

st.divider()

# ===== DISPLAY RESULTS =====
if st.session_state.analysis_report:
    report = st.session_state.analysis_report
    gap = report.gap_analysis
    
    # Coverage Summary
    st.header("📊 Coverage Summary")
    col1, col2, col3 = st.columns(3)
    
    stats = gap.coverage_stats
    with col1:
        st.metric(
            "Overall Coverage",
            f"{stats['overall_coverage']:.1%}",
            help="Percentage of JD keywords found in CV"
        )
    with col2:
        st.metric(
            "Required Skills",
            f"{stats['required_present']}/{stats['required_total']}",
            help="Must-have skills present in CV"
        )
    with col3:
        st.metric(
            "Preferred Skills",
            f"{stats['preferred_present']}/{stats['preferred_total']}",
            help="Nice-to-have skills present in CV"
        )
    
    # Present Keywords
    with st.expander("✅ Present Keywords (Already in CV)", expanded=False):
        if gap.present_keywords:
            present_df = pd.DataFrame([
                {
                    "Keyword": kw.keyword,
                    "Priority": kw.jd_priority,
                    "Match Score": f"{kw.match_score:.1f}%",
                    "Locations": ", ".join(kw.cv_locations[:3]) + ("..." if len(kw.cv_locations) > 3 else "")
                }
                for kw in gap.present_keywords
            ])
            st.dataframe(present_df, use_container_width=True)
        else:
            st.info("No keywords found")
    
    # Missing Keywords
    with st.expander("❌ Missing Keywords (Need to Add)", expanded=True):
        if gap.missing_keywords:
            # Group by priority
            required_missing = [kw for kw in gap.missing_keywords if kw.jd_priority == "required"]
            preferred_missing = [kw for kw in gap.missing_keywords if kw.jd_priority == "preferred"]
            optional_missing = [kw for kw in gap.missing_keywords if kw.jd_priority == "optional"]
            
            if required_missing:
                st.markdown("**🔴 Required (High Priority)**")
                st.write(", ".join([kw.keyword for kw in required_missing]))
            
            if preferred_missing:
                st.markdown("**🟡 Preferred (Medium Priority)**")
                st.write(", ".join([kw.keyword for kw in preferred_missing]))
            
            if optional_missing:
                st.markdown("**🟢 Optional (Low Priority)**")
                st.write(", ".join([kw.keyword for kw in optional_missing[:10]]))
        else:
            st.success("All JD keywords are present in CV!")
    
    # Irrelevant Keywords
    with st.expander("🗑️ Irrelevant Keywords (Consider Removing)", expanded=False):
        if gap.irrelevant_keywords:
            st.caption(f"Found {len(gap.irrelevant_keywords)} skills in CV that are not in JD")
            st.write(", ".join(gap.irrelevant_keywords[:20]))
            if len(gap.irrelevant_keywords) > 20:
                st.caption(f"...and {len(gap.irrelevant_keywords) - 20} more")
        else:
            st.info("All CV skills are relevant to JD")
    
    st.divider()
    
    # Experience Alignment
    st.header("💼 Experience-to-JD Alignment")
    
    if report.experience_alignments:
        for alignment in report.experience_alignments:
            relevance_pct = alignment.relevance_score * 100
            
            # Color code by relevance
            if relevance_pct >= 70:
                color = "🟢"
            elif relevance_pct >= 40:
                color = "🟡"
            else:
                color = "🔴"
            
            with st.expander(
                f"{color} {alignment.job_title} at {alignment.company_name} — {relevance_pct:.0f}% relevant",
                expanded=(alignment.relevance_score >= 0.5)
            ):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Matched Keywords:**")
                    if alignment.matched_keywords:
                        st.write(", ".join(alignment.matched_keywords))
                    else:
                        st.caption("No keyword matches")
                
                with col2:
                    st.markdown("**Matched Responsibilities:**")
                    if alignment.matched_responsibilities:
                        for resp in alignment.matched_responsibilities[:3]:
                            st.caption(f"• {resp}")
                    else:
                        st.caption("No responsibility matches")
                
                # Bullet scores
                if alignment.bullet_scores:
                    st.markdown("**Bullet Relevance Scores:**")
                    bullet_df = pd.DataFrame({
                        "Bullet #": range(1, len(alignment.bullet_scores) + 1),
                        "Relevance": [f"{score:.2f}" for score in alignment.bullet_scores]
                    })
                    st.dataframe(bullet_df, use_container_width=True)
    
    st.divider()
    
    # Keyword Coverage Table
    st.header("📋 Keyword Coverage Table (Rewrite Guidance)")
    
    if report.keyword_coverage_table:
        coverage_df = pd.DataFrame([
            {
                "Keyword": entry.jd_keyword,
                "Category": entry.category,
                "Priority": entry.priority,
                "In CV?": "✅" if entry.present_in_cv else "❌",
                "Current Freq": entry.current_frequency,
                "Target Freq": entry.target_frequency,
                "Add To": ", ".join(entry.suggested_sections) if entry.suggested_sections else "—"
            }
            for entry in report.keyword_coverage_table
        ])
        
        st.dataframe(
            coverage_df,
            use_container_width=True,
            height=400
        )
        
        # Download button
        csv = coverage_df.to_csv(index=False)
        st.download_button(
            "📥 Download Coverage Table (CSV)",
            csv,
            "keyword_coverage_table.csv",
            "text/csv"
        )

# Footer
st.divider()
st.caption("Phase 3 Complete ✓ | Next: Compliance Rules Definition (Phase 4)")

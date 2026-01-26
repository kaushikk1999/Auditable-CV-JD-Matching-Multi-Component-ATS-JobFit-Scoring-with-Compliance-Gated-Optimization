import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from scipy import stats

CSV_PATH = Path("paper/tables/table1_results_preview.csv")
OUTPUT_PDF, OUTPUT_PNG = Path("figures/fig2_ats_jobfit_boxplots.pdf"), Path("figures/fig2_ats_jobfit_boxplots.png")

def main():
    if not CSV_PATH.exists(): raise FileNotFoundError(f"Missing {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    if len(df) != 10: print(f"WARNING: N={len(df)} (expected 10)")
    
    df["ATS_Delta"] = df["ATS_After"] - df["ATS_Before"]
    df["JobFit_Delta"] = df["JobFit_After"] - df["JobFit_Before"]

    print(f"\n=== STATISTICS (N={len(df)}) ===")
    for m in ["ATS", "JobFit"]:
        d, post, pre = df[f"{m}_Delta"], df[f"{m}_After"], df[f"{m}_Before"]
        stat, p = stats.ttest_rel(post, pre)
        print(f"{m:6} | Median: {d.median():+5.1f} | Mean: {d.mean():+5.1f} | Range: [{d.min():+5.1f}, {d.max():+5.1f}] | p={p:.4f}")

    ats_med, ats_p = df["ATS_Delta"].median(), stats.ttest_rel(df["ATS_After"], df["ATS_Before"]).pvalue
    print(f"\nVerif: ATS Med={ats_med:.1f} (Doc:11.6), p={ats_p:.3f} (Doc:0.018). JobFit Med={df['JobFit_Delta'].median():.1f} (Doc:+1.0)")

    # Plotting
    fig, axes = plt.subplots(1, 2, figsize=(8, 3.5))
    props = dict(linewidth=1.2, color='black')
    median = dict(linewidth=1.5, color='firebrick')

    for i, (m, ax) in enumerate(zip(["ATS", "JobFit"], axes)):
        data = [df[f"{m}_Before"], df[f"{m}_After"]]
        ax.boxplot(data, tick_labels=["Before", "After"], whis=(0, 100), 
                   boxprops=props, whiskerprops=props, capprops=props, medianprops=median)
        
        # Jitter & Connect
        x1, x2 = np.random.normal(1, 0.04, len(df)), np.random.normal(2, 0.04, len(df))
        ax.plot(x1, df[f"{m}_Before"], 'o', color='gray', alpha=0.5, ms=4)
        ax.plot(x2, df[f"{m}_After"], 'o', color='gray', alpha=0.5, ms=4)
        for j in range(len(df)): ax.plot([x1[j], x2[j]], [df[f"{m}_Before"][j], df[f"{m}_After"][j]], 'gray', alpha=0.3, lw=0.7)
        
        # Annotations
        delta, p = df[f"{m}_Delta"].median(), stats.ttest_rel(df[f"{m}_After"], df[f"{m}_Before"]).pvalue
        txt = f"Median $\Delta$={delta:+.1f}\n" + ("n.s." if p > 0.05 else f"$p$={p:.3f}")
        ax.text(0.5, 0.05, txt, transform=ax.transAxes, ha='center', fontsize=9, bbox=dict(facecolor='white', alpha=0.8, ec='none'))
        ax.set_title(f"{m} Score", fontsize=11); ax.set_ylim(0, 105)

    axes[0].set_ylabel("Score (0-100)")
    fig.suptitle("Fig. 2 ATS and JobFit scores before and after", fontsize=12, fontweight='bold')
    plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # Adjust rect to make room for suptitle at top
    OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(OUTPUT_PDF); plt.savefig(OUTPUT_PNG, dpi=300)
    print(f"\nSaved: {OUTPUT_PDF}, {OUTPUT_PNG}")

if __name__ == "__main__": main()

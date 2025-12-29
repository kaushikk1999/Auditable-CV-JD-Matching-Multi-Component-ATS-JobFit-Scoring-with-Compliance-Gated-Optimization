from typing import Dict, List

def build_ablation_rows(full_score_0_1: float, components_0_1: Dict[str, float], weights: Dict[str, float]) -> List[Dict]:
    """
    Helper to generate ablation study rows for a given score breakdown.
    
    Args:
        full_score_0_1: The total weighted score in [0, 1].
        components_0_1: Dictionary of raw component scores in [0, 1].
        weights: Dictionary of weights for each component.
        
    Returns:
        List of dicts containing 'component_removed', 'score_without_component', 'score_drop', 'weight_percent'.
    """
    rows = []
    for name, c in components_0_1.items():
        w = float(weights.get(name, 0.0))
        score_wo = full_score_0_1 - (w * float(c))
        drop = full_score_0_1 - score_wo  # == w*c
        rows.append({
            "component_removed": name,
            "score_without_component": score_wo * 100.0,
            "score_drop": drop * 100.0,
            "weight_percent": w * 100.0,
        })
    # optional: sort by impact desc like your PDF table
    rows.sort(key=lambda r: r["score_drop"], reverse=True)
    return rows

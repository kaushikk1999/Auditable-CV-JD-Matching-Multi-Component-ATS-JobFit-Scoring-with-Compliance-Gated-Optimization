"""
Generate Synthetic Compliance Audit Data.

This script simulates a large-scale audit of 500 CVs to generate distribution charts for:
1. Violation Frequency by Rule
2. Top 20 Violated Buzzwords
3. Pass-Rate by Domain/Level

It uses the actual rules and word lists from the codebase but mocks the "Audit Result" 
based on realistic probability distributions.
"""
import sys
import json
import random
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.word_lists import BANNED_TERMS

# Configuration
NUM_SAMPLES = 500
DOMAINS = ["Engineering", "Sales", "Marketing", "Product", "Operations", "Finance"]
LEVELS = ["Entry", "Mid-Level", "Senior", "Executive"]

RULES = [
    "Buzzword Audit",
    "Stopword Audit",
    "Word Uniqueness",
    "Duplicate Phrases",
    "Quantification Integrity",
    "Brevity Analysis",
    "Bullet Density"
]

# Probability of failure for each rule (0.0 - 1.0)
RULE_FAILURE_PROBS = {
    "Buzzword Audit": 0.65,        # Very common
    "Stopword Audit": 0.10,        # Rare (tools usually catch this)
    "Word Uniqueness": 0.30,       # Common (repetitive verbs)
    "Duplicate Phrases": 0.25,     # Common
    "Quantification Integrity": 0.70, # Very common (missing metrics)
    "Brevity Analysis": 0.40,      # Moderate (too long/short)
    "Bullet Density": 0.20         # Moderate
}

def generate_dataset():
    data = {
        "total_audits": NUM_SAMPLES,
        "rule_violations": Counter(),
        "buzzword_counts": Counter(),
        "pass_rates": {} # {Domain: {Level: {total: N, passed: N}}}
    }
    
    # Initialize pass_rates structure
    for d in DOMAINS:
        data["pass_rates"][d] = {}
        for l in LEVELS:
            data["pass_rates"][d][l] = {"total": 0, "passed": 0}
            
    for _ in range(NUM_SAMPLES):
        domain = random.choice(DOMAINS)
        level = random.choice(LEVELS)
        
        # Adjust probs based on level (Executives use more buzzwords, Entry use fewer metrics)
        probs = RULE_FAILURE_PROBS.copy()
        if level == "Executive":
            probs["Buzzword Audit"] += 0.15
            probs["Brevity Analysis"] += 0.10
        elif level == "Entry":
            probs["Quantification Integrity"] += 0.15
        
        cv_violations = []
        
        # 1. Check Rules
        for rule, prob in probs.items():
            if random.random() < prob:
                cv_violations.append(rule)
                data["rule_violations"][rule] += 1
                
                # If Buzzword Audit failed, pick random buzzwords
                if rule == "Buzzword Audit":
                    num_buzzwords = random.randint(1, 5)
                    # Weight selection slightly towards common ones
                    # We'll just pick randomly from the list for now
                    chosen = random.sample(BANNED_TERMS, num_buzzwords)
                    data["buzzword_counts"].update(chosen)
        
        # 2. Record Pass/Fail
        passed = len(cv_violations) == 0
        
        data["pass_rates"][domain][level]["total"] += 1
        if passed:
            data["pass_rates"][domain][level]["passed"] += 1

    return data

def main():
    dataset = generate_dataset()
    
    # Format for JSON output
    output = {
        "violation_frequency": dict(dataset["rule_violations"].most_common()),
        "top_buzzwords": dict(dataset["buzzword_counts"].most_common(20)),
        "cohort_pass_rates": []
    }
    
    # Flatten pass rates for easier charting
    for d, levels in dataset["pass_rates"].items():
        for l, stats in levels.items():
            rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            output["cohort_pass_rates"].append({
                "domain": d,
                "level": l,
                "pass_rate": round(rate, 1),
                "total_samples": stats["total"]
            })
            
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()

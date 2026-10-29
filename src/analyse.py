import pandas as pd
from sklearn.metrics import cohen_kappa_score
from judge import parse
import numpy as np

MECHANISMS = ["level_emr", "level_exr", "level_inr"]
CONDITIONS = ["A", "B"]


def load_results(mechanism, condition):
    """One row per item: rp_id, human_level, judge_rating."""
    raw = pd.read_json(f"data/raw_{condition}_{mechanism}.jsonl", lines=True)
    ratings = []
    for t in raw['text']:
        rating, reason = parse(t)
        ratings.append(rating)
    raw["judge_ratings"] = ratings
    full = pd.read_csv("data/sample.csv")
    mask = (full["split"] == 'evaluations') & (full["mechanism"] == mechanism)
    full = full[mask]
    merged = raw.merge(full[["level", "rp_id"]], on="rp_id", validate='one_to_one')

    return merged

def summarise(df):
    """Agreement statistics for one mechanism x condition."""
    n = len(df)
    tokens_in = df['input_tokens'].sum()
    failures = df["judge_ratings"].isna().sum()
    df = df.dropna(subset=["judge_ratings"])          
    exact = (df["judge_ratings"] == df["level"]).mean()           
    kappa = cohen_kappa_score(df["level"], df["judge_ratings"])           
    kappa_q = cohen_kappa_score(df["level"], df["judge_ratings"], weights='quadratic')         
       
    return {
        "n": n,
        "parse_failures": failures,
        "exact": exact,
        "kappa": kappa,
        "kappa_quadratic": kappa_q,
        "input_tokens": tokens_in,
    }

def load_paired(mechanism):
    """One row per item: level, judge rating in A, judge rating in B."""
    a = load_results(mechanism, "A")
    b = load_results(mechanism, "B")
    a = a[['rp_id', 'level', 'judge_ratings']]
    b = b[['rp_id', 'level', 'judge_ratings']]
    merged = a.merge(b, on=["rp_id", "level"], suffixes=("_A", "_B"), validate="one_to_one") 

    return merged

import numpy as np

def bootstrap_kappa_diff(paired, n_boot=1000, weights=None, seed=42):
    """95% CI for kappa_B - kappa_A, resampling items with replacement."""
    rng = np.random.default_rng(seed)      
    n = len(paired)
    diffs = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)        
        s = paired.iloc[idx]                 
        kappa_a = cohen_kappa_score(s["level"], s["judge_ratings_A"], weights=weights)
        kappa_b = cohen_kappa_score(s["level"], s["judge_ratings_B"], weights=weights)
        diffs.append(kappa_b - kappa_a)
    return np.percentile(diffs, [2.5, 97.5])
    
def main():
    rows = []
    for condition in CONDITIONS:
        for mechanism in MECHANISMS:
            df = load_results(mechanism, condition)
            stats = summarise(df)
            stats["mechanism"] = mechanism
            stats["condition"] = condition
            rows.append(stats)
            print(f"Confusion matrix condition {condition} and {mechanism}")
            print(pd.crosstab(df["level"], df["judge_ratings"]))
            confusion_m = pd.crosstab(df["level"], df["judge_ratings"])
            confusion_m.to_csv(f"results/confusion_matrix_{condition}_{mechanism}.csv")

    for mechanism in MECHANISMS:
        paired = load_paired(mechanism)
        for w in [None, "quadratic"]:
            kappa_a = cohen_kappa_score(paired["level"], paired["judge_ratings_A"], weights=w)
            kappa_b = cohen_kappa_score(paired["level"], paired["judge_ratings_B"], weights=w)
            observed = kappa_b - kappa_a
            low, high = bootstrap_kappa_diff(paired, weights=w)
            print(mechanism, w, round(observed, 3), round(low, 3), round(high, 3))

    summary = pd.DataFrame(rows)
    summary = summary.round(3)
    print(summary)
    summary.to_csv("results/summary.csv", index=False)

if __name__ == "__main__":
    main()
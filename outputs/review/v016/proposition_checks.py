"""Exploratory exact examples checking wording around Proposition 1; no project data."""
from itertools import combinations
import json
from pathlib import Path
import numpy as np

d = np.array([1., 1., 1., 1., 0.])
v = [float(d[list(s)].mean() - np.delete(d, list(s)).mean())
     for s in combinations(range(5), 1)]
result = {'additive_random_split': {'drifts': v, 'mean': float(np.mean(v)),
                                  'positive_share': float(np.mean(np.array(v) > 0))}}
y = np.array([0, 0, 0, 1, 1, 1])
early = np.array([.1, .4, .8, .2, .5, .9])
late = np.array([.8, .3, .1, .7, .6, .2])

def auc(scores, ids):
    a, labels = scores[ids], y[ids]
    return float((a[labels == 1, None] > a[labels == 0]).mean())

v = []
for s in combinations(range(6), 3):
    t, s = [i for i in range(6) if i not in s], list(s)
    if len(set(y[s])) < 2 or len(set(y[t])) < 2:
        continue  # condition symmetrically on both AUCs being defined
    v.append((auc(late, s) - auc(late, t)) - (auc(early, s) - auc(early, t)))
result['auc_equal_split'] = {'valid_splits': len(v), 'drifts': v, 'mean': float(np.mean(v))}
Path(__file__).with_suffix('.json').write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))

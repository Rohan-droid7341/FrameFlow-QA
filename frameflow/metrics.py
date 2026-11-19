import numpy as np
from typing import List, Dict

def compute_temporal_iou(seg_a: Dict[str, float], seg_b: Dict[str, float]) -> float:
    """Computes Intersection-over-Union (IoU) along the 1D temporal axis."""
    start_a, end_a = seg_a["start_time"], seg_a["end_time"]
    start_b, end_b = seg_b["start_time"], seg_b["end_time"]

    inter_start = max(start_a, start_b)
    inter_end = min(end_a, end_b)
    intersection = max(0.0, inter_end - inter_start)

    union = (end_a - start_a) + (end_b - start_b) - intersection
    if union <= 0:
        return 0.0
    return round(intersection / union, 4)

def calculate_cohens_kappa(annotator_labels_a: List[str], annotator_labels_b: List[str]) -> float:
    """Calculates Cohen's Kappa for inter-annotator agreement across categorical tags."""
    if len(annotator_labels_a) != len(annotator_labels_b) or not annotator_labels_a:
        return 0.0

    categories = list(set(annotator_labels_a) | set(annotator_labels_b))
    n = len(annotator_labels_a)

    # Observed agreement
    agreements = sum(1 for a, b in zip(annotator_labels_a, annotator_labels_b) if a == b)
    p_observed = agreements / n

    # Expected agreement by chance
    p_expected = 0.0
    for cat in categories:
        count_a = annotator_labels_a.count(cat)
        count_b = annotator_labels_b.count(cat)
        p_expected += (count_a / n) * (count_b / n)

    if p_expected == 1.0:
        return 1.0

    kappa = (p_observed - p_expected) / (1.0 - p_expected)
    return round(float(kappa), 4)

from __future__ import annotations

from collections import defaultdict

from rapidfuzz import fuzz


def _normalize_label(value: str) -> str:
    return value.strip().lower()


def detect_dirty_label_clusters(
    values: list[str],
    score_cutoff: int = 92,
    min_cluster_size: int = 2,
    max_unique_values: int = 200,
) -> dict:
    """
    Very lightweight fuzzy clustering for dirty categorical labels.

    Returns:
        {
            "dirty_label_cluster_flag": bool,
            "cluster_count": int,
            "largest_cluster_size": int,
            "cluster_examples": list[list[str]]
        }
    """
    cleaned = []
    seen = set()

    for v in values:
        if not isinstance(v, str):
            continue
        x = v.strip()
        if not x:
            continue
        if x not in seen:
            cleaned.append(x)
            seen.add(x)

    if len(cleaned) <= 1:
        return {
            "dirty_label_cluster_flag": False,
            "cluster_count": 0,
            "largest_cluster_size": 0,
            "cluster_examples": [],
        }

    if len(cleaned) > max_unique_values:
        return {
            "dirty_label_cluster_flag": False,
            "cluster_count": 0,
            "largest_cluster_size": 0,
            "cluster_examples": [],
        }

    assigned = set()
    clusters = []

    for i, label in enumerate(cleaned):
        if label in assigned:
            continue

        current_cluster = [label]
        assigned.add(label)
        norm_a = _normalize_label(label)

        for j in range(i + 1, len(cleaned)):
            candidate = cleaned[j]
            if candidate in assigned:
                continue

            norm_b = _normalize_label(candidate)

            # exact normalized match
            if norm_a == norm_b:
                current_cluster.append(candidate)
                assigned.add(candidate)
                continue

            score = fuzz.ratio(norm_a, norm_b)
            if score >= score_cutoff:
                current_cluster.append(candidate)
                assigned.add(candidate)

        if len(current_cluster) >= min_cluster_size:
            clusters.append(sorted(current_cluster))

    largest_cluster_size = max((len(c) for c in clusters), default=0)

    return {
        "dirty_label_cluster_flag": len(clusters) > 0,
        "cluster_count": len(clusters),
        "largest_cluster_size": largest_cluster_size,
        "cluster_examples": clusters[:5],
    }
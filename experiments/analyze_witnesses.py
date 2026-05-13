"""Analyze 1-NN separation witnesses.

This script provides analysis of the witness JSON produced by search_minimal_1nn.py.
"""

from __future__ import annotations

import json
import sys

# Add src to path for imports
sys.path.insert(0, "src")


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Analyze 1-NN separation witnesses")
    parser.add_argument(
        "witness_file",
        type=str,
        nargs="?",
        default="outputs/witnesses/1nn_separation_witnesses.json",
        help="Path to witness JSON file"
    )
    parser.add_argument(
        "--minimal",
        action="store_true",
        help="Show only minimal examples by vertex count"
    )
    parser.add_argument(
        "--max_vertices",
        type=int,
        help="Filter by maximum vertex count"
    )
    args = parser.parse_args()

    with open(args.witness_file) as f:
        data = json.load(f)

    witnesses = data["witnesses"]
    metadata = data["metadata"]

    print("=" * 60)
    print("1-NN LOO vs Replace-One Separation Witness Analysis")
    print("=" * 60)

    print("\n[Metadata]")
    for key, value in metadata.items():
        if key != "constraints":
            if isinstance(value, dict):
                print(f"  {key}:")
                for k, v in value.items():
                    print(f"    {k}: {v}")
            else:
                print(f"  {key}: {value}")

    print(f"\n[Statistics]")
    print(f"  Total witnesses: {len(witnesses)}")

    from collections import Counter

    # Group by vertex count
    by_vertices = Counter(w["num_vertices"] for w in witnesses)
    print(f"\n  Witnesses by vertex count:")
    for v in sorted(by_vertices.keys()):
        print(f"    v={v}: {by_vertices[v]}")

    # Group by edge count
    by_edges = Counter(w["num_edges"] for w in witnesses)
    print(f"\n  Witnesses by edge count:")
    for e in sorted(by_edges.keys()):
        print(f"    e={e}: {by_edges[e]}")

    # Group by gap
    by_gap = Counter(w["separation_gap"] for w in witnesses)
    print(f"\n  Witnesses by separation gap:")
    for g in sorted(by_gap.keys()):
        print(f"    gap={g}: {by_gap[g]}")

    # LOO and Replace-one distributions
    loo_dist = Counter(w["loo_max"] for w in witnesses)
    rep_dist = Counter(w["replace_max"] for w in witnesses)
    print(f"\n  LOO max distribution:")
    for v in sorted(loo_dist.keys()):
        print(f"    loo_max={v}: {loo_dist[v]}")
    print(f"\n  Replace-one max distribution:")
    for v in sorted(rep_dist.keys()):
        print(f"    replace_max={v}: {rep_dist[v]}")

    # Max gap found
    max_gap = max(w["separation_gap"] for w in witnesses)
    print(f"\n  Maximum separation gap: {max_gap}")

    # Filter if requested
    if args.max_vertices:
        witnesses = [w for w in witnesses if w["num_vertices"] <= args.max_vertices]
        print(f"\n  Filtered to v <= {args.max_vertices}: {len(witnesses)} witnesses")

    # Show minimal examples
    if args.minimal:
        print("\n[Minimal Examples]")
        seen_configs = set()
        minimal = []
        for w in witnesses:
            key = (w["num_vertices"], w["num_edges"], tuple(w["sample_order"]), tuple(w["labels"]))
            if key not in seen_configs:
                seen_configs.add(key)
                minimal.append(w)

        minimal.sort(key=lambda w: (w["num_vertices"], w["num_edges"]))

        from collections import defaultdict
        by_v = defaultdict(list)
        for w in minimal:
            by_v[w["num_vertices"]].append(w)

        for v in sorted(by_v.keys()):
            print(f"\n  v={v} vertices:")
            for w in by_v[v][:2]:  # First 2 per vertex count
                print(f"    edges={w['num_edges']}, order={w['sample_order']}, labels={w['labels']}")
                print(f"      loo_max={w['loo_max']}, replace_max={w['replace_max']}, gap={w['separation_gap']}")

        print(f"\n  Total unique minimal configs: {len(minimal)}")

    # Show first full witness
    print("\n[First Witness (full detail)]")
    print(json.dumps(witnesses[0], indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())

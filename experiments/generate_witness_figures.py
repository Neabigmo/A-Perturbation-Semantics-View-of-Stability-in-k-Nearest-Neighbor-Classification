"""Generate figures for witness examples.

This script produces PDF/SVG visualizations of minimal 1-NN separation witnesses.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
import math

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def layout_by_degree(adjacency):
    """Place a high-degree vertex in the center and remaining vertices on a circle."""
    vertices = sorted(int(k) for k in adjacency.keys())
    positions = {}
    
    # Find center (vertex with most neighbors)
    center = max(vertices, key=lambda v: len(adjacency[str(v)]))
    positions[center] = (0, 0)
    
    # Place leaves in circle
    leaves = [v for v in vertices if v != center]
    for i, leaf in enumerate(sorted(leaves)):
        angle = 2 * math.pi * i / len(leaves)
        positions[leaf] = (math.cos(angle), math.sin(angle))
    
    return positions, center


def draw_graph(ax, adjacency, positions, vertex_labels, sample_order, title="", center=None):
    """Draw a labeled graph with annotations."""
    import matplotlib.patches as mpatches
    import matplotlib.pyplot as plt
    
    # Colors
    label_colors = {0: "#4CAF50", 1: "#2196F3"}  # green for 0, blue for 1
    edge_color = "#333333"
    
    vertices = sorted(int(k) for k in adjacency.keys())
    
    # Draw edges
    for v in vertices:
        for neighbor in adjacency[str(v)]:
            neighbor = int(neighbor)
            if v < neighbor:  # Draw each edge once
                x = [positions[v][0], positions[neighbor][0]]
                y = [positions[v][1], positions[neighbor][1]]
                ax.plot(x, y, color=edge_color, linewidth=1.5, zorder=1)
    
    # Draw vertices
    for v in vertices:
        x, y = positions[v]
        color = label_colors[vertex_labels[v]]
        radius = 0.2 if v == center else 0.15
        
        circle = plt.Circle((x, y), radius, color=color, ec=edge_color, linewidth=2, zorder=2)
        ax.add_patch(circle)
        
        # Vertex label (index)
        ax.text(x, y, str(v), ha='center', va='center', fontsize=10, fontweight='bold', zorder=3)
        
        # Sample order annotation
        order_idx = sample_order.index(v)
        order_text = f"S{order_idx}"
        offset = 0.28 if v == center else 0.22
        ax.text(x, y - offset, order_text, ha='center', va='top', fontsize=8, color='#666666', zorder=3)
    
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(title, fontsize=11, pad=10)
    
    # Legend
    legend_elements = [
        mpatches.Patch(facecolor=label_colors[0], edgecolor='black', label='Label 0'),
        mpatches.Patch(facecolor=label_colors[1], edgecolor='black', label='Label 1'),
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=8)


def generate_figures(output_dir: Path) -> None:
    """Generate figures for minimal witnesses."""
    import matplotlib.pyplot as plt
    from collections import defaultdict
    
    # Load witness data
    with open(ROOT / "outputs/witnesses/1nn_separation_witnesses.json") as f:
        sep_data = json.load(f)
    
    witnesses = sep_data['witnesses']
    
    # Group by vertex count
    by_v = defaultdict(list)
    for w in witnesses:
        by_v[w['num_vertices']].append(w)
    
    # Generate one figure per vertex count showing minimal examples
    for v in sorted(by_v.keys()):
        examples = by_v[v]
        
        # Select examples covering different label configurations
        selected = []
        seen_labels = set()
        for w in examples:
            lbl = tuple(w['labels'])
            if lbl not in seen_labels:
                seen_labels.add(lbl)
                selected.append(w)
            if len(selected) >= 4:
                break
        
        if not selected:
            continue
        
        n_examples = len(selected)
        fig, axes = plt.subplots(1, n_examples, figsize=(4 * n_examples, 5))
        if n_examples == 1:
            axes = [axes]
        
        for ax, w in zip(axes, selected):
            positions, center = layout_by_degree(w['adjacency_list'])
            
            title = (f"v={w['num_vertices']}, e={w['num_edges']}\n"
                     f"order={w['sample_order']}\n"
                     f"labels={w['labels']}\n"
                     f"gap={w['separation_gap']}")
            
            draw_graph(ax, w['adjacency_list'], positions, w['labels'], w['sample_order'], title, center)
        
        fig.suptitle(f"1-NN Separation Witnesses (k=1), {v} vertices", fontsize=12, y=0.98)
        plt.tight_layout()
        
        # Save both PDF and SVG
        pdf_path = output_dir / f"witnesses_v{v}.pdf"
        svg_path = output_dir / f"witnesses_v{v}.svg"
        fig.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=150)
        fig.savefig(svg_path, format='svg', bbox_inches='tight')
        plt.close(fig)
        print(f"Saved: {pdf_path}, {svg_path}")
    
    # Generate combined overview figure
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    for ax, v in zip(axes, sorted(by_v.keys())):
        examples = by_v[v]
        # Pick the first example
        w = examples[0]
        
        positions, center = layout_by_degree(w['adjacency_list'])
        
        title = (f"v={v} (min)\norder={w['sample_order']}\nlabels={w['labels']}\n"
                 f"LOO={w['loo_max']}, Rep={w['replace_max']}, gap={w['separation_gap']}")
        
        draw_graph(ax, w['adjacency_list'], positions, w['labels'], w['sample_order'], title, center)
    
    fig.suptitle("Minimal 1-NN Separation Witnesses by Vertex Count", fontsize=14, y=0.98)
    plt.tight_layout()
    
    pdf_path = output_dir / "witnesses_overview.pdf"
    svg_path = output_dir / "witnesses_overview.svg"
    fig.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=150)
    fig.savefig(svg_path, format='svg', bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {pdf_path}, {svg_path}")


def main() -> int:
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate figures for 1-NN separation witnesses")
    parser.add_argument(
        "--output_dir",
        type=Path,
        default=ROOT / "outputs" / "figures",
        help="Output directory for figures"
    )
    args = parser.parse_args()
    
    args.output_dir.mkdir(parents=True, exist_ok=True)
    generate_figures(args.output_dir)
    
    print(f"\nFigures generated in: {args.output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

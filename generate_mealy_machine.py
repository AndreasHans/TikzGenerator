"""Generate TikZ Mealy machine diagrams."""

import argparse
import math
import sys
from collections import defaultdict
from typing import Dict, List, Tuple


def parse_transitions(raw: str) -> List[Tuple[int, int, str, str]]:
    """Parse transition specs: 'from,to,input,output;from,to,input,output;...'"""
    transitions: List[Tuple[int, int, str, str]] = []
    for entry in raw.split(";"):
        entry = entry.strip()
        if not entry:
            continue
        parts = [p.strip() for p in entry.split(",")]
        if len(parts) != 4:
            print(
                f"Error: each transition needs 4 parts (from,to,input,output), got: '{entry}'",
                file=sys.stderr,
            )
            sys.exit(1)
        src, dst = int(parts[0]), int(parts[1])
        transitions.append((src, dst, parts[2], parts[3]))
    return transitions


def render_tikz(
    num_states: int,
    transitions: List[Tuple[int, int, str, str]],
    colors: List[str],
    labels: List[str],
) -> str:
    """Render a Mealy machine as TikZ code."""
    lines: List[str] = []

    lines.append("\\begin{tikzpicture}[")
    lines.append("  >=Latex,")
    lines.append(
        "  state/.style={draw,circle,minimum size=10mm,inner sep=0pt,font=\\small},"
    )
    lines.append("  edge/.style={-Latex,thick},")
    lines.append("  label/.style={font=\\small},")
    lines.append("  node distance=25mm")
    lines.append("]")
    lines.append("")

    # Arrange states in a circle
    lines.append("% --- States")
    angle_step = 360.0 / num_states
    radius = max(1.5, num_states * 0.6)
    for i in range(num_states):
        angle = 90 - i * angle_step  # start at top, go clockwise
        x = radius * math.cos(math.radians(angle))
        y = radius * math.sin(math.radians(angle))
        opts = ["state"]
        if colors[i] == "red":
            opts.append("fill=red!20")
        elif colors[i] == "green":
            opts.append("fill=green!20")
        opts_str = ", ".join(opts)
        lines.append(f"\\node[{opts_str}] (s{i}) at ({x:.2f},{y:.2f}) {{{labels[i]}}};")

    # Draw initial state arrow
    lines.append("")
    lines.append("% --- Initial state")
    init_angle = 90 + angle_step * 0.0  # point toward s0 from outside
    ix = radius * math.cos(math.radians(90)) + 1.2
    iy = radius * math.sin(math.radians(90))
    lines.append(f"\\draw[edge] ({ix:.2f},{iy:.2f}) -- (s0);")

    lines.append("")
    lines.append("% --- Transitions")

    # Group transitions by (src, dst) to merge labels on same edge
    grouped: Dict[Tuple[int, int], List[str]] = defaultdict(list)
    for src, dst, inp, out in transitions:
        grouped[(src, dst)].append(f"{inp}/{out}")

    # Track which pairs have both directions for bend handling
    pair_set = set(grouped.keys())

    for (src, dst), labels in grouped.items():
        label_text = ", ".join(labels)
        if src == dst:
            # Self-loop
            # Pick a direction away from center
            angle = 90 - src * angle_step
            if abs(angle % 360 - 90) < 10:
                loop_dir = "above"
            elif abs(angle % 360 - 270) < 10 or abs(angle % 360 + 90) < 10:
                loop_dir = "below"
            elif (angle % 360) > 90 and (angle % 360) < 270:
                loop_dir = "left"
            else:
                loop_dir = "right"
            lines.append(
                f"\\draw[edge] (s{src}) edge[loop {loop_dir}]"
                f" node[label, {loop_dir}] {{${label_text}$}} (s{src});"
            )
        else:
            bend = ""
            if (dst, src) in pair_set:
                bend = "bend left=15, "
            lines.append(
                f"\\draw[edge] (s{src}) edge[{bend}]"
                f" node[label, midway, auto] {{${label_text}$}} (s{dst});"
            )

    lines.append("")
    lines.append("\\end{tikzpicture}")
    return "\n".join(lines)


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate TikZ Mealy machine diagrams"
    )
    parser.add_argument(
        "--states",
        required=True,
        type=int,
        help="Number of states (s0, s1, ...)",
    )
    parser.add_argument(
        "--transitions",
        required=True,
        type=str,
        help="Semicolon-separated transitions: 'from,to,input,output;...' "
        "e.g. '0,1,a,0;1,0,b,1;0,0,b,1'",
    )
    parser.add_argument(
        "--colors",
        required=False,
        type=str,
        help="Comma-separated state colors (white, red, green). Default: all white",
    )
    parser.add_argument(
        "--labels",
        required=False,
        type=str,
        help="Comma-separated state labels (e.g. '$s_0$,$s_1$,...'). "
        "Defaults to $s_0$, $s_1$, etc. Supports LaTeX math.",
    )
    parser.add_argument(
        "--output",
        "-o",
        required=False,
        type=str,
        help="Output file name. Default: mealy_machine_{states}.txt",
    )
    args = parser.parse_args()

    if args.states < 1:
        print("Error: --states must be at least 1.", file=sys.stderr)
        sys.exit(1)

    transitions = parse_transitions(args.transitions)

    # Validate state ids
    for src, dst, inp, out in transitions:
        for sid in (src, dst):
            if sid < 0 or sid >= args.states:
                print(
                    f"Error: state {sid} out of range [0, {args.states - 1}].",
                    file=sys.stderr,
                )
                sys.exit(1)

    # Parse and validate colors
    valid_colors = {"white", "red", "green"}
    if args.colors:
        color_list = [c.strip() for c in args.colors.split(",")]
        invalid = [c for c in color_list if c not in valid_colors]
        if invalid:
            print(
                f"Error: invalid color(s): {', '.join(invalid)}. "
                f"Valid colors are: white, red, green.",
                file=sys.stderr,
            )
            sys.exit(1)
        if len(color_list) != args.states:
            print(
                f"Error: expected {args.states} colors, got {len(color_list)}.",
                file=sys.stderr,
            )
            sys.exit(1)
    else:
        color_list = ["white"] * args.states

    # Parse and validate labels
    if args.labels:
        label_list = [l.strip() for l in args.labels.split(",")]
        if len(label_list) != args.states:
            print(
                f"Error: expected {args.states} labels, got {len(label_list)}.",
                file=sys.stderr,
            )
            sys.exit(1)
    else:
        label_list = [f"$s_{i}$" for i in range(args.states)]

    tikz_code = render_tikz(args.states, transitions, color_list, label_list)
    filename = args.output if args.output else f"mealy_machine_{args.states}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(tikz_code)
    print(f"Wrote {filename}")


if __name__ == "__main__":
    main()

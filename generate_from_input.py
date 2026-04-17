"""Generate state machine and Mealy machine TikZ diagrams from an input spec."""

import argparse
import re
import subprocess
import sys
from pathlib import Path


def compute_state_count(topo_type: str, size: int) -> int:
    if topo_type == "Line":
        return size
    elif topo_type == "Grid":
        return size * size
    elif topo_type == "Maze":
        return size + 3 * (size // 2)
    else:
        print(f"Error: unknown topology type '{topo_type}'.", file=sys.stderr)
        sys.exit(1)


def parse_input(filepath: str):
    headers = {}
    y_states = set()
    thetas = []  # (c, observation, action)
    deltas = []  # (c, observation, c')

    with open(filepath, "r", encoding="utf-8") as f:
        for line_num, raw_line in enumerate(f, 1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            # key=value headers
            if "=" in line and not line.startswith("y(") and not line.startswith("theta(") and not line.startswith("delta("):
                key, _, value = line.partition("=")
                headers[key.strip()] = value.strip()
                continue

            # y(s)
            m = re.match(r"^y\((\d+)\)$", line)
            if m:
                y_states.add(int(m.group(1)))
                continue

            # theta(c,o,a)
            m = re.match(r"^theta\((\d+),([^,]+),([^)]+)\)$", line)
            if m:
                thetas.append((int(m.group(1)), m.group(2).strip(), m.group(3).strip()))
                continue

            # delta(c,o,c')
            m = re.match(r"^delta\((\d+),\s*([^,]+?)\s*,\s*(\d+)\)$", line)
            if m:
                deltas.append((int(m.group(1)), m.group(2).strip(), int(m.group(3))))
                continue

            print(f"Warning: ignoring unrecognized line {line_num}: {line}", file=sys.stderr)

    # Validate required headers
    for key in ("type", "size", "goal", "memory"):
        if key not in headers:
            print(f"Error: missing required header '{key}'.", file=sys.stderr)
            sys.exit(1)

    topo_type = headers["type"]
    size = int(headers["size"])
    goal = int(headers["goal"])
    memory = int(headers["memory"])

    # Validate
    state_count = compute_state_count(topo_type, size)
    if goal < 0 or goal >= state_count:
        print(f"Error: goal state {goal} out of range [0, {state_count - 1}].", file=sys.stderr)
        sys.exit(1)
    for s in y_states:
        if s < 0 or s >= state_count:
            print(f"Error: y state {s} out of range [0, {state_count - 1}].", file=sys.stderr)
            sys.exit(1)
    for c, o, a in thetas:
        if c < 0 or c >= memory:
            print(f"Error: theta memory state {c} out of range [0, {memory - 1}].", file=sys.stderr)
            sys.exit(1)
    for c, o, cp in deltas:
        if c < 0 or c >= memory:
            print(f"Error: delta source {c} out of range [0, {memory - 1}].", file=sys.stderr)
            sys.exit(1)
        if cp < 0 or cp >= memory:
            print(f"Error: delta target {cp} out of range [0, {memory - 1}].", file=sys.stderr)
            sys.exit(1)

    return topo_type, size, goal, memory, state_count, y_states, thetas, deltas


def build_colors(state_count: int, goal: int, y_states: set) -> str:
    colors = ["white"] * state_count
    colors[goal] = "green"
    for s in y_states:
        colors[s] = "red"
    return ",".join(colors)


def build_transitions(thetas, deltas) -> str:
    # Index theta by (c, o) -> action
    theta_map = {}
    for c, o, a in thetas:
        theta_map[(c, o)] = a

    # Index delta by (c, o) -> c'
    delta_map = {}
    for c, o, cp in deltas:
        delta_map[(c, o)] = cp

    # Join on (c, o)
    transitions = []
    all_keys = set(theta_map.keys()) | set(delta_map.keys())
    for c, o in sorted(all_keys):
        if (c, o) not in theta_map:
            print(f"Warning: delta({c},{o},...) has no matching theta.", file=sys.stderr)
            continue
        if (c, o) not in delta_map:
            print(f"Warning: theta({c},{o},...) has no matching delta.", file=sys.stderr)
            continue
        a = theta_map[(c, o)]
        cp = delta_map[(c, o)]
        transitions.append(f"{c},{cp},{o},{a}")

    return ";".join(transitions)


def build_labels(memory: int) -> str:
    labels = []
    for i in range(memory):
        if i < 10:
            labels.append(f"$c_{i}$")
        else:
            labels.append(f"$c_{{{i}}}$")
    return ",".join(labels)


def main():
    parser = argparse.ArgumentParser(description="Generate TikZ diagrams from input spec")
    parser.add_argument("input", nargs="?", default="input.txt", help="Input file (default: input.txt)")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent

    topo_type, size, goal, memory, state_count, y_states, thetas, deltas = parse_input(args.input)

    # Step 2: Generate state machine
    colors = build_colors(state_count, goal, y_states)
    sm_cmd = [
        sys.executable,
        str(script_dir / "generate_state_machine.py"),
        "--type", topo_type,
        "--size", str(size),
        "--no-self-loops",
        "--colors", colors,
    ]
    print(f"Running: {' '.join(sm_cmd)}")
    result = subprocess.run(sm_cmd, cwd=str(script_dir))
    if result.returncode != 0:
        print("Error: generate_state_machine.py failed.", file=sys.stderr)
        sys.exit(1)

    # Step 3: Generate Mealy machine
    transitions = build_transitions(thetas, deltas)
    labels = build_labels(memory)
    mm_file = f"mealy_machine_{memory}.txt"
    mm_cmd = [
        sys.executable,
        str(script_dir / "generate_mealy_machine.py"),
        "--states", str(memory),
        "--transitions", transitions,
        "--labels", labels,
        "--output", mm_file,
    ]
    print(f"Running: {' '.join(mm_cmd)}")
    result = subprocess.run(mm_cmd, cwd=str(script_dir))
    if result.returncode != 0:
        print("Error: generate_mealy_machine.py failed.", file=sys.stderr)
        sys.exit(1)

    # Step 4: Combine into a single figure
    sm_file = f"state_machine_{topo_type}_{size}.txt"
    combined_file = f"combined_{topo_type}_{size}.txt"
    combine_figures(script_dir / sm_file, script_dir / mm_file, script_dir / combined_file, topo_type, size)


def _compute_column_count(topo_type: str, size: int) -> int:
    """Compute number of columns (horizontal extent) of the state machine."""
    if topo_type == "Line":
        return size
    elif topo_type == "Grid":
        return size
    elif topo_type == "Maze":
        return size
    else:
        return size


def combine_figures(sm_path: Path, mm_path: Path, out_path: Path, topo_type: str = "Line", size: int = 1) -> None:
    """Combine state machine and Mealy machine into a single tikzpicture."""
    sm_text = sm_path.read_text(encoding="utf-8")
    mm_text = mm_path.read_text(encoding="utf-8")

    # Extract body from both (strip tikzpicture wrapper and preamble)
    sm_body = _strip_tikz_wrapper(sm_text)
    mm_body = _strip_tikz_wrapper(mm_text)

    # Prefix Mealy machine node names to avoid conflicts (s0 -> m0, etc.)
    mm_body = _prefix_nodes(mm_body, "m")

    # Build combined tikzpicture with shared preamble
    lines = []
    lines.append("\\begin{tikzpicture}[")
    lines.append("  scale=0.65,")
    lines.append("  transform shape,")
    lines.append("  >=Latex,")
    lines.append("  state/.style={draw,circle,minimum size=5mm,inner sep=0pt,font=\\scriptsize},")
    lines.append("  edge/.style={-Latex,thin},")
    lines.append("  action/.style={font=\\tiny},")
    lines.append("  label/.style={font=\\tiny},")
    lines.append("  node distance=7mm")
    lines.append("]")
    lines.append("")
    lines.append("% === State Machine ===")
    lines.append(sm_body)
    lines.append("")
    lines.append("% === Mealy Machine ===")
    # Place Mealy machine to the right of the state machine
    # Use column count (horizontal extent) rather than total node count
    col_count = _compute_column_count(topo_type, size)
    xshift = col_count * 1.0 + 6.0  # extra padding
    # Vertically center the Mealy machine relative to the state machine
    # Rows are separated by node_distance=7mm=0.7cm, going downward
    if topo_type == "Line":
        row_count = 1
    elif topo_type == "Grid":
        row_count = size
    else:  # Maze
        row_count = 1 + size // 2
    yshift = -(row_count - 1) * 0.7 / 2  # center offset in cm
    lines.append(f"\\begin{{scope}}[xshift={xshift:.1f}cm, yshift={yshift:.2f}cm]")
    lines.append(mm_body)
    lines.append("\\end{scope}")
    lines.append("")
    lines.append("\\end{tikzpicture}")

    combined = "\n".join(lines)
    out_path.write_text(combined, encoding="utf-8")
    print(f"Wrote {out_path.name}")


def _strip_tikz_wrapper(text: str) -> str:
    """Remove \\begin{tikzpicture}[...] preamble and \\end{tikzpicture} from TikZ code."""
    lines = text.splitlines()
    # Find end of preamble (the line after the closing ])
    start = 0
    for i, line in enumerate(lines):
        if line.strip() == "]":
            start = i + 1
            break
    # Find end marker
    end = len(lines)
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == "\\end{tikzpicture}":
            end = i
            break
    # Strip leading blank lines from body
    body_lines = lines[start:end]
    while body_lines and not body_lines[0].strip():
        body_lines.pop(0)
    while body_lines and not body_lines[-1].strip():
        body_lines.pop()
    return "\n".join(body_lines)


def _prefix_nodes(text: str, prefix: str) -> str:
    """Replace node references (sN) with prefixed versions (e.g. mN)."""
    # Replace node definitions and references: (sN) -> (mN), and coordinate refs
    text = re.sub(r'\(s(\d+)\)', rf'({prefix}\1)', text)
    # Replace 'of sN' placement references
    text = re.sub(r'of s(\d+)', rf'of {prefix}\1', text)
    return text


if __name__ == "__main__":
    main()

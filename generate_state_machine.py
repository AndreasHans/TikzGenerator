"""Generate TikZ state machine diagrams from a topology specification."""

import argparse
import math
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class State:
    """A single state in the state machine."""

    id: int
    row: int
    col: int
    is_left_edge: bool = False
    is_right_edge: bool = False
    color: str = "white"
    label: Optional[str] = None
    self_loop_direction: Optional[str] = None
    section_comment: Optional[str] = None
    placement: Optional[str] = None


@dataclass
class Topology:
    """The full graph structure for rendering."""

    type: str
    size: int
    states: List[State] = field(default_factory=list)
    edges: List[Tuple[int, int]] = field(default_factory=list)
    edge_sections: List[Tuple[str, List[Tuple[int, int]]]] = field(
        default_factory=list
    )


def build_line_topology(size: int, colors: List[str]) -> Topology:
    """Build a Line topology of the given size."""
    states: List[State] = []
    edges: List[Tuple[int, int]] = []

    for i in range(size):
        placement = None
        if i > 0:
            placement = f"right=of s{i - 1}"

        self_loop = None
        if i == 0:
            self_loop = "left"
        elif i == size - 1:
            self_loop = "right"

        states.append(
            State(
                id=i,
                row=0,
                col=i,
                is_left_edge=(i == 0),
                is_right_edge=(i == size - 1),
                color=colors[i],
                self_loop_direction=self_loop,
                placement=placement,
            )
        )

    # Bidirectional edges between consecutive states
    for i in range(size - 1):
        edges.append((i, i + 1))
        edges.append((i + 1, i))

    return Topology(type="Line", size=size, states=states, edges=edges)


def build_grid_topology(size: int, colors: List[str]) -> Topology:
    """Build a Grid topology of the given size."""
    states: List[State] = []
    horizontal_edges: List[Tuple[int, int]] = []
    vertical_edges: List[Tuple[int, int]] = []

    for row in range(size):
        for col in range(size):
            sid = row * size + col

            # Placement
            if row == 0 and col == 0:
                placement = None
            elif col == 0:
                placement = f"below=of s{(row - 1) * size + col}"
            else:
                placement = f"right=of s{sid - 1}"

            # Section comment
            section_comment = f"States (row {row})"

            # Self-loop direction for perimeter states
            self_loop = None
            if row == 0:
                self_loop = "above"
            elif row == size - 1:
                self_loop = "below"
            elif col == 0:
                self_loop = "left"
            elif col == size - 1:
                self_loop = "right"

            states.append(
                State(
                    id=sid,
                    row=row,
                    col=col,
                    is_left_edge=(col == 0),
                    is_right_edge=(col == size - 1),
                    color=colors[sid],
                    self_loop_direction=self_loop,
                    section_comment=section_comment,
                    placement=placement,
                )
            )

    # Horizontal edges
    for row in range(size):
        for col in range(size - 1):
            a = row * size + col
            b = a + 1
            horizontal_edges.append((a, b))
            horizontal_edges.append((b, a))

    # Vertical edges (row-pair by row-pair, columns left to right)
    for row in range(size - 1):
        for col in range(size):
            a = row * size + col
            b = (row + 1) * size + col
            vertical_edges.append((a, b))
            vertical_edges.append((b, a))

    all_edges = horizontal_edges + vertical_edges
    edge_sections = [
        ("Horizontal transitions", horizontal_edges),
        ("Vertical transitions", vertical_edges),
    ]

    return Topology(
        type="Grid",
        size=size,
        states=states,
        edges=all_edges,
        edge_sections=edge_sections,
    )


def build_maze_topology(size: int, colors: List[str]) -> Topology:
    """Build a Maze topology of the given size."""
    arm_length = size // 2
    states: List[State] = []
    horizontal_edges: List[Tuple[int, int]] = []
    left_arm_edges: List[Tuple[int, int]] = []
    middle_arm_edges: List[Tuple[int, int]] = []
    right_arm_edges: List[Tuple[int, int]] = []

    # Horizontal line states (ids 0 through size-1)
    for i in range(size):
        placement = None
        if i > 0:
            placement = f"right=of s{i - 1}"

        if i == 0:
            self_loop = "left"
        elif i == size - 1:
            self_loop = "right"
        else:
            self_loop = "above"

        comment = "States (horizontal line)" if i == 0 else None
        states.append(
            State(
                id=i,
                row=0,
                col=i,
                is_left_edge=(i == 0),
                is_right_edge=(i == size - 1),
                color=colors[i],
                self_loop_direction=self_loop,
                section_comment=comment,
                placement=placement,
            )
        )

    # Horizontal edges
    for i in range(size - 1):
        horizontal_edges.append((i, i + 1))
        horizontal_edges.append((i + 1, i))

    # Arm definitions: (anchor_col, anchor_id, section_name, loop_dir_non_bottom)
    anchor_ids = [0, size // 2, size - 1]
    arm_names = [
        ("left arm, below s0", "left"),
        (f"middle arm, below s{size // 2}", "right"),
        (f"right arm, below s{size - 1}", "right"),
    ]
    arm_edge_lists = [left_arm_edges, middle_arm_edges, right_arm_edges]

    next_id = size
    for idx, anchor_id in enumerate(anchor_ids):
        section_name, loop_dir = arm_names[idx]
        edge_list = arm_edge_lists[idx]
        anchor_col = states[anchor_id].col

        for j in range(arm_length):
            sid = next_id + j
            arm_row = j + 1

            if j == 0:
                placement = f"below=of s{anchor_id}"
            else:
                placement = f"below=of s{sid - 1}"

            if j == arm_length - 1:
                self_loop = "below"
            else:
                self_loop = loop_dir

            comment = f"States ({section_name})" if j == 0 else None
            states.append(
                State(
                    id=sid,
                    row=arm_row,
                    col=anchor_col,
                    is_left_edge=(anchor_col == 0),
                    is_right_edge=(anchor_col == size - 1),
                    color=colors[sid],
                    self_loop_direction=self_loop,
                    section_comment=comment,
                    placement=placement,
                )
            )

        # Arm edges: anchor <-> first arm state, then consecutive pairs
        first_arm_id = next_id
        edge_list.append((anchor_id, first_arm_id))
        edge_list.append((first_arm_id, anchor_id))
        for j in range(arm_length - 1):
            a = next_id + j
            b = next_id + j + 1
            edge_list.append((a, b))
            edge_list.append((b, a))

        next_id += arm_length

    all_edges = (
        horizontal_edges
        + left_arm_edges
        + middle_arm_edges
        + right_arm_edges
    )
    edge_sections = [
        ("Horizontal transitions", horizontal_edges),
        ("Left arm transitions", left_arm_edges),
        ("Middle arm transitions", middle_arm_edges),
        ("Right arm transitions", right_arm_edges),
    ]

    return Topology(
        type="Maze",
        size=size,
        states=states,
        edges=all_edges,
        edge_sections=edge_sections,
    )


def _action_from_positions(from_state: State, to_state: State) -> str:
    """Determine the action label for a transition based on state positions."""
    dc = to_state.col - from_state.col
    dr = to_state.row - from_state.row
    if dc > 0:
        return "right"
    elif dc < 0:
        return "left"
    elif dr > 0:
        return "down"
    else:
        return "up"


def _edge_label_placement(action: str) -> str:
    """TikZ label placement for a bend-left edge, based on action direction."""
    return {"right": "above", "left": "below", "down": "right", "up": "left"}[action]


# Display names for actions
_ACTION_DISPLAY = {"left": "L", "right": "R", "up": "U", "down": "D"}


def _all_actions(topo_type: str) -> List[str]:
    """Ordered list of possible actions for a topology type."""
    if topo_type == "Line":
        return ["left", "right"]
    return ["left", "right", "up", "down"]


def _compute_self_loop_actions(
    state_id: int,
    topo_type: str,
    outgoing_actions: Dict[int, Set[str]],
) -> List[str]:
    """Compute the actions that belong on a state's self-loop."""
    all_acts = _all_actions(topo_type)
    used = outgoing_actions.get(state_id, set())
    return [a for a in all_acts if a not in used]


def _compute_row_count(topo_type: str, size: int) -> int:
    """Compute the number of vertical rows a topology occupies."""
    if topo_type == "Line":
        return 1
    elif topo_type == "Grid":
        return size
    else:  # Maze
        return 1 + size // 2


def render_tikz(
    topology: Topology,
    include_self_loops: bool = True,
    include_action_labels: bool = True,
    node_prefix: str = "",
    wrap: bool = True,
) -> str:
    """Render a Topology as a complete TikZ code string."""
    lines: List[str] = []
    p = node_prefix  # shorthand for prefixing node names

    # Build lookup structures for action labels
    state_map: Dict[int, State] = {s.id: s for s in topology.states}
    outgoing_actions: Dict[int, Set[str]] = defaultdict(set)
    if include_action_labels:
        for from_id, to_id in topology.edges:
            action = _action_from_positions(state_map[from_id], state_map[to_id])
            outgoing_actions[from_id].add(action)

    # Preamble
    if wrap:
        lines.append("\\begin{tikzpicture}[")
        lines.append("  >=Latex,")
        lines.append(
            "  state/.style={draw,circle,minimum size=8mm,inner sep=0pt,font=\\small},"
        )
        lines.append("  edge/.style={-Latex,thick},")
        if include_action_labels:
            lines.append("  action/.style={font=\\tiny},")
        lines.append("  node distance=12mm")
        lines.append("]")
        lines.append("")

    # States
    current_comment: Optional[str] = None
    for state in topology.states:
        # Emit section comments when they change
        if state.section_comment is not None and state.section_comment != current_comment:
            current_comment = state.section_comment
            lines.append(f"% --- {current_comment}")
        elif state is topology.states[0]:
            lines.append("% --- States")

        # Build node options
        opts = ["state"]
        if state.color == "red":
            opts.append("fill=red!20")
        elif state.color == "green":
            opts.append("fill=green!20")

        if state.placement:
            prefixed_placement = state.placement.replace("=of s", f"=of {p}s")
            opts.append(prefixed_placement)

        opts_str = ", ".join(opts)
        display = state.label if state.label is not None else str(state.id)
        lines.append(f"\\node[{opts_str}] ({p}s{state.id}) {{{display}}};")

    lines.append("")

    # Self-loops and transitions
    def _render_self_loop(state: State) -> str:
        """Render a single self-loop draw command."""
        cmd = f"\\draw[edge] ({p}s{state.id}) edge[loop {state.self_loop_direction}]"
        if include_action_labels:
            actions = _compute_self_loop_actions(
                state.id, topology.type, outgoing_actions
            )
            if actions:
                label_text = ", ".join(_ACTION_DISPLAY[a] for a in actions)
                cmd += f" node[action, {state.self_loop_direction}] {{${label_text}$}}"
        cmd += f" ({p}s{state.id});"
        return cmd

    def _render_edge(from_id: int, to_id: int) -> str:
        """Render a single transition draw command."""
        cmd = f"\\draw[edge] ({p}s{from_id}) edge[bend left=20]"
        if include_action_labels:
            action = _action_from_positions(state_map[from_id], state_map[to_id])
            placement = _edge_label_placement(action)
            cmd += f" node[action, midway, {placement}] {{${_ACTION_DISPLAY[action]}$}}"
        cmd += f" ({p}s{to_id});"
        return cmd

    if topology.type == "Line":
        # Line: interleave self-loops with transitions in one "Transitions" section
        lines.append("% --- Transitions")
        # State 0 self-loop first
        first_state = topology.states[0]
        if include_self_loops and first_state.self_loop_direction:
            lines.append(_render_self_loop(first_state))
        # All regular edges
        for from_id, to_id in topology.edges:
            lines.append(_render_edge(from_id, to_id))
        # Last state self-loop last
        last_state = topology.states[-1]
        if include_self_loops and last_state.self_loop_direction:
            lines.append(_render_self_loop(last_state))
        lines.append("")
    else:
        # Grid/Maze: separate self-loops section, then edge sections
        self_loop_states = [s for s in topology.states if s.self_loop_direction]
        if include_self_loops and self_loop_states:
            if topology.type == "Grid":
                lines.append("% --- Self-loops (perimeter states)")
            else:
                lines.append("% --- Self-loops")
            for state in self_loop_states:
                lines.append(_render_self_loop(state))
            lines.append("")

        # Transition edge sections
        if topology.edges:
            edge_sections: List[Tuple[str, List[Tuple[int, int]]]] = []
            if topology.edge_sections:
                edge_sections = topology.edge_sections
            else:
                edge_sections = [("Transitions", topology.edges)]

            for section_name, edges in edge_sections:
                lines.append(f"% --- {section_name}")
                for from_id, to_id in edges:
                    lines.append(_render_edge(from_id, to_id))
                lines.append("")

    if wrap:
        lines.append("\\end{tikzpicture}")
    return "\n".join(lines)


def render_tikz_stacked(
    topologies: List[Topology],
    include_self_loops: bool = True,
    include_action_labels: bool = True,
) -> str:
    """Render multiple topology copies stacked vertically using TikZ scopes."""
    lines: List[str] = []

    # Preamble (shared)
    lines.append("\\begin{tikzpicture}[")
    lines.append("  >=Latex,")
    lines.append(
        "  state/.style={draw,circle,minimum size=8mm,inner sep=0pt,font=\\small},"
    )
    lines.append("  edge/.style={-Latex,thick},")
    if include_action_labels:
        lines.append("  action/.style={font=\\tiny},")
    lines.append("  node distance=12mm")
    lines.append("]")
    lines.append("")

    # Compute vertical offset per copy (node_distance=12mm + node_size=8mm = 20mm per row)
    topo_type = topologies[0].type
    topo_size = topologies[0].size
    row_count = _compute_row_count(topo_type, topo_size)
    row_height_cm = 2.0  # ~20mm per row
    padding_cm = 2.0
    offset_cm = row_count * row_height_cm + padding_cm

    for idx, topo in enumerate(topologies):
        yshift = -idx * offset_cm
        prefix = f"c{idx}"
        lines.append(f"% === Copy {idx} ===")
        lines.append(f"\\begin{{scope}}[yshift={yshift}cm]")
        body = render_tikz(
            topo,
            include_self_loops=include_self_loops,
            include_action_labels=include_action_labels,
            node_prefix=prefix,
            wrap=False,
        )
        lines.append(body)
        lines.append("\\end{scope}")
        lines.append("")

    lines.append("\\end{tikzpicture}")
    return "\n".join(lines)


def write_output(tikz_code: str, filename: str) -> None:
    """Write TikZ code to a file."""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(tikz_code)
    print(f"Wrote {filename}")


def _compute_state_count(topo_type: str, size: int) -> int:
    """Compute the total number of states for a given topology and size."""
    if topo_type == "Line":
        return size
    elif topo_type == "Grid":
        return size * size
    else:  # Maze
        return size + 3 * (size // 2)


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate TikZ state machine diagrams"
    )
    parser.add_argument(
        "--type",
        required=True,
        choices=["Line", "Grid", "Maze"],
        help="Topology type: Line, Grid, or Maze",
    )
    parser.add_argument(
        "--size",
        required=True,
        type=int,
        help="Size parameter (odd positive integer)",
    )
    parser.add_argument(
        "--colors",
        required=False,
        type=str,
        help="Comma-separated state colors (white, red, green). "
        "Use | to separate multiple copies with different colors "
        "(e.g. 'red,white,white|white,red,white|white,white,red').",
    )
    parser.add_argument(
        "--labels",
        required=False,
        type=str,
        help="Comma-separated state labels (e.g. '$s_0$,$s_1$,...'). "
        "Defaults to state number. Supports LaTeX math.",
    )
    parser.add_argument(
        "--no-self-loops",
        action="store_true",
        default=False,
        help="Omit self-loop edges from the output",
    )
    parser.add_argument(
        "--no-action-labels",
        action="store_true",
        default=False,
        help="Omit action labels (left, right, up, down) from edges",
    )
    parser.add_argument(
        "--output",
        "-o",
        required=False,
        type=str,
        help="Output file name. Default: state_machine_{type}_{size}.txt",
    )
    args = parser.parse_args()

    # Validate size is odd and positive
    if args.size < 1 or args.size % 2 == 0:
        print(
            f"Error: --size must be an odd positive integer, got {args.size}.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Validate minimum size
    min_size = 5 if args.type == "Maze" else 3
    if args.size < min_size:
        print(
            f"Error: --size for {args.type} must be at least {min_size}, got {args.size}.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Compute state count and parse color sets (| separates copies)
    state_count = _compute_state_count(args.type, args.size)
    valid_colors = {"white", "red", "green"}

    if args.colors:
        color_sets_raw = args.colors.split("|")
    else:
        color_sets_raw = []

    color_sets: List[List[str]] = []
    if color_sets_raw:
        for set_idx, raw_set in enumerate(color_sets_raw):
            color_list = [c.strip() for c in raw_set.split(",")]
            invalid = [c for c in color_list if c not in valid_colors]
            if invalid:
                copy_label = f" (copy {set_idx})" if len(color_sets_raw) > 1 else ""
                print(
                    f"Error: invalid color(s){copy_label}: {', '.join(invalid)}. "
                    f"Valid colors are: white, red, green.",
                    file=sys.stderr,
                )
                sys.exit(1)
            if len(color_list) != state_count:
                copy_label = f" (copy {set_idx})" if len(color_sets_raw) > 1 else ""
                print(
                    f"Error: expected {state_count} colors{copy_label} for {args.type} "
                    f"of size {args.size}, got {len(color_list)}.",
                    file=sys.stderr,
                )
                sys.exit(1)
            color_sets.append(color_list)
    else:
        color_sets.append(["white"] * state_count)

    # Validate labels
    if args.labels:
        label_list = [l.strip() for l in args.labels.split(",")]
        if len(label_list) != state_count:
            print(
                f"Error: expected {state_count} labels for {args.type} "
                f"of size {args.size}, got {len(label_list)}.",
                file=sys.stderr,
            )
            sys.exit(1)
    else:
        label_list = [str(i) for i in range(state_count)]

    # Build topologies (one per color set)
    builders = {
        "Line": build_line_topology,
        "Grid": build_grid_topology,
        "Maze": build_maze_topology,
    }
    topologies: List[Topology] = []
    for color_list in color_sets:
        topology = builders[args.type](args.size, color_list)
        for state, label in zip(topology.states, label_list):
            state.label = label
        topologies.append(topology)

    # Render and write
    render_opts = dict(
        include_self_loops=not args.no_self_loops,
        include_action_labels=not args.no_action_labels,
    )
    if len(topologies) == 1:
        tikz_code = render_tikz(topologies[0], **render_opts)
    else:
        tikz_code = render_tikz_stacked(topologies, **render_opts)

    filename = args.output if args.output else f"state_machine_{args.type}_{args.size}.txt"
    write_output(tikz_code, filename)


if __name__ == "__main__":
    main()

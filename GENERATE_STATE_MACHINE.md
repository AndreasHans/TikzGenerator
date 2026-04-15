# State machine TikZ generator

Generate TikZ state machine diagrams for LaTeX documents. No dependencies beyond Python 3.8+.

## Quick start

```bash
python generate_state_machine.py --type Line --size 7
python generate_state_machine.py --type Grid --size 5
python generate_state_machine.py --type Maze --size 11
```

Output goes to `state_machine_{type}_{size}.txt` by default, or use `--output`/`-o` to set a custom file name.

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--type` | Yes | Topology: `Line`, `Grid`, or `Maze` |
| `--size` | Yes | Odd positive integer. Minimum 3 for Line/Grid, 5 for Maze |
| `--colors` | No | Comma-separated colors for each state. Valid: `white`, `red`, `green`. Use `\|` to separate multiple copies with different colors (see Stacked copies). Default: all white |
| `--labels` | No | Comma-separated labels for each state. Supports LaTeX math (e.g., `$s_0$`). Default: state number |
| `--no-self-loops` | No | Omit all self-loop edges from the output |
| `--no-action-labels` | No | Omit action labels (L, R, U, D) from edges. Labels are included by default |
| `--output`, `-o` | No | Output file name. Default: `state_machine_{type}_{size}.txt` |

## Action labels

By default, every edge includes an action label rendered as LaTeX math (`$...$`):

- **Line**: `$L$` (left), `$R$` (right)
- **Grid and Maze**: `$L$`, `$R$`, `$U$` (up), `$D$` (down)

Transition edges show the action that causes that transition (e.g., moving right from s0 to s1 is labeled `$R$`). Self-loops show the remaining actions that have no corresponding neighbor -- taking those actions keeps you in the same state. For example, the top-left corner of a Grid has a self-loop labeled `$L, U$`.

Use `--no-action-labels` to omit all action labels from the output.

## Topologies

### Line

N states in a horizontal row. Self-loops on the first (left) and last (right) states. Bidirectional edges between neighbors.

- State count: `size`

### Grid

N x N states in a square grid. Self-loops on all perimeter states. Bidirectional edges between horizontal and vertical neighbors.

- State count: `size * size`

### Maze

A horizontal line of N states with three downward arms hanging from the left end (s0), middle (s{size//2}), and right end (s{size-1}). Each arm has `size // 2` states. Self-loops on every state.

- State count: `size + 3 * (size // 2)`

## State ordering

Colors and labels map to states by index, in this order:

- **Line**: s0 through s{size-1}, left to right
- **Grid**: s0 through s{size*size-1}, row by row (row 0 left-to-right, then row 1, etc.)
- **Maze**: horizontal line first (s0 through s{size-1}), then left arm top-to-bottom, then middle arm, then right arm

## Stacked copies

Stack multiple copies of the same diagram vertically, each with different state colors. Separate color sets with `|` in the `--colors` argument:

```bash
python generate_state_machine.py --type Line --size 3 --colors "red,white,white|white,red,white|white,white,red"
```

This produces three copies of the Line topology stacked vertically, each highlighting a different state. The number of copies equals the number of `|`-separated color groups.

Each copy is wrapped in a `\begin{scope}[yshift=...]...\end{scope}` block with unique node ID prefixes (`c0s0`, `c1s0`, `c2s0`, etc.) to avoid TikZ naming conflicts. Vertical spacing is computed automatically based on the topology's row count.

Labels, self-loop settings, and action label settings apply uniformly to all copies -- only colors vary per copy.

## Examples

Basic line with 25 states:

```bash
python generate_state_machine.py --type Line --size 25
```

Maze with LaTeX subscript labels:

```bash
python generate_state_machine.py --type Maze --size 5 --labels "$s_0$,$s_1$,$s_2$,$s_3$,$s_4$,$s_5$,$s_6$,$s_7$,$s_8$,$s_9$,$s_{10}$"
```

Grid with row-based coloring (row 2 red, last row white, rest green):

```bash
# 5x5 grid (25 states): row 2 = indices 10-14 = red, row 4 = indices 20-24 = white, rest = green
python generate_state_machine.py --type Grid --size 5 --colors "green,green,green,green,green,green,green,green,green,green,red,red,red,red,red,green,green,green,green,green,white,white,white,white,white"
```

Maze with specific coloring and no self-loops:

```bash
# Maze size 5 (11 states): first 2 horizontal red, middle arm green, rest white
python generate_state_machine.py --type Maze --size 5 --colors "red,red,white,white,white,white,white,green,green,white,white" --no-self-loops
```

Maze without self-loops (transitions only with action labels):

```bash
python generate_state_machine.py --type Maze --size 7 --no-self-loops -o state_machine_Maze_7_no_loops.txt
```

Clean diagram with no action labels:

```bash
python generate_state_machine.py --type Grid --size 5 --no-action-labels
```

Stacked Line diagrams highlighting each state in turn:

```bash
python generate_state_machine.py --type Line --size 5 \
  --colors "green,white,white,white,white|white,green,white,white,white|white,white,green,white,white|white,white,white,green,white|white,white,white,white,green" \
  --no-self-loops -o line_5_all_highlights.txt
```

## AI reference

When generating `--colors` or `--labels` strings programmatically, compute the state count first:

- Line: `count = size`
- Grid: `count = size * size`
- Maze: `count = size + 3 * (size // 2)`

Then build a comma-separated string with exactly `count` entries. For labels with LaTeX subscripts, use `$s_{N}$` (braces required for N >= 10).

Colors apply a 20% tint in TikZ: `red` becomes `fill=red!20`, `green` becomes `fill=green!20`, `white` means no fill attribute.

Action labels are short single-letter codes rendered as LaTeX math: L (left), R (right), U (up), D (down). Self-loop labels combine unused actions (e.g., `$L, U$` for a corner state). A TikZ `action` style (`font=\tiny`) is added to the preamble when action labels are enabled.

For stacked copies, join multiple comma-separated color strings with `|`. Each group must have exactly `count` colors. Node IDs are prefixed with `c{copy_index}` (e.g., `c0s0`, `c1s0`). Vertical offset between copies is computed as `row_count * 2 + 2` cm, where row_count is 1 for Line, `size` for Grid, and `1 + size // 2` for Maze.

All arguments are validated. Errors print to stderr and exit with code 1.

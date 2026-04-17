---
name: generate-state-machine
description: "Generate TikZ state machine diagrams for Line, Grid, or Maze topologies. Use when asked to create, generate, or draw a state machine, topology diagram, line, grid, or maze with optional state colors, labels, self-loops, and action labels."
argument-hint: "e.g. 'maze of size 7 with goal state 12 colored green and no self-loops'"
---

# Generate State Machine TikZ Diagrams

Generate TikZ state machine diagrams by running `generate_state_machine.py` in the workspace root.

## When to Use

- User asks to create/generate a line, grid, or maze diagram
- User asks for a state machine or topology diagram with specific colors, labels, or options
- User wants to visualize states with or without self-loops or action labels

## Procedure

### 1. Determine Parameters

Extract from the user's request:

| Parameter | How to determine |
|-----------|-----------------|
| **type** | `Line`, `Grid`, or `Maze` — infer from the request |
| **size** | Must be an **odd positive integer**. Minimum 3 for Line/Grid, minimum 5 for Maze |
| **colors** | Map user descriptions (e.g., "goal state 8 green", "state 4 red") to a comma-separated color string. Valid colors: `white`, `red`, `green` |
| **labels** | If user wants custom labels (e.g., LaTeX subscripts `$s_0$`), build a comma-separated string |
| **self-loops** | Add `--no-self-loops` if user says "no self-loops" or "without self-loops" |
| **action labels** | Add `--no-action-labels` if user says "no action labels" or "without labels" |
| **output** | Use `-o filename.txt` if user specifies a name; otherwise default is `state_machine_{type}_{size}.txt` |

### 2. Compute State Count

Before building `--colors` or `--labels`, compute the number of states:

- **Line**: `count = size`
- **Grid**: `count = size * size`
- **Maze**: `count = size + 3 * (size // 2)`

The colors and labels strings must have exactly `count` comma-separated entries.

### 3. Build the Command

```bash
python generate_state_machine.py --type {Type} --size {size} [options]
```

**Options:**
- `--colors "c0,c1,c2,..."` — one color per state (`white`, `red`, or `green`)
- `--labels "l0,l1,l2,..."` — one label per state (supports LaTeX math like `$s_0$`)
- `--no-self-loops` — omit self-loop edges
- `--no-action-labels` — omit L/R/U/D labels from edges
- `-o filename.txt` — custom output file name

**Stacked copies** (multiple color sets separated by `|`):
```bash
--colors "red,white,white|white,red,white|white,white,red"
```
Each `|`-group produces a vertically stacked copy with those colors.

### 4. Run the Command

Run from the workspace root (`TikzGenerator/` directory):

```bash
python generate_state_machine.py --type Maze --size 9 --no-self-loops
```

Output writes to `state_machine_{type}_{size}.txt` (or the `-o` path).

## Topologies

### Line
N states in a horizontal row. Bidirectional L/R edges between neighbors. Self-loops on first (left) and last (right) states.

### Grid
N×N states in a square grid. Bidirectional L/R/U/D edges between neighbors. Self-loops on all perimeter states.

### Maze
A horizontal line of N states with three downward arms from s0 (left), s{size//2} (middle), and s{size-1} (right). Each arm has `size // 2` states. Self-loops on every state.

**State ordering for colors/labels:** horizontal line first (s0–s{size-1}), then left arm top-to-bottom, then middle arm, then right arm.

## Color Mapping

- `white` — no fill (default)
- `red` — renders as `fill=red!20`
- `green` — renders as `fill=green!20`

## Examples

Maze size 5, goal state 8 green, state 4 red, no self-loops:
```bash
python generate_state_machine.py --type Maze --size 5 --colors "white,white,white,white,red,white,white,white,green,white,white" --no-self-loops
```

Grid size 5, all white, no action labels:
```bash
python generate_state_machine.py --type Grid --size 5 --no-action-labels
```

Line size 7 with LaTeX labels:
```bash
python generate_state_machine.py --type Line --size 7 --labels "$s_0$,$s_1$,$s_2$,$s_3$,$s_4$,$s_5$,$s_6$"
```

Stacked Line highlighting each state:
```bash
python generate_state_machine.py --type Line --size 3 --colors "red,white,white|white,red,white|white,white,red" --no-self-loops
```

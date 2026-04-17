---
name: generate-from-input
description: "Generate combined TikZ diagrams (state machine + Mealy machine) from a spec file. Use when asked to generate from an input file, create a combined diagram, or produce both a state machine and Mealy machine from theta/delta transition rules."
argument-hint: "e.g. 'generate diagrams from input.txt' or 'create a Maze size 7 with goal 8, memory 2, and these transitions...'"
---

# Generate Combined Diagrams from Input Spec

Generate a state machine, Mealy machine, and combined diagram by running `generate_from_input.py` with a spec file.

## When to Use

- User asks to generate from an input/spec file
- User provides theta/delta transition rules and wants both diagrams
- User wants a combined state machine + Mealy machine figure
- User has or wants to create a spec file with type, size, goal, memory, y-states, and transitions

## Procedure

### 1. Create or Identify the Input File

The input file is plain text with headers and transition rules. Lines starting with `#` and blank lines are ignored.

**Required headers:**

| Key | Description |
|-----|-------------|
| `type` | Topology: `Line`, `Grid`, or `Maze` |
| `size` | Odd positive integer. Min 3 for Line/Grid, min 5 for Maze |
| `goal` | Goal state index (will be colored green) |
| `memory` | Number of Mealy machine memory states |

**State markers:**
- `y(s)` — marks state `s` as a y-state (colored red)

**Transition rules:**
- `theta(c,o,a)` — in memory state `c`, on observation `o`, output action `a`
- `delta(c,o,c')` — in memory state `c`, on observation `o`, transition to memory state `c'`

Matching `theta` and `delta` entries (same `c` and `o`) are joined to form Mealy machine edges labeled `$o/a$`.

### 2. Validate the Spec

**State count formulas** (for validating `goal` and `y` indices):
- Line: `count = size`
- Grid: `count = size * size`
- Maze: `count = size + 3 * (size // 2)`

**Constraints:**
- `goal` must be in `[0, state_count - 1]`
- Each `y(s)` state must be in `[0, state_count - 1]`
- `c` values in theta/delta must be in `[0, memory - 1]`
- `c'` values in delta must be in `[0, memory - 1]`
- Every `theta(c,o,...)` should have a matching `delta(c,o,...)`  and vice versa

### 3. Run the Command

```bash
python generate_from_input.py [input_file]
```

Default input file is `input.txt` if omitted.

### 4. Output Files

The script produces three files:
- `state_machine_{type}_{size}.txt` — state machine diagram (with `--no-self-loops` and colors from goal/y-states)
- `mealy_machine_{memory}.txt` — Mealy machine diagram (with `$c_0$`, `$c_1$`, ... labels)
- `combined_{type}_{size}.txt` — both diagrams side by side in a single `tikzpicture`

## Input File Example

```
type=Maze
size=7
goal=8
memory=2
y(0)
theta(0,0,R)
theta(0,bot,L)
theta(1,0,R)
theta(1,bot,R)
delta(0,0,1)
delta(0,bot,0)
delta(1,bot,1)
delta(1,0,1)
```

This generates:
- A 7-wide Maze with state 0 red, state 8 green, no self-loops
- A 2-state Mealy machine with edges from the theta/delta pairs
- A combined figure with both placed side by side

## How It Works Internally

1. Parses the input file for headers, y-states, theta rules, and delta rules
2. Builds a color string: goal state → green, y-states → red, rest → white
3. Calls `generate_state_machine.py` with `--type`, `--size`, `--no-self-loops`, and `--colors`
4. Joins theta/delta on `(c, o)` to build transition strings (`c,c',o,a`)
5. Calls `generate_mealy_machine.py` with `--states`, `--transitions`, and `--labels`
6. Combines both outputs into a single `tikzpicture` with the Mealy machine placed to the right

## Creating a New Input File

If the user provides transition rules inline, create an input file following this template:

```
type={Type}
size={size}
goal={goal_state}
memory={memory_count}
y({red_state_1})
y({red_state_2})
theta({c},{observation},{action})
delta({c},{observation},{c_prime})
```

Save it (e.g., `input.txt` or a descriptive name) then run:
```bash
python generate_from_input.py my_spec.txt
```

# TikzGenerator

A collection of Python scripts for generating TikZ diagrams of automata and state machines for LaTeX documents. No dependencies beyond Python 3.8+.

## Tools

| Script | Description | Docs |
|--------|-------------|------|
| `generate_from_input.py` | All-in-one generator: reads a spec file and produces a state machine, Mealy machine, and combined diagram | — |
| `generate_state_machine.py` | State machine diagrams (Line, Grid, Maze topologies) with configurable colors, labels, action labels, and stacked copies | [GENERATE_STATE_MACHINE.md](GENERATE_STATE_MACHINE.md) |
| `generate_mealy_machine.py` | Mealy machine diagrams with arbitrary states, input/output transitions, colors, and labels | [GENERATE_MEALY_MACHINE.md](GENERATE_MEALY_MACHINE.md) |

## Usage

The easiest way to generate diagrams is with `generate_from_input.py`. Write a spec file (see [Input format](#input-format)) and run:

```bash
python generate_from_input.py input.txt
```

This produces three files:

- `state_machine_{type}_{size}.txt` — the state machine diagram
- `mealy_machine_{memory}.txt` — the Mealy machine diagram
- `combined_{type}_{size}.txt` — both diagrams side by side in a single `tikzpicture`

You can also call the underlying scripts directly:

```bash
# State machine — 5x5 grid, center green, bottom row red
python generate_state_machine.py --type Grid --size 5 --colors "white,white,white,white,white,white,white,white,white,white,white,white,green,white,white,white,white,white,white,white,red,red,red,red,red"

# Mealy machine — 3 states with transitions, colors, and labels
python generate_mealy_machine.py --states 3 --transitions "0,1,a,0;1,2,b,1;2,0,a,1" --colors "green,white,red" --labels '$q_0$,$q_1$,$q_2$'
```

Each script writes a `.txt` file containing TikZ code that can be included in a LaTeX document with `\input{}`.

## Input format

The spec file used by `generate_from_input.py` is a plain-text file with headers and transition rules. Lines starting with `#` and blank lines are ignored.

### Headers

| Key | Description |
|-----|-------------|
| `type` | Topology: `Line`, `Grid`, or `Maze` |
| `size` | Size parameter (odd positive integer) |
| `goal` | Goal state index (colored green) |
| `memory` | Number of Mealy machine memory states |

### State markers

- `y(s)` — marks state `s` as a "y-state" (colored red in the diagram)

### Transition rules

- `theta(c,o,a)` — in memory state `c`, on observation `o`, output action `a`
- `delta(c,o,c')` — in memory state `c`, on observation `o`, transition to memory state `c'`

Matching `theta` and `delta` entries (same `c` and `o`) are joined to form Mealy machine edges labeled `o/a`.

### Example

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

This generates a 7-wide Maze with state 0 red, state 8 green, and a 2-state Mealy machine.

## LaTeX integration

Wrap the output in a `tikzpicture`-compatible document. Required packages:

```latex
\usepackage{tikz}
\usetikzlibrary{arrows.meta,positioning,automata}
```

Then include the generated file:

```latex
\input{state_machine_Grid_5.txt}
```

See each tool's documentation for full argument reference and examples.

## Copilot Skills

This project includes three [GitHub Copilot skills](https://code.visualstudio.com/docs/copilot/copilot-customization) that let you generate diagrams through natural language in VS Code's Copilot Chat. The skills live in `.github/skills/` and are automatically picked up by Copilot.

### Available Skills

| Skill | Trigger phrases | What it does |
|-------|----------------|--------------|
| **generate-state-machine** | "create a line/grid/maze", "draw a state machine", "topology diagram" | Generates a state machine diagram via `generate_state_machine.py` with the right `--type`, `--size`, `--colors`, `--labels`, etc. |
| **generate-mealy-machine** | "create a Mealy machine", "draw a transducer", "automaton with input/output" | Generates a Mealy machine diagram via `generate_mealy_machine.py` with `--states`, `--transitions`, colors, and labels |
| **generate-from-input** | "generate from input file", "create combined diagram", "generate from spec" | Runs `generate_from_input.py` on a spec file to produce a state machine, Mealy machine, and combined diagram |

### How to Use

Open Copilot Chat in VS Code and describe what you want in plain English. Examples:

- **"Create a line of size 15 with the first 3 states green"**
  → Copilot runs `generate_state_machine.py --type Line --size 15 --colors "green,green,green,white,..."` and writes `state_machine_Line_15.txt`

- **"Draw a maze of size 7 with goal state 8 green, state 0 red, no self-loops"**
  → Copilot runs `generate_state_machine.py --type Maze --size 7 --colors "red,...,green,..." --no-self-loops`

- **"Create a 3-state Mealy machine with transitions 0→1 on a/0, 1→2 on b/1, 2→0 on a/1"**
  → Copilot runs `generate_mealy_machine.py --states 3 --transitions "0,1,a,0;1,2,b,1;2,0,a,1"`

- **"Generate diagrams from input.txt"**
  → Copilot runs `generate_from_input.py input.txt` and produces three output files

### What You Can Specify

For **state machines**, you can describe:
- Topology type (Line, Grid, Maze) and size
- State colors (e.g., "first 5 green", "state 12 red")
- Custom labels (e.g., "labels are state number + 1", "random values 0–99")
- Options like "no self-loops" or "no action labels"
- Stacked copies with different color highlights

For **Mealy machines**, you can describe:
- Number of states
- Transitions as from→to with input/output labels
- State colors and custom labels

For **combined diagrams**, you can provide:
- A spec file path, or describe the transitions inline and Copilot will create the spec file for you

## Development

This tool was developed entirely through AI-assisted generation. See [DEVELOPMENT_PROCESS.md](DEVELOPMENT_PROCESS.md) for details.

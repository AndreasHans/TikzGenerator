# TikzGenerator

A collection of Python scripts for generating TikZ diagrams of automata and state machines for LaTeX documents. No dependencies beyond Python 3.8+.

## Tools

| Script | Description | Docs |
|--------|-------------|------|
| `generate_state_machine.py` | State machine diagrams (Line, Grid, Maze topologies) with configurable colors, labels, action labels, and stacked copies | [GENERATE_STATE_MACHINE.md](GENERATE_STATE_MACHINE.md) |
| `generate_mealy_machine.py` | Mealy machine diagrams with arbitrary states, input/output transitions, colors, and labels | [GENERATE_MEALY_MACHINE.md](GENERATE_MEALY_MACHINE.md) |

## Usage

```bash
# State machine — 5x5 grid, center green, bottom row red
python generate_state_machine.py --type Grid --size 5 --colors "white,...,green,...,red,..."

# Mealy machine — 3 states with transitions, colors, and labels
python generate_mealy_machine.py --states 3 --transitions "0,1,a,0;1,2,b,1;2,0,a,1" --colors "green,white,red" --labels '$q_0$,$q_1$,$q_2$'
```

Each script writes a `.txt` file containing TikZ code that can be included in a LaTeX document with `\input{}`.

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

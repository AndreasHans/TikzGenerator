# Mealy machine TikZ generator

Generate TikZ Mealy machine diagrams for LaTeX documents. No dependencies beyond Python 3.8+.

## Quick start

```bash
python generate_mealy_machine.py --states 3 --transitions "0,1,a,0;1,2,b,1;2,0,a,1;0,0,b,0"
```

Output goes to `mealy_machine_{states}.txt` by default, or use `--output`/`-o` to set a custom file name.

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--states` | Yes | Number of states (`s0` through `s{N-1}`) |
| `--transitions` | Yes | Semicolon-separated transitions (see format below) |
| `--colors` | No | Comma-separated colors for each state. Valid: `white`, `red`, `green`. Default: all white |
| `--labels` | No | Comma-separated labels for each state. Supports LaTeX math (e.g., `$s_0$`). Default: `$s_0$`, `$s_1$`, etc. |
| `--output`, `-o` | No | Output file name. Default: `mealy_machine_{states}.txt` |

## Transition format

Each transition is four comma-separated values:

```
from,to,input,output
```

Multiple transitions are separated by semicolons:

```
0,1,a,0;1,0,b,1;0,0,b,0
```

- `from` / `to` — state indices (0-based, must be in range `[0, states-1]`)
- `input` — the input symbol (arbitrary text, rendered in LaTeX math mode)
- `output` — the output symbol (arbitrary text, rendered in LaTeX math mode)

Each transition is rendered as an edge labeled `$input/output$`.

## Layout

States are arranged in a circle and labeled `$s_0$`, `$s_1$`, etc. (or custom labels via `--labels`). An arrow points into `s0` to mark the initial state. States can be colored with `--colors`; `red` and `green` states get a light fill (`red!20` / `green!20`), `white` states have no fill.

- **Self-loops** — transitions where `from == to` are drawn as loops, positioned away from the center of the circle.
- **Bidirectional edges** — when transitions exist in both directions between two states, edges are bent to avoid overlap.
- **Parallel transitions** — multiple transitions between the same pair of states are merged into a single edge with combined labels (e.g., `$a/0, b/1$`).

## Examples

Two-state machine:

```bash
python generate_mealy_machine.py --states 2 --transitions "0,1,a,0;1,0,b,1;0,0,b,1;1,1,a,0"
```

Three states with colors and custom labels:

```bash
python generate_mealy_machine.py --states 3 \
  --transitions "0,1,a,0;1,2,b,1;2,0,a,1" \
  --colors "green,white,red" \
  --labels '$q_0$,$q_1$,$q_2$'
```

Four-state machine with custom output file:

```bash
python generate_mealy_machine.py --states 4 \
  --transitions "0,1,0,0;1,2,0,1;2,3,1,0;3,0,1,1;0,0,1,1;1,1,1,0;2,2,0,1;3,3,0,0" \
  -o my_mealy.txt
```

---
name: generate-mealy-machine
description: "Generate TikZ Mealy machine diagrams with circular state layout. Use when asked to create, generate, or draw a Mealy machine, automaton, or finite transducer with input/output transitions, state colors, and custom labels."
argument-hint: "e.g. '3-state Mealy machine with transitions 0->1 on a/0 and 1->0 on b/1'"
---

# Generate Mealy Machine TikZ Diagrams

Generate TikZ Mealy machine diagrams by running `generate_mealy_machine.py` in the workspace root.

## When to Use

- User asks to create/generate a Mealy machine, transducer, or automaton with input/output labels
- User provides states and transitions with input/output pairs
- User wants a circular state diagram with labeled edges

## Procedure

### 1. Determine Parameters

Extract from the user's request:

| Parameter | How to determine |
|-----------|-----------------|
| **states** | Number of states (integer >= 1). States are `s0` through `s{N-1}` |
| **transitions** | Semicolon-separated list of `from,to,input,output` (see format below) |
| **colors** | Optional comma-separated colors, one per state. Valid: `white`, `red`, `green` |
| **labels** | Optional comma-separated labels. Default: `$s_0$`, `$s_1$`, etc. Supports LaTeX math |
| **output** | Use `-o filename.txt` for custom name; default is `mealy_machine_{states}.txt` |

### 2. Build the Transition String

Each transition is four comma-separated values: `from,to,input,output`

Multiple transitions are separated by semicolons:
```
0,1,a,0;1,0,b,1;0,0,b,0
```

- `from` / `to` — 0-based state indices in range `[0, states-1]`
- `input` — input symbol (rendered in LaTeX math mode)
- `output` — output symbol (rendered in LaTeX math mode)

Each edge is labeled `$input/output$`. Parallel transitions between the same pair are merged into a single edge (e.g., `$a/0, b/1$`).

### 3. Build the Command

```bash
python generate_mealy_machine.py --states {N} --transitions "{transitions}" [options]
```

**Options:**
- `--colors "c0,c1,..."` — one color per state (`white`, `red`, or `green`)
- `--labels "l0,l1,..."` — one label per state (supports LaTeX math like `$q_0$`)
- `-o filename.txt` — custom output file name

### 4. Run the Command

Run from the workspace root (`TikzGenerator/` directory):

```bash
python generate_mealy_machine.py --states 3 --transitions "0,1,a,0;1,2,b,1;2,0,a,1"
```

Output writes to `mealy_machine_{states}.txt` (or the `-o` path).

## Layout Details

- States are arranged in a **circle**, labeled `$s_0$`, `$s_1$`, etc.
- An **initial state arrow** points into `s0`
- **Self-loops** (from == to) are positioned away from the circle center
- **Bidirectional edges** are bent to avoid overlap
- **Parallel transitions** between the same pair are merged into one edge with combined labels

## Color Mapping

- `white` — no fill (default)
- `red` — renders as `fill=red!20`
- `green` — renders as `fill=green!20`

## Examples

Two-state machine:
```bash
python generate_mealy_machine.py --states 2 --transitions "0,1,a,0;1,0,b,1;0,0,b,1;1,1,a,0"
```

Three states with colors and custom labels:
```bash
python generate_mealy_machine.py --states 3 --transitions "0,1,a,0;1,2,b,1;2,0,a,1" --colors "green,white,red" --labels "$q_0$,$q_1$,$q_2$"
```

Four-state machine with custom output:
```bash
python generate_mealy_machine.py --states 4 --transitions "0,1,0,0;1,2,0,1;2,3,1,0;3,0,1,1;0,0,1,1;1,1,1,0;2,2,0,1;3,3,0,0" -o my_mealy.txt
```

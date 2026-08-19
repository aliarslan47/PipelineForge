# PipelineForge

Turkish version: [README.tr.md](README.tr.md)

A generator for the Forge family's standard **Pipeline DAG** diagrams. It turns a small
per-project spec into a self-contained, bilingual (`tr`/`en`) HTML page: a hand-drawn inline-SVG
node-graph on a dotted canvas, typed cards (code chip + name + tool + ports), curved bezier edges,
a decision diamond, a module matrix table, and the isolated-environment list. Every project comes
out of the same mould; only the graph content and the category palette change.

The point: RNAForge, VirusForge and BacForge all had their `docs/pipeline_architecture.html` drawn
by hand. PipelineForge makes that reproducible — one skeleton, one command, driven by a spec.

## How it works

- **Skeleton is fixed** (the RNAForge reference): CSS/theme tokens, sections, node vocabulary, the
  TR/EN toggle, and the layout mechanics all live in `pipelineforge/forge.py`. There is one source
  of truth for the look.
- **Content comes from a spec** (`specs/<project>.yml`): the nodes, the edges, the categories, the
  tools, the environments, the decision node.
- **Edges are the real `run()` dependencies.** The spec author extracts them from the project's code
  (the `state.is_done` / `inputs()` guards), so the diagram matches how the pipeline actually runs —
  it is not a hand-wavy sketch.
- **Colours are roles, categories are per-project.** Blue = shared (fixed across the family), green
  and amber = the two branch categories, purple = diagnostic. A project maps its own categories
  (organism, molecule, platform, …) onto these roles.
- **Layout engine.** Each node declares a `lane` (an x-column) and a `y`; the engine computes pixel
  positions and routes each edge as a bezier between typed ports (`top`/`bottom`/`left`/`right`),
  leaving and entering perpendicular to the card edge. Hub fan-outs use `to_port: left`.

## Usage

```bash
pip install -e .            # or: pip install pyyaml
pipelineforge render specs/rnaforge.yml -o ../rnaforge-pipeline/docs/pipeline_architecture.html
pipelineforge render specs/virusforge.yml -o ../VirusForge/docs/pipeline_architecture.html
pipelineforge render specs/bacforge.yml  -o ../BacForge/docs/pipeline_architecture.html
```

Each render also self-validates: it prints the per-page node/edge counts and checks tag balance and
that no replacement character (`U+FFFD`) slipped in. Publish the output on GitHub Pages
(`Settings → Pages → main /docs`) so the badge in the project README links to a live rendered page.

## Example specs

| Spec | Project | Archetype | Nodes / edges |
|---|---|---|---|
| `specs/rnaforge.yml`   | RNAForge   | hub-and-spoke (m06) | 21 / 23 |
| `specs/virusforge.yml` | VirusForge | molecule branch (DNA/RNA) | 13 / 16 |
| `specs/bacforge.yml`   | BacForge   | hub-and-spoke (M04) | 19 / 20 |

## Adding a new project

1. Extract the real `run()` dependencies from the project's module code (which module requires which).
2. Write `specs/<project>.yml`: `meta`, `lanes`, `categories`, `nodes` (code, tr/en name, tool,
   `cat`, `lane`, `y`, `dep`), `edges`, `envs`, optional `decision` and `hub_label`.
3. `pipelineforge render specs/<project>.yml -o <project>/docs/pipeline_architecture.html`.
4. Commit, enable Pages, point the project README's diagram badge at the rendered URL.

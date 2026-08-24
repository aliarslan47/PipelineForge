# PipelineForge

A generator for the Forge family's standard **Pipeline DAG** diagrams — turns a small per-project spec into a self-contained, bilingual (`tr`/`en`) HTML node-graph.

[![Pipeline DAG](https://img.shields.io/badge/output-Pipeline%20DAG-0d6b8f)](https://github.com/aliarslan47/PipelineForge)
[![family](https://img.shields.io/badge/family-Forge-2f8f5b)](https://github.com/aliarslan47/PipelineForge)
[![spec](https://img.shields.io/badge/driven%20by-YAML%20spec-c07211)](https://github.com/aliarslan47/PipelineForge)

[Türkçe](README.tr.md) · **English**

## What is it?

PipelineForge is the diagram-generator member of the Forge family — same visual standard as BacForge, VirusForge and RNAForge, but a tool rather than a pipeline. Every project's `docs/pipeline_architecture.html` comes out of the same mould; only the graph content and the category palette change.

## What it does

It renders a hand-drawn inline-SVG node-graph on a dotted canvas from a YAML spec: typed cards (code chip + name + tool + ports), curved bezier edges, a decision diamond, a module matrix table, the isolated-environment list, and a TR/EN toggle.

- **Skeleton is fixed** (the RNAForge reference): CSS/theme, sections, node vocabulary and layout mechanics live in `pipelineforge/forge.py` — one source of truth for the look.
- **Content comes from a spec** (`specs/<project>.yml`): nodes, edges, categories, tools, environments, decision node.
- **Edges are the real `run()` dependencies** extracted from the project's code, so the diagram matches how the pipeline actually runs — not a hand-wavy sketch.
- **Colours are roles, categories are per-project**: blue = shared, green/amber = branches, purple = diagnostic. Each render self-validates (node/edge counts, tag balance, no `U+FFFD`).

## Installation

```bash
git clone https://github.com/aliarslan47/PipelineForge.git
cd PipelineForge

pip install -e .            # or: pip install pyyaml
```

## Usage

```bash
pipelineforge render specs/rnaforge.yml   -o ../rnaforge-pipeline/docs/pipeline_architecture.html
pipelineforge render specs/virusforge.yml -o ../VirusForge/docs/pipeline_architecture.html
pipelineforge render specs/bacforge.yml   -o ../BacForge/docs/pipeline_architecture.html
```

Publish the output on GitHub Pages (`Settings → Pages → main /docs`) so the diagram badge in the project README links to a live page.

## Modules

The specs it renders (one per Forge project); add a new project by extracting its real `run()` dependencies into `specs/<project>.yml`, rendering, and pointing the README badge at the published page.

| Spec | Project | Archetype | Nodes / edges |
|---|---|---|---|
| `specs/rnaforge.yml` | RNAForge | hub-and-spoke (m06) | 21 / 23 |
| `specs/virusforge.yml` | VirusForge | molecule branch (DNA/RNA) | 13 / 16 |
| `specs/bacforge.yml` | BacForge | hub-and-spoke (M04) | 19 / 20 |

Full spec format and the "adding a new project" walkthrough live in the source and `specs/`.

---

Forge family: [RNAForge](https://github.com/aliarslan47/RNAForge) (bulk RNA-seq) · [BacForge](https://github.com/aliarslan47/BacForge) (bacteria) · [VirusForge](https://github.com/aliarslan47/VirusForge) (virus/phage) · [MicrobiomeForge](https://github.com/aliarslan47/MicrobiomeForge) (microbiome) · [Vaxforge](https://github.com/aliarslan47/Vaxforge) (reverse vaccinology) · [ImmForge](https://github.com/aliarslan47/ImmForge) (immune simulation) · **PipelineForge** (DAG generator).

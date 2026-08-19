"""PipelineForge CLI — spec YAML'dan standart Pipeline DAG HTML üretir.

Kullanım:
    python -m pipelineforge render specs/rnaforge.yml -o out.html
    python -m pipelineforge render specs/rnaforge.yml            # stdout
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .forge import Decision, Edge, Node, Spec, render, validate

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


def load_spec(path: str | Path) -> Spec:
    if yaml is None:
        raise SystemExit("PyYAML gerekli: pip install pyyaml")
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))

    nodes = [Node(**n) for n in raw["nodes"]]
    edges = [Edge(**e) for e in raw["edges"]]
    dec = None
    if raw.get("decision"):
        dec = Decision(at=tuple(raw["decision"]["at"]),
                       tr_label=raw["decision"]["tr_label"],
                       tr_sub=raw["decision"]["tr_sub"],
                       en_label=raw["decision"]["en_label"],
                       en_sub=raw["decision"]["en_sub"])
    return Spec(
        name=raw["name"], title=raw["title"], filename=raw["filename"],
        repo=raw["repo"], favicon=raw.get("favicon", "🔬"),
        subtitle_tr=raw["subtitle_tr"], subtitle_en=raw["subtitle_en"],
        footer_tr=raw["footer_tr"], footer_en=raw["footer_en"],
        aria_tr=raw.get("aria_tr", ""), aria_en=raw.get("aria_en", ""),
        lanes=raw["lanes"], viewbox=tuple(raw["viewbox"]),
        categories=raw["categories"], nodes=nodes, edges=edges,
        envs=raw["envs"], decision=dec, hub_label=raw.get("hub_label"),
    )


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="pipelineforge")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("render", help="spec YAML -> Pipeline DAG HTML")
    r.add_argument("spec")
    r.add_argument("-o", "--out", help="çıktı dosyası (yoksa stdout)")
    r.add_argument("--no-validate", action="store_true")
    args = p.parse_args(argv)

    if args.cmd == "render":
        spec = load_spec(args.spec)
        html = render(spec)
        if not args.no_validate:
            v = validate(html)
            msg = (f"[pipelineforge] {spec.name}: {v['nodes_per_page']} kart/sayfa, "
                   f"{v['edges_per_page']} kenar/sayfa")
            if v["errors"]:
                print(msg + "  HATALAR: " + "; ".join(v["errors"]), file=sys.stderr)
                return 2
            print(msg + "  ✓ dengeli, 0 bozuk karakter", file=sys.stderr)
        if args.out:
            Path(args.out).write_text(html, encoding="utf-8")
            print(f"[pipelineforge] yazıldı: {args.out}", file=sys.stderr)
        else:
            sys.stdout.write(html)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Build the ontology review slide deck.

Usage (from the repository root):
    .venv\\Scripts\\python docs\\slidedeck\\ontology_review\\build_deck.py [-o OUTPUT]

Runs every example in ``deck/examples.py`` (rdflib + owlrl), then renders the
slides in ``deck/slides.py`` to ``ontology_review.pptx`` next to this file.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from deck import examples, primitives  # noqa: E402
from deck.slides import DECK  # noqa: E402


def build(output: Path) -> int:
    ex = examples.run_all()
    prs = primitives.new_presentation()
    for number, make in enumerate(DECK, start=1):
        slide = make(prs, ex)
        if number > 1:
            dark = slide.background.fill.fore_color.rgb != primitives.T.WHITE
            primitives.footer(slide, number, dark=dark)
    prs.core_properties.title = "What is an ontology? From RDF to OWL"
    prs.core_properties.subject = "Ontology, RDF, SPARQL, RDFS, SKOS and OWL"
    prs.save(output)
    return len(DECK)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("-o", "--output", type=Path, default=HERE / "ontology_review.pptx")
    args = parser.parse_args()
    count = build(args.output)
    print(f"Wrote {count} slides to {args.output}")


if __name__ == "__main__":
    main()

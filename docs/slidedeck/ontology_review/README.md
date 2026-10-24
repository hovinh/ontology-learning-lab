# Ontology review slide deck

A 54-slide introduction to ontologies for people meeting the idea for the first
time, built up through the Semantic Web standards from RDF to OWL. The main
reference is *Semantic Web for the Working Ontologist* (notes in
[references/working_ontologist_book.md](../../../references/working_ontologist_book.md)),
cited on the References slide rather than chapter by chapter.
Every code panel and result table on the slides comes from a small movie graph
that is executed with rdflib and owlrl at build time.

The slides are written to be read on their own, without a speaker.

| Part | Slides |
|---|---|
| 1. What is an ontology? | Definition, the four building blocks, the vocabulary-to-ontology spectrum, ontology vs. database schema |
| 2. Why we need ontologies | The problem they solve, then the Semantic Web motivation |
| 3. The building blocks, layer by layer | The stack, the uncovered layers in brief, one slide per layer (URI, RDF, RDFS, RDFS-Plus, OWL, SKOS, rules, SPARQL), then all layers answering one question, and a cheat sheet |
| 4–8. Deep dives | RDF and SPARQL; inference; vocabularies; OWL; modeling well |
| 9. Conclusions | Takeaways, references, glossary |

## Build

From the repository root (Windows, Python 3.11):

```powershell
py -3.11 -m venv .venv
.venv\Scripts\pip install pip-tools
.venv\Scripts\pip-sync requirements.txt

.venv\Scripts\python docs\slidedeck\ontology_review\build_deck.py
```

This writes `ontology_review.pptx` next to `build_deck.py`. Pass `-o path.pptx`
to write somewhere else.

To print every example and its result without building slides:

```powershell
cd docs\slidedeck\ontology_review
..\..\..\.venv\Scripts\python -m deck.examples
```

## Dependencies

`requirements.in` at the repository root lists the top-level packages, and
`requirements.txt` is the pip-tools lock file. To add or upgrade a package:

```powershell
.venv\Scripts\pip-compile --strip-extras requirements.in
.venv\Scripts\pip-sync requirements.txt
```

## Layout

| Path | What it holds |
|---|---|
| `build_deck.py` | Entry point: runs the examples, renders the slides |
| `deck/examples.py` | Loads `data/` and `queries/`, runs them, asserts the expected result |
| `deck/slides.py` | One function per slide, in deck order (`DECK` at the bottom) |
| `deck/primitives.py` | python-pptx helpers: cards, code panels, tables, RDF graph diagrams |
| `deck/theme.py` | Palette, fonts and sizes |
| `data/*.ttl` | The running example: studio catalogue, fan wiki, schema, SKOS genres, OWL model |
| `queries/*.rq` | SPARQL queries shown on the slides |
| `assets/semantic_web_stack.png` | W3C Semantic Web Stack, public domain, from [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Semantic_Web_Stack.png); the overlay boxes on slides 12 and 13 are pixel coordinates in this file (`W3C_LAYERS` and `W3C_UNCOVERED` in `slides.py`) |

## The running example

Two sources describe the same James Dean films under different names:

- `studio.ttl` uses `:JamesDean`; `fanwiki.ttl` uses `fan:Dean_James`.
- Merging them (Part 4) leaves two nodes. RDFS adds types and labels (Part 5).
  An inverse-functional `registryId` makes OWL RL infer `owl:sameAs` (Part 5).
- `genres_skos.ttl` adds a SKOS genre vocabulary (Part 6).
- `owl_model.ttl` adds a `hasValue` restriction and a max-cardinality
  restriction (Part 7) and a property chain (Part 8).
- `queries/together.rq` needs every layer at once. The build reruns it with each
  layer's file removed, and with no reasoner, and checks that every run returns
  zero rows (the "One question that needs every layer" slide).

Colour key on the slides: teal is asserted, amber is inferred, clay is a warning.

## Editing

- Change text or layout in `deck/slides.py`; restyle everything in `deck/theme.py`.
- Change the data or queries in `data/` and `queries/`. If a result changes,
  the matching assert in `deck/examples.py` will fail and tell you which slide
  to revisit.
- Speaker notes are set per slide with `P.notes(...)`.

"""Runnable examples behind the slides.

Every example loads Turtle from ``data/`` and SPARQL from ``queries/``, runs it
with rdflib (plus owlrl for RDFS / OWL RL inference) and returns what the slide
needs: the exact source text that ran and the rows it produced. Each example
also asserts the result it is meant to demonstrate, so a dependency upgrade
that changes behaviour breaks the build instead of silently changing a slide.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import owlrl
from owlrl.Namespaces import ERRNS
from rdflib import OWL, RDF, RDFS, Graph, Literal, Namespace, URIRef

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
QUERIES = ROOT / "queries"

STUDIO = Namespace("http://studio.example/")
FAN = Namespace("http://fanwiki.example/id/")
THEATRE = Namespace("http://theatre.example/")
GENRE = Namespace("http://studio.example/genre/")

PREFIXES = {
    ":": str(STUDIO),
    "fan:": str(FAN),
    "th:": str(THEATRE),
    "g:": str(GENRE),
    "rdfs:": str(RDFS),
    "owl:": str(OWL),
    "rdf:": str(RDF),
}


@dataclass
class Example:
    """Source text shown on a slide and the result it produced."""

    code: str
    rows: list[tuple[str, ...]] = field(default_factory=list)
    header: tuple[str, ...] = ()
    facts: dict[str, object] = field(default_factory=dict)


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def strip_comments(text: str) -> str:
    """Drop full-line comments and blank lines for compact on-slide display."""
    lines = [ln for ln in text.splitlines() if ln.strip() and not ln.lstrip().startswith("#")]
    return "\n".join(lines)


def load(*names: str) -> Graph:
    g = Graph()
    for name in names:
        g.parse(DATA / name, format="turtle")
    return g


def qname(term) -> str:
    """Render a term the way it is written on the slides."""
    if isinstance(term, Literal):
        return str(term)
    text = str(term)
    # Longest namespace first so "g:" wins over ":" for genre URIs.
    for prefix, ns in sorted(PREFIXES.items(), key=lambda kv: -len(kv[1])):
        if text.startswith(ns):
            return prefix + text[len(ns):]
    return f"<{text}>"


def select(g: Graph, query_file: str) -> tuple[tuple[str, ...], list[tuple[str, ...]]]:
    result = g.query(read_text(QUERIES / query_file))
    header = tuple(str(v) for v in result.vars)
    rows = [tuple(qname(v) for v in row) for row in result]
    return header, rows


def rdfs_closure(g: Graph) -> Graph:
    closed = Graph()
    for t in g:
        closed.add(t)
    owlrl.DeductiveClosure(owlrl.RDFS_Semantics, axiomatic_triples=False).expand(closed)
    return closed


def owl_rl_closure(g: Graph) -> Graph:
    closed = Graph()
    for t in g:
        closed.add(t)
    owlrl.DeductiveClosure(owlrl.OWLRL_Semantics, axiomatic_triples=False).expand(closed)
    return closed


def is_example_term(term) -> bool:
    return isinstance(term, Literal) or any(
        str(term).startswith(str(ns)) for ns in (STUDIO, FAN, THEATRE, GENRE)
    )


def interesting_inferred(before: Graph, after: Graph, predicates=None) -> list[tuple[str, str, str]]:
    """New triples about the example data, minus reflexive / bookkeeping noise."""
    rows = []
    for s, p, o in after - before:
        if predicates is not None and p not in predicates:
            continue
        if not (is_example_term(s) and is_example_term(o)):
            continue
        if p == OWL.sameAs and s == o:
            continue
        rows.append((qname(s), qname(p), qname(o)))
    return sorted(rows)


# --------------------------------------------------------------------------- #
# Ch 3: triples and merging
# --------------------------------------------------------------------------- #
def merge_sources() -> Example:
    studio = load("studio.ttl")
    fan = load("fanwiki.ttl")
    merged = studio + fan
    assert len(merged) == len(studio) + len(fan)  # no shared triples: union is a plain sum
    dean_nodes = sorted(
        qname(s) for s in set(merged.subjects()) if "Dean" in str(s)
    )
    assert dean_nodes == [":JamesDean", "fan:Dean_James"]
    return Example(
        code=strip_comments(read_text(DATA / "fanwiki.ttl")),
        facts={
            "studio": len(studio),
            "fan": len(fan),
            "merged": len(merged),
            "dean_nodes": dean_nodes,
        },
    )


def table_to_triples() -> Example:
    """The first studio movie as a table row and as triples."""
    g = load("studio.ttl")
    movie = STUDIO.RebelWithoutACause
    order = [STUDIO.movieTitle, STUDIO.releaseYear, STUDIO.directedBy]
    rows = [(qname(movie), qname(p), qname(g.value(movie, p))) for p in order]
    rows += [(qname(movie), qname(STUDIO.starring), qname(o))
             for o in sorted(g.objects(movie, STUDIO.starring))]
    assert len(rows) == 5
    return Example(code="", rows=rows, header=("subject", "predicate", "object"))


def turtle_snippet() -> Example:
    text = read_text(DATA / "studio.ttl")
    # Show only the prefix line and the first movie block.
    lines = text.splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.startswith(":RebelWithoutACause"))
    block = []
    for ln in lines[start:]:
        block.append(ln)
        if ln.rstrip().endswith("."):
            break
    code = lines[1] + "\n\n" + "\n".join(block)
    return Example(code=code)


# --------------------------------------------------------------------------- #
# Ch 5: SPARQL
# --------------------------------------------------------------------------- #
def sparql_select() -> Example:
    g = load("studio.ttl")
    header, rows = select(g, "dean_movies.rq")
    assert [r[0] for r in rows] == ["East of Eden", "Rebel Without a Cause", "Giant"]
    return Example(code=strip_comments(read_text(QUERIES / "dean_movies.rq")), rows=rows, header=header)


def sparql_explore() -> Example:
    g = load("fanwiki.ttl")
    header, rows = select(g, "explore.rq")
    assert ("fan:bornIn",) in rows
    return Example(code=read_text(QUERIES / "explore.rq"), rows=rows, header=header)


def sparql_construct() -> Example:
    g = load("studio.ttl")
    built = g.query(read_text(QUERIES / "construct_worked_with.rq")).graph
    rows = sorted((qname(s), qname(p), qname(o)) for s, p, o in built if s == STUDIO.JamesDean)
    assert len(rows) == 3
    return Example(
        code=read_text(QUERIES / "construct_worked_with.rq"),
        rows=rows,
        header=("subject", "predicate", "object"),
        facts={"total": len(built)},
    )


# --------------------------------------------------------------------------- #
# Ch 6-7: RDFS inference
# --------------------------------------------------------------------------- #
def rdfs_type_propagation() -> Example:
    asserted = load("studio.ttl", "schema_rdfs.ttl")
    closed = rdfs_closure(asserted)
    people_before = set(asserted.subjects(RDF.type, STUDIO.Person))
    people_after = sorted(qname(s) for s in closed.subjects(RDF.type, STUDIO.Person))
    assert not people_before and ":JamesDean" in people_after
    inferred = interesting_inferred(asserted, closed, predicates={RDF.type})
    return Example(
        code=strip_comments(read_text(DATA / "schema_rdfs.ttl")),
        rows=[r for r in inferred if r[0] in (":JamesDean", ":NicholasRay")],
        header=("subject", "predicate", "object"),
        facts={
            "asserted": len(asserted),
            "people_after": people_after,
            "inferred_types": len(inferred),
        },
    )


def rdfs_labels() -> Example:
    closed = rdfs_closure(load("studio.ttl", "schema_rdfs.ttl"))
    header, rows = select(closed, "labels.rq")
    assert ("rdfs:label" not in {r[1] for r in rows}) and len(rows) == 10
    return Example(code=read_text(QUERIES / "labels.rq"), rows=rows, header=header)


def rdfs_domain_trap() -> Example:
    asserted = load("studio.ttl", "schema_rdfs.ttl", "theatre.ttl")
    closed = rdfs_closure(asserted)
    play = THEATRE.StreetcarNamedDesire1947
    assert (play, RDF.type, STUDIO.Movie) in closed
    return Example(
        code=strip_comments(read_text(DATA / "theatre.ttl")),
        rows=[(qname(play), "rdf:type", qname(STUDIO.Movie))],
        header=("subject", "predicate", "object"),
    )


# --------------------------------------------------------------------------- #
# Ch 8: RDFS-Plus sameness
# --------------------------------------------------------------------------- #
def rdfs_plus_same_as() -> Example:
    asserted = load("studio.ttl", "fanwiki.ttl", "alignment_rdfsplus.ttl")
    _, before = select(asserted, "born.rq")
    closed = owl_rl_closure(asserted)
    assert (FAN.Dean_James, OWL.sameAs, STUDIO.JamesDean) in closed
    header, rows = select(closed, "born.rq")
    assert before == [] and rows == [("Giant", "Marion, Indiana")]
    return Example(
        code=strip_comments(read_text(DATA / "alignment_rdfsplus.ttl")),
        rows=rows,
        header=header,
        facts={"before_rows": len(before), "query": strip_comments(read_text(QUERIES / "born.rq"))},
    )


# --------------------------------------------------------------------------- #
# Ch 10: SKOS
# --------------------------------------------------------------------------- #
def skos_drama() -> Example:
    g = load("studio.ttl", "genres_skos.ttl")
    header, rows = select(g, "drama_movies.rq")
    assert {r[0] for r in rows} == {"East of Eden", "Giant", "Rebel Without a Cause"}
    lines = read_text(DATA / "genres_skos.ttl").splitlines()
    start = lines.index("g:TeenDrama a skos:Concept ;")
    block = lines[start:start + 4]
    assert block[-1].rstrip().endswith(".")
    tagged = next(ln for ln in lines if ln.startswith(":RebelWithoutACause"))
    snippet = "\n".join(block + ["", " ".join(tagged.split())])
    return Example(code=strip_comments(read_text(QUERIES / "drama_movies.rq")), rows=rows, header=header,
                   facts={"snippet": snippet})


# --------------------------------------------------------------------------- #
# Ch 11, 12, 15: OWL
# --------------------------------------------------------------------------- #
def owl_closure_of_model() -> tuple[Graph, Graph]:
    asserted = load("studio.ttl", "fanwiki.ttl", "fanwiki_giant.ttl", "owl_model.ttl")
    return asserted, owl_rl_closure(asserted)


def owl_has_value() -> Example:
    asserted, closed = owl_closure_of_model()
    members = sorted(qname(s) for s in closed.subjects(RDF.type, STUDIO.JamesDeanMovie))
    assert members == [":EastOfEden", ":Giant", ":RebelWithoutACause"]
    model = read_text(DATA / "owl_model.ttl").split("# Ch 12")[0]
    return Example(
        code=strip_comments(model.split("# Ch 11")[1].split("\n", 1)[1]),
        rows=[(m, "rdf:type", ":JamesDeanMovie") for m in members],
        header=("subject", "predicate", "object"),
    )


def owl_max_cardinality() -> Example:
    asserted, closed = owl_closure_of_model()
    assert (STUDIO.GeorgeStevens, OWL.sameAs, FAN.G_Stevens) in closed
    # Close the world on purpose: say the two names are different people.
    contradicted = Graph()
    for t in asserted:
        contradicted.add(t)
    contradicted.add((STUDIO.GeorgeStevens, OWL.differentFrom, FAN.G_Stevens))
    checked = owl_rl_closure(contradicted)
    errors = sorted(str(o) for o in checked.objects(None, ERRNS.error))
    pair = [e for e in errors if str(STUDIO.GeorgeStevens) in e and str(FAN.G_Stevens) in e]
    assert pair, "expected OWL RL to report an inconsistency"
    model = read_text(DATA / "owl_model.ttl").split("# Ch 12")[1].split("# Ch 15")[0]
    return Example(
        code=strip_comments(model.split("\n", 1)[1]) + "\n\n"
        + strip_comments(read_text(DATA / "fanwiki_giant.ttl")).split("\n", 2)[2],
        rows=[(":GeorgeStevens", "owl:sameAs", "fan:G_Stevens")],
        header=("subject", "predicate", "object"),
        facts={"error": pair[0], "error_count": len(errors)},
    )


def owl_property_chain() -> Example:
    # Studio data only, so the fan wiki's second name for George Stevens stays out.
    closed = owl_rl_closure(load("studio.ttl", "owl_model.ttl"))
    rows = sorted(
        (qname(s), qname(p), qname(o))
        for s, p, o in closed.triples((STUDIO.JamesDean, STUDIO.workedWith, None))
    )
    construct = sparql_construct()
    assert rows == construct.rows, "OWL chain and SPARQL rule should agree"
    model = read_text(DATA / "owl_model.ttl").split("# Ch 15")[1]
    return Example(
        code=strip_comments(model.split("\n", 1)[1]),
        rows=rows,
        header=("subject", "predicate", "object"),
    )


# --------------------------------------------------------------------------- #
# Ch 14: competency questions as executable tests
# --------------------------------------------------------------------------- #
COMPETENCY_QUESTIONS = [
    ("Which movies did James Dean star in?",
     "ASK { ?m :starring :JamesDean }"),
    ("Are directors people too?",
     "ASK { :NicholasRay a :Person }"),
    ("Can a generic UI label any movie?",
     "ASK { :Giant rdfs:label ?l }"),
    ("Which awards did a movie win?",
     "ASK { ?m :wonAward ?a }"),
]


def competency_questions() -> Example:
    g = rdfs_closure(load("studio.ttl", "schema_rdfs.ttl"))
    prologue = f"PREFIX : <{STUDIO}>\nPREFIX rdfs: <{RDFS}>\n"
    rows = []
    for question, ask in COMPETENCY_QUESTIONS:
        answer = bool(g.query(prologue + ask).askAnswer)
        rows.append((question, ask, "pass" if answer else "fail"))
    assert [r[2] for r in rows] == ["pass", "pass", "pass", "fail"]
    return Example(code="", rows=rows, header=("Competency question", "SPARQL ASK", "Result"))


# --------------------------------------------------------------------------- #
# All layers together: one question that needs every layer
# --------------------------------------------------------------------------- #
TOGETHER_DATA = ["studio.ttl", "fanwiki.ttl"]
TOGETHER_MODEL = {
    "RDFS": "schema_rdfs.ttl",
    "RDFS-Plus": "alignment_rdfsplus.ttl",
    "OWL": "owl_model.ttl",
    "SKOS": "genres_skos.ttl",
}


def together() -> Example:
    files = TOGETHER_DATA + list(TOGETHER_MODEL.values())
    asserted = load(*files)
    closed = owl_rl_closure(asserted)
    header, rows = select(closed, "together.rq")
    assert rows == [
        ("James Dean", "Marion, Indiana", "Elia Kazan"),
        ("James Dean", "Marion, Indiana", "George Stevens"),
        ("James Dean", "Marion, Indiana", "Nicholas Ray"),
    ]
    # Take one layer away at a time: the question should stop being answerable.
    ablations = [("No reasoner: asserted triples only", len(select(asserted, "together.rq")[1]))]
    for layer, name in TOGETHER_MODEL.items():
        rest = [f for f in files if f != name]
        ablations.append((f"Without {layer} ({name})",
                          len(select(owl_rl_closure(load(*rest)), "together.rq")[1])))
    assert all(n == 0 for _, n in ablations)
    # The query body, one pattern per row, with the layer named in its trailing comment.
    lines = []
    for ln in read_text(QUERIES / "together.rq").splitlines():
        pattern, _, layer = ln.partition("#")
        if pattern.strip().startswith("?") and layer:
            lines.append((pattern.strip(), layer.strip()))
    data = load(*TOGETHER_DATA)
    model = load(*TOGETHER_MODEL.values())
    return Example(
        code=strip_comments(read_text(QUERIES / "together.rq")),
        rows=rows,
        header=header,
        facts={
            "lines": lines,
            "ablations": ablations,
            "data": len(data),
            "model": len(model),
            "asserted": len(asserted),
            "inferred": len(interesting_inferred(asserted, closed)),
        },
    )


def run_all() -> dict[str, Example]:
    return {
        "merge": merge_sources(),
        "table": table_to_triples(),
        "turtle": turtle_snippet(),
        "select": sparql_select(),
        "explore": sparql_explore(),
        "construct": sparql_construct(),
        "subclass": rdfs_type_propagation(),
        "labels": rdfs_labels(),
        "domain_trap": rdfs_domain_trap(),
        "same_as": rdfs_plus_same_as(),
        "skos": skos_drama(),
        "has_value": owl_has_value(),
        "max_card": owl_max_cardinality(),
        "chain": owl_property_chain(),
        "cq": competency_questions(),
        "together": together(),
    }


if __name__ == "__main__":
    for name, ex in run_all().items():
        print(f"== {name} ==")
        if ex.code:
            print(ex.code)
            print("--")
        for row in ex.rows:
            print("   ", row)
        if ex.facts:
            print("    facts:", ex.facts)

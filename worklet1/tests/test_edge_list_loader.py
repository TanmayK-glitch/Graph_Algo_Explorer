"""EdgeListLoader tests: valid files, every malformed case, both representations."""

from pathlib import Path

import pytest

from worklet1.graph import AdjacencyListGraph, AdjacencyMatrixGraph
from worklet1.io import EdgeListFormatError, EdgeListLoader

SAMPLES = Path(__file__).resolve().parent.parent / "sample_graphs"


def write(tmp_path, text, name="g.edgelist"):
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return p


def test_load_design_example_weighted_directed():
    g = EdgeListLoader.load(SAMPLES / "weighted_directed.edgelist")
    assert isinstance(g, AdjacencyListGraph)  # default representation (DD-02)
    assert g.is_directed and g.is_weighted
    assert g.vertices == ["A", "B", "C", "D"]
    assert g.edge_weight("A", "B") == 4.0 and g.edge_weight("C", "D") == 5.0
    assert g.edge_count() == 4


def test_load_into_matrix(GraphClass):
    g = EdgeListLoader.load(SAMPLES / "weighted_directed.edgelist", graph_class=GraphClass)
    assert isinstance(g, GraphClass) and g.edge_count() == 4


def test_isolated_vertex_and_trailing_comment():
    g = EdgeListLoader.load(SAMPLES / "undirected_components.edgelist")
    assert g.vertices == ["A", "B", "C", "D", "E"]
    assert g.neighbours("E") == [] and not g.is_directed and not g.is_weighted


def test_negative_weights_loaded():
    g = EdgeListLoader.load(SAMPLES / "negative_weights.edgelist")
    assert g.edge_weight("A", "B") == -2.5


def test_self_loop_file():
    g = EdgeListLoader.load(SAMPLES / "self_loop.edgelist")
    assert g.has_edge("A", "A")


def test_comments_blank_lines_bom_and_crlf(tmp_path):
    p = tmp_path / "x.edgelist"
    p.write_bytes(b"\xef\xbb\xbf# hi\r\n\r\nUNDIRECTED # kind\r\n  UNWEIGHTED\r\n\r\nA B # edge\r\n")
    g = EdgeListLoader.load(p)
    assert g.has_edge("A", "B")


def test_header_only_file_gives_empty_graph(tmp_path):
    g = EdgeListLoader.load(write(tmp_path, "DIRECTED\nWEIGHTED\n"))
    assert g.vertices == [] and g.is_directed and g.is_weighted


def test_numeric_ids_are_strings(tmp_path):
    g = EdgeListLoader.load(write(tmp_path, "UNDIRECTED\nUNWEIGHTED\n1 2\n"))
    assert g.vertices == ["1", "2"]


def test_accepts_str_path(tmp_path):
    p = write(tmp_path, "UNDIRECTED\nUNWEIGHTED\nA B\n")
    assert EdgeListLoader.load(str(p)).has_edge("A", "B")


def test_missing_file_raises_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        EdgeListLoader.load(tmp_path / "nope.edgelist")


@pytest.mark.parametrize("name,expected_line", [
    ("no_header", 1), ("bad_direction_header", 1), ("missing_weight", 4),
    ("bad_weight", 3), ("extra_field", 3), ("duplicate_edge", 4), ("nan_weight", 3),
])
def test_malformed_reports_exact_line(name, expected_line):
    with pytest.raises(EdgeListFormatError) as info:
        EdgeListLoader.load(SAMPLES / "malformed" / f"{name}.edgelist")
    assert info.value.line_number == expected_line


def test_empty_file_rejected():
    with pytest.raises(EdgeListFormatError):
        EdgeListLoader.load(SAMPLES / "malformed" / "empty.edgelist")


def test_lowercase_header_rejected(tmp_path):
    with pytest.raises(EdgeListFormatError):
        EdgeListLoader.load(write(tmp_path, "directed\nunweighted\nA B\n"))


def test_weighted_edge_in_unweighted_file_rejected(tmp_path):
    with pytest.raises(EdgeListFormatError):
        EdgeListLoader.load(write(tmp_path, "DIRECTED\nUNWEIGHTED\nA B 2.0\n"))


def test_headers_in_wrong_order_rejected(tmp_path):
    with pytest.raises(EdgeListFormatError):
        EdgeListLoader.load(write(tmp_path, "WEIGHTED\nDIRECTED\nA B 1\n"))


def test_line_number_counts_comments_and_blanks(tmp_path):
    with pytest.raises(EdgeListFormatError) as info:
        EdgeListLoader.load(write(tmp_path, "# c\n\nDIRECTED\nWEIGHTED\n\nA B x\n"))
    assert info.value.line_number == 6


def test_directory_path_rejected(tmp_path):
    with pytest.raises(OSError):
        EdgeListLoader.load(tmp_path)


def test_matrix_and_list_load_identically():
    a = EdgeListLoader.load(SAMPLES / "scc_example.edgelist", AdjacencyListGraph)
    b = EdgeListLoader.load(SAMPLES / "scc_example.edgelist", AdjacencyMatrixGraph)
    assert a.vertices == b.vertices and a.all_edges() == b.all_edges()

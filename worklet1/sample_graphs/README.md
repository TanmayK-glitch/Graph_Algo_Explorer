# Sample graphs (edge-list format v1 - PROPOSED, pending Worklet 2/3 sign-off)

    # comment lines and trailing "# ..." comments are ignored
    DIRECTED | UNDIRECTED      first non-comment line
    WEIGHTED | UNWEIGHTED      second non-comment line
    u v [weight]               edge; weight present iff WEIGHTED
    v                          isolated vertex (single token)

Vertex ids are whitespace-free strings. `malformed/` holds files that the loader must reject
with `EdgeListFormatError` (a `ValueError` that names the line number).

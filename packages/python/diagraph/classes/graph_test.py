from .graph import Graph


def test_it_builds_empty_graph():
    Graph({})


def test_it_builds_connected_directed_graph():
    graph = Graph({"a": ["b"], "b": ["c"]})

    dump = graph.to_json()
    assert dump.get("links") == [
        {
            "source": graph.get_int_key_for_node("a"),
            "target": graph.get_int_key_for_node("b"),
        },
        {
            "source": graph.get_int_key_for_node("b"),
            "target": graph.get_int_key_for_node("c"),
        },
    ]


# def test_it_raises_for_a_slice():
#     graph = Graph({"a": ["b"], "b": ["c"]})

#     with pytest.raises(Exception):
#         graph[1:2]

#     with pytest.raises(Exception):
#         graph[1:2:2]



def test_it_can_update_nodes():
    graph = Graph({"a": ["b"], "b": ["c"]})

    graph["a"] = "d"

    dump = graph.to_json()
    assert dump.get("links") == [
        {
            "source": graph.get_int_key_for_node("d"),
            "target": graph.get_int_key_for_node("b"),
        },
        {
            "source": graph.get_int_key_for_node("b"),
            "target": graph.get_int_key_for_node("c"),
        },
    ]


def test_it_can_get_in_edges():
    graph = Graph({"a": ["b"], "b": ["c"]})

    assert graph.in_edges("c") == ["b"]
    assert graph.in_edges("b") == ["a"]

    graph = Graph({"a": ["b"], "b": ["c"], "d": ["c"]})

    assert graph.in_edges("c") == ["b", "d"]


def test_it_can_get_out_edges():
    graph = Graph({"a": ["b", "d"], "b": ["c"], "d": ["c"]})

    assert graph.out_edges("a") == ["b", "d"]
    assert graph.out_edges("b") == ["c"]
    assert graph.out_edges("d") == ["c"]


# def test_it_returns_a_copy_of_itself():
#     graph = Graph({"a": ["b"], "b": ["c"]})
#     graph_2 = graph[:]

#     graph["a"] = "d"
#     graph_2["a"] = "e"

#     assert graph.to_json().get("links") == [
#         {
#             "source": graph.get_int_key_for_node("d"),
#             "target": graph.get_int_key_for_node("b"),
#         },
#         {
#             "source": graph.get_int_key_for_node("b"),
#             "target": graph.get_int_key_for_node("c"),
#         },
#     ]
#     assert graph_2.to_json().get("links") == [
#         {
#             "source": graph_2.get_int_key_for_node("e"),
#             "target": graph_2.get_int_key_for_node("b"),
#         },
#         {
#             "source": graph_2.get_int_key_for_node("b"),
#             "target": graph_2.get_int_key_for_node("c"),
#         },
#     ]

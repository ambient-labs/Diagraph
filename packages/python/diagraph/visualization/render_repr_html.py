from __future__ import annotations

import inspect
import json
import random
from importlib import resources
from importlib.metadata import distribution

import networkx as nx

diagraph_version = distribution("diagraph").metadata["version"]


def load_from_dist(url: str):
    return load_resource(f"./assets/dist/{url}")


def load_resource(resource_filepath: str, pkg="diagraph") -> str:
    ref = resources.files(pkg).joinpath(resource_filepath)
    with ref.open("r") as f:
        return f.read()


def render_repr_html(diagraph):
    G = diagraph.__graph__.__G__

    graph = {}
    nodes = []
    links = nx.node_link_data(G)["links"]
    if len(links) == 0:
        for int_key in nx.topological_sort(G):
            fn = diagraph.__graph__.get_node_for_int_key(int_key)
            graph[fn.__name__] = []
    else:
        for link in links:
            source = link.get("source")
            target = link.get("target")
            if graph.get(target) is None:
                graph[target] = []
            graph[target].append(source)
        if len(graph.keys()) == 0:
            raise Exception("Empty graph")

    for fn in diagraph.__graph__.get_nodes():
        int_key = str(diagraph.__graph__.get_int_key_for_node(fn))
        node = diagraph[fn]
        node_definition = {
            "id": int_key,
            "label": fn.__name__,
            "fn": inspect.getsource(fn),
            "prompt": "",
            "result": "",
        }
        if node.__is_decorated__:
            try:
                node_definition["prompt"] = node.prompt
            except Exception:
                pass
        try:
            node_definition["result"] = node.result
        except Exception:
            pass
        nodes.append(node_definition)

    # fn = diagraph.__graph__.get_node_for_int_key(0)
    # graph = json.dumps(graph)

    style = load_from_dist("style.css")
    script = load_from_dist("diagraph-visualizer.umd.cjs")

    props = json.dumps(
        {
            "nodes": nodes,
            "graph": graph,
            "version": diagraph_version,
        },
    )
    random_number = random.randint(0, 100000000)
    root_id = f"root-{random_number}"
    style = (
        "#"
        + root_id
        + """ {
  width: 100%;
    min-height: 600px;
    display: flex;
    align-items: stretch;
}
"""
        + style
    )
    return f"""

    <style>{style}</style>

        <script type="module">{script}</script>

<div id="{root_id}"></div>
    <script type="module">

    renderDiagraphVisualization(document.getElementById('{root_id}'), {props})
    </script>

         """

    # <script type="module">{fe}</script>
    # <div style="min-height: 600px; width: 100%; display: flex; flex: 1;">
    #  <diagraph-template graph='{graph}' style="position: absolute;">
    #  </diagraph-template>
    #  </div>

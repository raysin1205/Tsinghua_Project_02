import numpy as np
import pandas as pd
import networkx as nx

from config import alpha, beta

def build_directed_edges(edges_data: pd.DataFrame):
    rows = []
    for _,row in edges_data.iterrows():
        base = row.to_dict()
        
        forward = base.copy()
        forward["edge_id"] = base["edge_id"] + "f"
        forward["from_node"] = base["from_node"]
        forward["to_node"] = base["to_node"]

        rows.append(forward)

        if row["bidirectional"]:
            backword = base.copy()

            backword = base.copy()
            backword["edge_id"] = base["edge_id"] + "b"
            backword["from_node"] = base["to_node"]
            backword["to_node"] = base["from_node"]

            rows.append(backword)
    
    directed_edges = pd.DataFrame(rows)
    directed_edges["t0"] = directed_edges["length_m"] / directed_edges["free_speed"]
    directed_edges["closed"] = False

    return directed_edges


def bpr_time(t0, flow, capacity, alpha=alpha, beta=beta):

    t0 = np.asarray(t0, dtype=float)
    flow = np.asarray(flow, dtype=float)
    capacity = np.asarray(capacity, dtype=float)

    result = t0 * (1 + alpha *( (flow / capacity) ** beta))
    return result


def close_edges_by_node_pairs(directed_edges: pd.DataFrame, closed_node_pairs):

    directed_edges = directed_edges.copy()

    for from_node, to_node in closed_node_pairs:
        mask = (
            (directed_edges["from_node"] == from_node)
            & (directed_edges["to_node"] == to_node)
        )
        directed_edges.loc[mask, "closed"] = True

    return directed_edges


def get_closed_edge_ids(edges: pd.DataFrame):
    return edges.loc[edges["closed"], "edge_id"].tolist()


def build_graph(edges: pd.DataFrame):
    graph = nx.DiGraph()

    available_edges = edges[~edges["closed"]]
    for _, row in available_edges.iterrows():
        graph.add_edge(
            row["from_node"],
            row["to_node"],
            edge_id=row["edge_id"],
            t0=row["t0"],
            road_name = row["road_name"],
            length_m = row["length_m"],
            lanes = row["lanes"],
            road_class  = row["road_class"],
            capacity = row["capacity"],
            free_speed  = ["free_speed "],
        )  
        
    return graph
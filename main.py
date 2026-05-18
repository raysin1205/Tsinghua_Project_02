from data_loader import load_all_data
from network_model import build_directed_edges, bpr_time, close_edges_by_node_pairs, get_closed_edge_ids, build_graph
from config import BLOCKED_NODE_PAIRS


def main():
    nodes, edges, od_pairs, release_curve = load_all_data()

    print(edges["bidirectional"].head())
    print(edges["bidirectional"].dtype)
    print(edges["bidirectional"].unique())

    directed_edges = build_directed_edges(edges)

    print("Original edges:", edges.shape)
    print("Directed edges:", directed_edges.shape)

    print(directed_edges[["edge_id", "from_node", "to_node"]].head(10))
    print(
    directed_edges[
        ["edge_id", "from_node", "to_node", "length_m", "free_speed", "t0"]
    ].head(10)
    )
    print("\nBPR test:")
    print("flow = 0:", bpr_time(2.0, 0, 100))
    print("flow = 100:", bpr_time(2.0, 100, 100))
    print("flow = 200:", bpr_time(2.0, 200, 100))

    blocked_edges = close_edges_by_node_pairs(directed_edges, BLOCKED_NODE_PAIRS)

    print("\nClosed edge ids:")
    print(get_closed_edge_ids(blocked_edges))

    print("\nClosed rows:")
    print(
        blocked_edges.loc[
            blocked_edges["closed"],
            ["edge_id", "from_node", "to_node", "closed"]
        ]
    )
    graph = build_graph(directed_edges)
    blocked_graph = build_graph(blocked_edges)

    print("\nGraph nodes:", graph.number_of_nodes())
    print("Graph edges:", graph.number_of_edges())

    print("\nBlocked graph nodes:", blocked_graph.number_of_nodes())
    print("Blocked graph edges:", blocked_graph.number_of_edges())

if __name__ == "__main__":
    main()
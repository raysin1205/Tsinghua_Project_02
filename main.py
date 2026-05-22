from data_loader import load_all_data
from network_model import build_directed_edges, bpr_time, close_edges_by_node_pairs, get_closed_edge_ids, build_graph
from config import BLOCKED_NODE_PAIRS, OUTPUT_DIR
import networkx as nx
from assignment import node_path_to_edge_path, aon_assignment, compute_static_metrics
from dynamics import prepare_edge_index, prepare_source_vector, prepare_turn_matrix, release_rate
import numpy as np

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
    node_path = nx.shortest_path(graph, source="T01", target="C01", weight="t0")
    edge_path = node_path_to_edge_path(graph, node_path)

    print("\nExample shortest node path:")
    print(node_path)

    print("\nExample shortest edge path:")
    print(edge_path)
    edge_results, od_paths = aon_assignment(graph, directed_edges, od_pairs)

    print("\nAON result:")
    print("Number of OD paths:", len(od_paths))
    print("Total demand:", od_pairs["demand"].sum())
    print("Total edge flow:", edge_results["flow"].sum())

    print("\nTop 10 edges by flow:")
    print(
        edge_results.sort_values("flow", ascending=False)[
            ["edge_id", "from_node", "to_node", "flow", "capacity"]
        ].head(10)
    )

    metrics = compute_static_metrics(edge_results)

    print("\nStatic metrics:")
    print(metrics)

    top10 = edge_results.sort_values("v_c_ratio", ascending=False).head(10)

    print("\nTop 10 congested edges:")
    print(
        top10[
            [
                "edge_id",
                "from_node",
                "to_node",
                "road_name",
                "flow",
                "capacity",
                "v_c_ratio",
                "travel_time",
            ]
        ]
    )
    OUTPUT_DIR.mkdir(exist_ok=True)

    task2_output = edge_results.sort_values("v_c_ratio", ascending=False)
    task2_output.to_csv(OUTPUT_DIR / "task2_edges_normal.csv", index=False)

    edge_id_to_idx, idx_to_edge_id = prepare_edge_index(directed_edges)

    source_vector = prepare_source_vector(
        directed_edges,
        od_pairs,
        od_paths,
        edge_id_to_idx,
    )

    print("\nODE source vector test:")
    print("Number of edges:", len(edge_id_to_idx))
    print("Source vector length:", len(source_vector))
    print("Total source demand:", source_vector.sum())
    print("Total OD demand:", od_pairs["demand"].sum())
    print("Nonzero source edges:", (source_vector > 0).sum())

    turn_matrix = prepare_turn_matrix(
    directed_edges,
    od_pairs,
    od_paths,
    edge_id_to_idx,
    )

    print("\nODE turn matrix test:")
    print("Turn matrix shape:", turn_matrix.shape)
    print("Nonzero turns:", turn_matrix.nnz)

    row_sums = np.array(turn_matrix.sum(axis=1)).ravel()

    print("Max row sum:", row_sums.max())
    print("Rows with positive turns:", (row_sums > 0).sum())

    print("\nRelease curve test:")
    for t in [0, 1, 2.5, 5, 8, 20]:
        print(t, release_rate(t, release_curve))

    area = np.trapezoid(
        release_curve["release_rate"].values,
        release_curve["t_minute"].values,
    )
    print("Release curve area:", area)



    
if __name__ == "__main__":
    main()
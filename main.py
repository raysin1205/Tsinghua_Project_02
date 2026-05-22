from data_loader import load_all_data
from network_model import (
    build_directed_edges,
    build_graph,
    close_edges_by_node_pairs,
)
from assignment import (
    aon_assignment,
    compute_static_metrics,
    format_task2_edges_output,
)
from dynamics import (
    compute_dynamic_metrics,
    prepare_edge_index,
    prepare_source_vector,
    prepare_turn_matrix,
    run_ode_simulation,
)
from visualization import plot_total_in_net, plot_top_edges_dynamic_curves
from config import OUTPUT_DIR, BLOCKED_NODE_PAIRS



def main():
    nodes, edges, od_pairs, release_curve = load_all_data()

# 读取 /data 数据并检查
    print("Data loaded successfully.")
    print("nodes:", nodes.shape)
    print("edges:", edges.shape)
    print("od_pairs:", od_pairs.shape)
    print("release_curve:", release_curve.shape)

# 路网构建与检查
    directed_edges = build_directed_edges(edges)
    graph = build_graph(directed_edges)

    print("directed_edges:", directed_edges.shape)
    print("graph nodes:", graph.number_of_nodes())
    print("graph edges:", graph.number_of_edges())

# AON 和 BPR import
    edge_results, od_paths = aon_assignment(graph, directed_edges, od_pairs)
    static_metrics = compute_static_metrics(edge_results)

    print("\nTask 2 completed: AON assignment and BPR metrics.")
    print("Number of OD paths:", len(od_paths))
    print("Static metrics:", static_metrics)

    top10_congested = edge_results.sort_values("v_c_ratio", ascending=False).head(10)

# Top10
    print("\nTop 10 congested edges:")
    print(
        top10_congested[
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

# edges_normal.csv 生成
    OUTPUT_DIR.mkdir(exist_ok=True)

    task2_output = format_task2_edges_output(edge_results)
    task2_output.to_csv(
        OUTPUT_DIR / "task2_edges_normal.csv",
        index=False,
        encoding="utf-8-sig",
    )

# 动态ODE实现
    edge_id_to_idx, idx_to_edge_id = prepare_edge_index(directed_edges)

    source_vector = prepare_source_vector(
        directed_edges,
        od_pairs,
        od_paths,
        edge_id_to_idx,
    )

    turn_matrix = prepare_turn_matrix(
        directed_edges,
        od_pairs,
        od_paths,
        edge_id_to_idx,
    )

    sol = run_ode_simulation(
        directed_edges,
        source_vector,
        turn_matrix,
        release_curve,
    )

    dynamic_metrics = compute_dynamic_metrics(sol, od_pairs["demand"].sum())

    print("\nTask 3 completed: ODE dynamic simulation.")
    print("Dynamic metrics:", dynamic_metrics)

# Task03 要求的 task3_total_in_net.png 和 task3_dynamic_curves.png 图片生成
    plot_total_in_net(
        sol,
        OUTPUT_DIR / "task3_total_in_net.png",
    )

    top5_edge_ids = (
        edge_results.sort_values("v_c_ratio", ascending=False)
        .head(5)["edge_id"]
        .tolist()
    )

    plot_top_edges_dynamic_curves(
        sol,
        top5_edge_ids,
        edge_id_to_idx,
        OUTPUT_DIR / "task3_dynamic_curves.png",
    )


# BLOCKED 封路场景对比
    blocked_edges = close_edges_by_node_pairs(directed_edges, BLOCKED_NODE_PAIRS)
    blocked_graph = build_graph(blocked_edges)

    blocked_edge_results, blocked_od_paths = aon_assignment(
        blocked_graph,
        blocked_edges,
        od_pairs,
    )
    blocked_static_metrics = compute_static_metrics(blocked_edge_results)

    blocked_task2_output = format_task2_edges_output(blocked_edge_results)
    blocked_task2_output.to_csv(
        OUTPUT_DIR / "task2_edges_blocked.csv",
        index=False,
        encoding="utf-8-sig",
    )

    blocked_edge_id_to_idx, _ = prepare_edge_index(blocked_edges)

    blocked_source_vector = prepare_source_vector(
        blocked_edges,
        od_pairs,
        blocked_od_paths,
        blocked_edge_id_to_idx,
    )

    blocked_turn_matrix = prepare_turn_matrix(
        blocked_edges,
        od_pairs,
        blocked_od_paths,
        blocked_edge_id_to_idx,
    )

    blocked_sol = run_ode_simulation(
        blocked_edges,
        blocked_source_vector,
        blocked_turn_matrix,
        release_curve,
    )

    blocked_dynamic_metrics = compute_dynamic_metrics(
        blocked_sol,
        od_pairs["demand"].sum(),
    )


    print("\nTask 4 completed: blocked scenario simulation.")
    print("Blocked static metrics:", blocked_static_metrics)
    print("Blocked dynamic metrics:", blocked_dynamic_metrics)

    print("\nScenario comparison:")
    print("Normal static TSTT:", static_metrics["static_tstt"])
    print("Blocked static TSTT:", blocked_static_metrics["static_tstt"])
    print("Normal dynamic TSTT:", dynamic_metrics["dynamic_tstt"])
    print("Blocked dynamic TSTT:", blocked_dynamic_metrics["dynamic_tstt"])
    print("Normal saturated edges:", static_metrics["saturated_count"])
    print("Blocked saturated edges:", blocked_static_metrics["saturated_count"])









if __name__ == "__main__":
    main()
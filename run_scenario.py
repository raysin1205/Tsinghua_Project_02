from network_model import (
    build_directed_edges,
    build_graph,
    close_edges_by_node_pairs,
)

from assignment import (
    aon_assignment,
    compute_static_metrics,
)

from dynamics import (
    compute_dynamic_metrics,
    prepare_edge_index,
    prepare_source_vector,
    prepare_turn_matrix,
    run_ode_simulation,
)


# 为 Bonus2 以及 代码整体模块化 def 的一个提供场景的运行仿真计算的函数
def run_scenario(scenario_name, edges, od_pairs, release_curve, closed_node_pairs=None,):

    # 路网构建与检查
    directed_edges = build_directed_edges(edges)

    if closed_node_pairs is not None:
        directed_edges = close_edges_by_node_pairs(directed_edges, closed_node_pairs)

    graph = build_graph(directed_edges)

    # AON 和 BPR 实现
    edge_results, od_paths = aon_assignment(graph, directed_edges, od_pairs)
    static_metrics = compute_static_metrics(edge_results)

    # 动态ODE实现
    edge_id_to_idx, _ = prepare_edge_index(directed_edges)

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

    return {
        "name": scenario_name,
        "directed_edges": directed_edges,
        "graph": graph,
        "edge_results": edge_results,
        "od_paths": od_paths,
        "static_metrics": static_metrics,
        "sol": sol,
        "dynamic_metrics": dynamic_metrics,
        "edge_id_to_idx": edge_id_to_idx,
    }
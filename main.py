from data_loader import load_all_data
from network_model import (
    build_directed_edges,
    build_graph,
    close_edges_by_node_pairs,
    get_closed_edge_ids,
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
from visualization import (
    plot_total_in_net, 
    plot_top_edges_dynamic_curves,
    plot_network_heatmap,
    plot_flow_diff_map,
)
from comparison import compute_flow_diff, compute_detour_table
from config import OUTPUT_DIR, BLOCKED_NODE_PAIRS


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




def main():

# 读取 /data 数据
    nodes, edges, od_pairs, release_curve = load_all_data()
    OUTPUT_DIR.mkdir(exist_ok=True)


    # 正常场景：任务 2 + 任务 3
    normal_result = run_scenario("Normal", edges, od_pairs, release_curve)
    edge_results = normal_result["edge_results"]
    od_paths = normal_result["od_paths"]
    static_metrics = normal_result["static_metrics"]
    sol = normal_result["sol"]
    dynamic_metrics = normal_result["dynamic_metrics"]
    edge_id_to_idx = normal_result["edge_id_to_idx"]
    directed_edges = normal_result["directed_edges"]


    print("\nTask 2: Normal AON + BPR results")
    print("Static TSTT:", static_metrics["static_tstt"])
    print("Saturated edges:", static_metrics["saturated_count"])
    print("Max v/c:", static_metrics["max_vc"])



# Top10
    top10_congested = edge_results.sort_values("v_c_ratio", ascending=False).head(10)
    print("\nTask 2: Top 10 congested edges")
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


    task2_output = format_task2_edges_output(edge_results)
    task2_output.to_csv(
        OUTPUT_DIR / "task2_edges_normal.csv",
        index=False,
        encoding="utf-8-sig",
    )



    print("\nTask 3: Dynamic ODE results")
    print("Dynamic TSTT:", dynamic_metrics["dynamic_tstt"])
    print("Completion rate:", dynamic_metrics["completion_rate"])
    print("nfev:", dynamic_metrics["nfev"])
    print("steps:", dynamic_metrics["steps"])


# Task03 要求的 task3_total_in_net.png 和 task3_dynamic_curves.png 图片生成
    plot_total_in_net(
        sol,
        OUTPUT_DIR / "task3_total_in_net.png",
    )

    top5_edge_ids = top10_congested.head(5)["edge_id"].tolist()

    plot_top_edges_dynamic_curves(
        sol,
        top5_edge_ids,
        edge_id_to_idx,
        OUTPUT_DIR / "task3_dynamic_curves.png",
    )



    # 封路场景：任务 4
    blocked_result = run_scenario(
        "Blocked",
        edges,
        od_pairs,
        release_curve,
        BLOCKED_NODE_PAIRS,
    )

    blocked_edges = blocked_result["directed_edges"]
    blocked_edge_results = blocked_result["edge_results"]
    blocked_od_paths = blocked_result["od_paths"]
    blocked_static_metrics = blocked_result["static_metrics"]
    blocked_dynamic_metrics = blocked_result["dynamic_metrics"]

    blocked_task2_output = format_task2_edges_output(blocked_edge_results)
    blocked_task2_output.to_csv(
        OUTPUT_DIR / "task2_edges_blocked.csv",
        index=False,
        encoding="utf-8-sig",
    )


    print("\nTask 4: Blocked scenario comparison")

    print("Normal static TSTT:", static_metrics["static_tstt"])
    print("Blocked static TSTT:", blocked_static_metrics["static_tstt"])
    print("Normal dynamic TSTT:", dynamic_metrics["dynamic_tstt"])
    print("Blocked dynamic TSTT:", blocked_dynamic_metrics["dynamic_tstt"])
    print("Normal saturated edges:", static_metrics["saturated_count"])
    print("Blocked saturated edges:", blocked_static_metrics["saturated_count"])



    flow_diff = compute_flow_diff(edge_results, blocked_edge_results)

    flow_diff.to_csv(
        OUTPUT_DIR / "task4_flow_diff.csv",
        index=False,
        encoding="utf-8-sig",
    )

    print("\nTask 4: Top 10 flow increase edges")
    print(flow_diff.head(10))


# 绕路代价计算, task4_detour.csv 生成
    closed_edge_ids = get_closed_edge_ids(blocked_edges)

    detour_table = compute_detour_table(
        od_pairs,
        od_paths,
        blocked_od_paths,
        directed_edges,
        closed_edge_ids,
    )

    detour_table.to_csv(
        OUTPUT_DIR / "task4_detour.csv",
        index=False,
        encoding="utf-8-sig",
    )

    weighted_avg_detour = (
        (detour_table["detour_min"] * detour_table["demand"]).sum()
        / detour_table["demand"].sum()
    )

    total_detour_person_min = (
        detour_table["detour_min"] * detour_table["demand"]
    ).sum()

    print("\nTask 4: Affected OD detour analysis")
    print("Affected OD pairs:", len(detour_table))
    print("Weighted average detour time:", weighted_avg_detour)
    print("Total detour person-minutes:", total_detour_person_min)
    print(detour_table.head(10))


    # 任务 5：路网可视化
    common_vmax = max(
        edge_results["v_c_ratio"].max(),
        blocked_edge_results["v_c_ratio"].max(),
    )

    plot_network_heatmap(
        nodes,
        edge_results,
        OUTPUT_DIR / "task5_heatmap_normal.png",
        "Normal Scenario Heatmap",
        common_vmax,
    )

    plot_network_heatmap(
        nodes,
        blocked_edge_results,
        OUTPUT_DIR / "task5_heatmap_blocked.png",
        "Blocked Scenario Heatmap",
        common_vmax,
    )

    plot_network_heatmap(
        nodes,
        blocked_edge_results,
        OUTPUT_DIR / "task5_heatmap_blocked.png",
        "Blocked Scenario Heatmap",
        common_vmax,
    )

    plot_flow_diff_map(
        nodes,
        flow_diff,
        OUTPUT_DIR / "task5_flow_diff.png",
        "Flow Difference After Blocking",
    )




if __name__ == "__main__":
    main()
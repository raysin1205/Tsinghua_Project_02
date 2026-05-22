def compute_flow_diff(normal_edge_results, blocked_edge_results):
    """
    BLOCKED 封闭道路情景对比
    参数：
    normal_dge_results
    blocked_edge_results
    输出：
    flow_diff, 一张 84 行的 DataFrame
    """
    normal_flow = normal_edge_results[
    ["edge_id", "from_node", "to_node", "road_name", "flow"]
    ].rename(columns={"flow": "flow_normal"})

    blocked_flow = blocked_edge_results[
    ["edge_id", "flow"]
    ].rename(columns={"flow": "flow_blocked"})

    flow_diff = normal_flow.merge(blocked_flow, on="edge_id", how="left")
    flow_diff["flow_delta"] = (
    flow_diff["flow_blocked"] - flow_diff["flow_normal"]
    )

    flow_diff = flow_diff.rename(
    columns={
        "from_node": "from",
        "to_node": "to",
    }
    )

    required_columns = [
    "edge_id",
    "from",
    "to",
    "road_name",
    "flow_normal",
    "flow_blocked",
    "flow_delta",
    ]

    flow_diff = flow_diff[required_columns]
    flow_diff = flow_diff.sort_values("flow_delta", ascending=False)

    return flow_diff
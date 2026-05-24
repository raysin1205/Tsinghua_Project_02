import pandas as pd

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


def t0_compute(edge_path, edge_t0_map):
    total = 0

    for edge_id in edge_path:
        total += edge_t0_map[edge_id]

    return total


def compute_detour_table(
    od_pairs,
    normal_od_paths,
    blocked_od_paths,
    directed_edges,
    closed_edge_ids
    ):

    closed_edge_set = set(closed_edge_ids)
    edge_t0_map = dict(zip(directed_edges["edge_id"], directed_edges["t0"]))

    rows = []

    for od_idx, normal_path in normal_od_paths.items():
        if not any(edge_id in closed_edge_set for edge_id in normal_path):
            continue

        blocked_path = blocked_od_paths[od_idx]

        t0_normal = t0_compute(normal_path, edge_t0_map)
        t0_blocked = t0_compute(blocked_path, edge_t0_map)
        detour = t0_blocked - t0_normal

        rows.append(
            {
                "origin": od_pairs.loc[od_idx, "origin"],
                "destination": od_pairs.loc[od_idx, "destination"],
                "demand": od_pairs.loc[od_idx, "demand"],
                "t0_normal_min": t0_normal,
                "t0_blocked_min": t0_blocked,
                "detour_min": detour,
            }
        )

    detour_table = pd.DataFrame(rows)
    detour_table = detour_table.sort_values("demand", ascending=False)

    return detour_table
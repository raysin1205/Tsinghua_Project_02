"""
It can also be run directly for debugging:
    python3 bonus_01.py
"""

import plotly.graph_objects as go

from config import OUTPUT_DIR, BLOCKED_NODE_PAIRS
from data_loader import load_all_data
from run_scenario import run_scenario


# Public entry point for main.py

def generate_bonus_b1_interactive_map(
    nodes,
    normal_result,
    blocked_result,
    output_path=None,
    blocked_node_pairs=BLOCKED_NODE_PAIRS,
):


    if output_path is None:
        output_path = OUTPUT_DIR / "network_interactive.html"

    node_pos = {
        row["node_id"]: (row["x"], row["y"])
        for _, row in nodes.iterrows()
    }

    blocked_directed_pairs = set()
    for u, v in blocked_node_pairs:
        blocked_directed_pairs.add((u, v))
        blocked_directed_pairs.add((v, u))

    normal_edges_data = prepare_edges_for_html(normal_result["edge_results"])
    blocked_edges_data = prepare_edges_for_html(blocked_result["edge_results"])

    fig = go.Figure()

    # Draw edges first and nodes last, so nodes stay above edges.
    normal_trace_indices = add_edges(
        fig,
        normal_edges_data,
        node_pos=node_pos,
        blocked_directed_pairs=blocked_directed_pairs,
        visible=True,
        scenario_name="Normal",
    )

    blocked_trace_indices = add_edges(
        fig,
        blocked_edges_data,
        node_pos=node_pos,
        blocked_directed_pairs=blocked_directed_pairs,
        visible=False,
        scenario_name="Blocked",
    )

    node_trace_index = add_nodes(fig, nodes)

    total_traces = len(fig.data)
    normal_visible = [False] * total_traces
    blocked_visible = [False] * total_traces

    normal_visible[node_trace_index] = True
    blocked_visible[node_trace_index] = True

    for i in normal_trace_indices:
        normal_visible[i] = True

    for i in blocked_trace_indices:
        blocked_visible[i] = True

    fig.update_layout(
        title=dict(
            text="Campus Traffic Network - Normal Scenario",
            x=0.02,
            xanchor="left",
            y=0.97,
        ),
        xaxis_title="x (m)",
        yaxis_title="y (m)",
        xaxis=dict(
            range=[0, 2000],
            showgrid=True,
            zeroline=False,
        ),
        yaxis=dict(
            range=[300, 2900],
            scaleanchor="x",
            scaleratio=1,
            showgrid=True,
            zeroline=False,
        ),
        hovermode="closest",
        updatemenus=[
            dict(
                buttons=[
                    dict(
                        label="Normal",
                        method="update",
                        args=[
                            {"visible": normal_visible},
                            {"title.text": "Campus Traffic Network - Normal Scenario"},
                        ],
                    ),
                    dict(
                        label="Blocked",
                        method="update",
                        args=[
                            {"visible": blocked_visible},
                            {"title.text": "Campus Traffic Network - Blocked Scenario"},
                        ],
                    ),
                ],
                direction="down",
                x=0.98,
                y=1.10,
                xanchor="right",
                yanchor="top",
                showactive=True,
                bgcolor="rgba(255,255,255,0.95)",
                bordercolor="rgba(80,100,130,0.45)",
            )
        ],
        margin=dict(l=60, r=40, t=100, b=60),
    )

    fig.write_html(
        output_path,
        include_plotlyjs="cdn",
        full_html=True,
        config={"responsive": True},
        div_id="campus-traffic-network",
    )

    html_text = output_path.read_text(encoding="utf-8")
    html_text = html_text.replace(
        "<head><meta charset=\"utf-8\" /></head>",
        """<head><meta charset=\"utf-8\" />
<style>
html, body {
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
}
#campus-traffic-network {
    width: 100vw !important;
    height: 100vh !important;
}
</style>
</head>""",
    )
    output_path.write_text(html_text, encoding="utf-8")

    print(f"Bonus B1 interactive network saved to: {output_path}")
    return output_path


# Helper functions

def prepare_edges_for_html(edge_results):
    """Convert edge result DataFrame into list-of-dict records for Plotly."""
    columns = [
        "edge_id",
        "from_node",
        "to_node",
        "road_name",
        "length_m",
        "flow",
        "capacity",
        "v_c_ratio",
        "travel_time",
    ]
    return edge_results[columns].to_dict(orient="records")


def edge_color_by_vc(v_c_ratio, is_blocked=False):
    """Return edge color according to v/c ratio."""
    if is_blocked:
        return "red"
    if v_c_ratio < 0.3:
        return "lightgray"
    if v_c_ratio < 0.7:
        return "green"
    if v_c_ratio < 1.0:
        return "orange"
    if v_c_ratio < 1.5:
        return "red"
    return "purple"


def edge_width_by_flow(flow, capacity):
    """Return edge width according to flow/capacity."""
    if capacity <= 0:
        return 1.5
    ratio = flow / capacity
    return min(8, 1.5 + 4 * ratio)


def add_edges(
    fig,
    edges_data,
    node_pos,
    blocked_directed_pairs,
    visible=True,
    scenario_name="Normal",
):
    """
    Add edge traces to the Plotly figure.
    """
    trace_indices = []

    for edge in edges_data:
        from_node = edge["from_node"]
        to_node = edge["to_node"]

        x1, y1 = node_pos[from_node]
        x2, y2 = node_pos[to_node]
        x_mid = (x1 + x2) / 2
        y_mid = (y1 + y2) / 2

        is_blocked_edge = (from_node, to_node) in blocked_directed_pairs
        is_blocked_visible_edge = scenario_name == "Blocked" and is_blocked_edge

        edge_color = edge_color_by_vc(
            edge["v_c_ratio"],
            is_blocked=is_blocked_visible_edge,
        )
        edge_width = edge_width_by_flow(edge["flow"], edge["capacity"])
        dash_style = "dash" if is_blocked_visible_edge else "solid"

        fig.add_trace(
            go.Scatter(
                x=[x1, x2],
                y=[y1, y2],
                mode="lines",
                line=dict(
                    width=edge_width,
                    color=edge_color,
                    dash=dash_style,
                ),
                hoverinfo="skip",
                showlegend=False,
                visible=visible,
            )
        )
        trace_indices.append(len(fig.data) - 1)

        fig.add_trace(
            go.Scatter(
                x=[x_mid],
                y=[y_mid],
                mode="markers",
                marker=dict(
                    size=18,
                    color="rgba(0,0,0,0)",
                ),
                hovertemplate=(
                    f"<b>{scenario_name} 场景</b><br>"
                    f"道路名称：{edge['road_name']}<br>"
                    f"边 ID : {edge['edge_id']}<br>"
                    f"方向 : {from_node} → {to_node}<br>"
                    f"长度 : {edge['length_m']:.0f} m<br>"
                    f"流量 : {edge['flow']:.0f} 人 / 8min<br>"
                    f"容量 : {edge['capacity']:.0f} 人 / 8min<br>"
                    f"v/c : {edge['v_c_ratio']:.3f}<br>"
                    f"穿越时间 : {edge['travel_time']:.3f} min"
                    "<extra></extra>"
                ),
                showlegend=False,
                visible=visible,
            )
        )
        trace_indices.append(len(fig.data) - 1)

    return trace_indices


def add_nodes(fig, nodes):
    """Add node trace to the Plotly figure."""
    type_to_color = {
        "building": "#4C78A8",
        "dorm": "#B279A2",
        "canteen": "#F58518",
    }

    node_colors = [
        type_to_color.get(node_type, "gray")
        for node_type in nodes["type"]
    ]

    fig.add_trace(
        go.Scatter(
            x=nodes["x"],
            y=nodes["y"],
            mode="markers+text",
            text=nodes["name"],
            textposition="top center",
            textfont=dict(size=10),
            hovertemplate=[
                f"<b>{row['name']}</b><br>"
                f"node_id : {row['node_id']}<br>"
                f"type : {row['type']}<br>"
                f"x = {row['x']} m<br>"
                f"y = {row['y']} m"
                "<extra></extra>"
                for _, row in nodes.iterrows()
            ],
            marker=dict(
                size=15,
                color=node_colors,
                line=dict(width=1.5, color="black"),
            ),
            showlegend=False,
            visible=True,
        )
    )

    return len(fig.data) - 1


# Direct debugging entry point

def main():
    """Allow this Bonus module to be run independently for debugging."""
    nodes, edges, od_pairs, release_curve = load_all_data()

    normal_result = run_scenario(
        "Normal",
        edges,
        od_pairs,
        release_curve,
    )

    blocked_result = run_scenario(
        "Blocked",
        edges,
        od_pairs,
        release_curve,
        BLOCKED_NODE_PAIRS,
    )

    generate_bonus_b1_interactive_map(
        nodes,
        normal_result,
        blocked_result,
        OUTPUT_DIR / "network_interactive.html",
        BLOCKED_NODE_PAIRS,
    )


if __name__ == "__main__":
    main()
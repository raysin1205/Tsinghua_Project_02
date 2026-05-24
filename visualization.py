import matplotlib.pyplot as plt
from config import OUTPUT_DIR


plt.rcParams["font.sans-serif"] = [
    "Microsoft YaHei",   # Windows 
    "SimHei",            # Windows 
    "PingFang SC",       # macOS 
    "Heiti TC",          # macOS 
    "WenQuanYi Zen Hei", # Linux 
]
plt.rcParams["axes.unicode_minus"] = False


def plot_total_in_net(sol, output_path):
    """
    绘制路网总在途人数随时间变化曲线。
    参数：
        sol: solve_ivp 返回的结果对象。
        output_path: 图片输出路径。
    """
    total_in_net = sol.y.sum(axis=0)
    plt.figure(figsize=(8, 5))
    plt.plot(sol.t, total_in_net)
    plt.xlabel("Time")
    plt.ylabel("The number of pepole in net")
    plt.title("Total in net VS Time")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def plot_top_edges_dynamic_curves(sol, top_edge_ids, edge_id_to_idx, output_path):

    """
    绘制 Top 5 拥堵边的在途人数动态曲线。
    参数：
        sol: solve_ivp 返回的结果对象。
        top_edge_ids: Top 5 拥堵边的 edge_id 列表。
        edge_id_to_idx: edge_id 到 sol.y 行号的映射。
        output_path: 图片输出路径。
    """
    plt.figure(figsize=(8, 5))

    idx = []
    for edge_id in top_edge_ids:
        idx = edge_id_to_idx[edge_id]
        plt.plot(sol.t, sol.y[idx], label=edge_id)

    plt.xlabel("Time")
    plt.ylabel("The number of people on edge")
    plt.title("Dynamic Curves of Top 5 Congested Edges")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    


def plot_network_heatmap(nodes, edge_results, output_path, title, v_max=None):
    """
    绘制路网静态热力图。
    参数：
        nodes: 节点表，包含 node_id、type、name、x、y。
        edge_results: 边结果表，包含 from_node、to_node、flow、v_c_ratio。
        output_path: 图片输出路径。
        title: 图标题。
    """

    node_pos = {
    row["node_id"]: (row["x"], row["y"])
    for _, row in nodes.iterrows()
    }

    fig, ax = plt.subplots(figsize=(8, 8))

    if v_max is None:
        max_vc = max(edge_results["v_c_ratio"].max(), 1e-6)
    else:
        max_vc = v_max
    
    cmap = plt.get_cmap("YlOrRd")
    norm = plt.Normalize(vmin=0, vmax=max_vc)
    max_flow = max(edge_results["flow"].max(), 1)

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    fig.colorbar(sm, ax=ax, label="v/c ratio")

    for _, row in edge_results.iterrows():
        from_node = row["from_node"]
        to_node = row["to_node"]

        x1, y1 = node_pos[from_node]
        x2, y2 = node_pos[to_node]

        row_ratio = row["flow"] / max_flow
        width = 1.0 + 3.0 * (row_ratio ** 0.5) 

        color = cmap(norm(row["v_c_ratio"]))

        ax.plot([x1, x2], [y1, y2], linewidth=width, alpha=0.9, color = color)


    node_colors = {
        "building":"#4C78A8",
        "dorm":"#B279A2",
        "canteen":"#F58518"
    }

    for _, row in nodes.iterrows():
        name = row["name"]
        node_type = row["type"]
        x = row["x"]
        y = row["y"]

        color = node_colors.get(node_type)
        ax.scatter(x, y, s=60, color=color, edgecolors="black", linewidths=0.5)
        ax.text(x + 15, y + 15, name, fontsize=8)

        
    ax.set_title(title)
    ax.axis("equal")
    ax.grid(True, alpha=0.2)
    fig.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)



def plot_flow_diff_map(nodes, flow_diff, output_path, title):
    """
    绘制差异图
    参数：
        nodes: 节点表，包含 node_id、type、name、x、y。
        flow_diff: 差异数据。
        output_path: 图片输出路径。
        title: 图标题。
    """
    node_pos = {
    row["node_id"]: (row["x"], row["y"])
    for _, row in nodes.iterrows()
    }

    fig, ax = plt.subplots(figsize=(8, 8))

    max_abs_delta = max(abs(flow_diff["flow_delta"].min()), abs(flow_diff["flow_delta"].max()))

    cmap = plt.get_cmap("RdBu_r")
    norm = plt.Normalize(vmin=-max_abs_delta, vmax=max_abs_delta)

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    fig.colorbar(sm, ax=ax, label="Flow delta (blocked - normal)")

# 这是底图
    for _, row in flow_diff.iterrows(): 
        from_node = row["from"]
        to_node = row["to"]

        x1, y1 = node_pos[from_node]
        x2, y2 = node_pos[to_node]

        row_ratio = abs(row["flow_delta"]) / max_abs_delta
        width = 1.2

        color = "lightgray"

        ax.plot([x1, x2], [y1, y2], linewidth=width, alpha=0.65, color = color, zorder=1)

# 这是主图
    for _, row in flow_diff.iterrows():
        from_node = row["from"]
        to_node = row["to"]

        x1, y1 = node_pos[from_node]
        x2, y2 = node_pos[to_node]

        row_ratio = abs(row["flow_delta"]) / max_abs_delta
        width = 1.0 + 3.0 * (row_ratio ** 0.5) 

        color = cmap(norm(row["flow_delta"]))

        ax.plot([x1, x2], [y1, y2], linewidth=width, alpha=0.9, color = color, zorder=2)


    node_colors = {
        "building":"#4C78A8",
        "dorm":"#B279A2",
        "canteen":"#F58518"
    }

    for _, row in nodes.iterrows():
        name = row["name"]
        node_type = row["type"]
        x = row["x"]
        y = row["y"]

        color = node_colors.get(node_type)
        ax.scatter(x, y, s=60, color=color, edgecolors="black", linewidths=0.5, zorder=3)
        ax.text(x + 15, y + 15, name, fontsize=8, zorder=4)
 
    ax.set_title(title)
    ax.axis("equal")
    ax.grid(True, alpha=0.2)
    fig.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)

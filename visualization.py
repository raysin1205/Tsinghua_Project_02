import matplotlib.pyplot as plt
from config import OUTPUT_DIR


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
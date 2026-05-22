from data_loader import load_all_data
from network_model import build_directed_edges, build_graph


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

    


if __name__ == "__main__":
    main()
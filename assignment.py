import networkx as nx
from network_model import bpr_time


def node_path_to_edge_path(graph, node_path): # 将节点路径转化成边的路径
    """
    参数：
        graph: networkx.DiGraph, 边属性中必须包含 edge_id。
        node_path: list[str]，节点路径，例如 ["T01", "T05", "T02"]。

    返回：
        edge_path: list[str]，边 ID 路径，例如 ["E003b", "E029f"]。
    """
    edge_path = []

    for u, v in zip(node_path[:-1], node_path[1:]):
        edge_id = graph[u][v]["edge_id"]
        edge_path.append(edge_id)

    return edge_path


def aon_assignment(graph, directed_edges, od_pairs): # 实现AON分配，将每条edge的flow添加到edge上
    """
    参数：
        graph: networkx.DiGraph, 路网有向图, 边权重使用 t0。
        directed_edges: pandas.DataFrame, 有向边表。
        od_pairs: pandas.DataFrame, OD 需求表，包含 origin、destination、demand。

    返回：
        edge_results: pandas.DataFrame, 
        它是在 directed_edges 基础上新增：
            flow: AON 分配得到的边流量；
            travel_time: BPR 计算得到的拥堵后通行时间；
            v_c_ratio: flow / capacity。
        od_paths: dict, 键为 OD 表行索引，值为该 OD 的边 ID 路径。
    """
    edge_flow = {}
    od_paths = {}

    for edge_id in directed_edges["edge_id"]:
        edge_flow[edge_id] = 0.0

    for idx, row in od_pairs.iterrows():
        origin = row["origin"]
        destination = row["destination"]
        demand = row["demand"]

        node_path = nx.shortest_path(
        graph,
        source=origin,
        target=destination,
        weight="t0",
        )   
        
        edge_path = node_path_to_edge_path(graph, node_path)
        od_paths[idx] = edge_path

        for edge in edge_path:
            edge_flow[edge] += demand

    edge_results = directed_edges.copy()
    edge_results["flow"] = edge_results["edge_id"].map(edge_flow).fillna(0.0)
    edge_results["travel_time"] = bpr_time(
    edge_results["t0"],
    edge_results["flow"],
    edge_results["capacity"],
    )
    edge_results["v_c_ratio"] = edge_results["flow"] / edge_results["capacity"]

    return edge_results, od_paths


def compute_static_metrics(edge_results): # 计算TSTT
    '''
        参数：
        edge_results: pandas.DataFrame, 必须包含 flow、travel_time、v_c_ratio。

    返回：
        dict: 包含：
            static_tstt: 静态总通行时间，单位为人·分钟；
            saturated_count: v/c >= 1 的饱和路段数量；
            max_vc: 最大 v/c 值。
    '''

    static_tstt = float((edge_results["flow"] * edge_results["travel_time"]).sum())
    saturated_count = int((edge_results["v_c_ratio"] >= 1).sum())
    max_vc = float(edge_results["v_c_ratio"].max())

    return {
        "static_tstt" : static_tstt,
        "saturated_count" : saturated_count,
        "max_vc": max_vc
    }


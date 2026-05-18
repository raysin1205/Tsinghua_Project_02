import numpy as np
import pandas as pd
import networkx as nx

from config import alpha, beta

def build_directed_edges(edges_data: pd.DataFrame): # 将原csv数据中的`无向边`转化成`有向边`
    """
    将原始道路表拆分为有向边表，并计算自由流通行时间 t0。

    参数：
        edges_df: pandas.DataFrame,原始 edges.csv 数据。每一行表示一条原始道路。

    返回：
        directed_edges: pandas.DataFrame
        其中 edge_id 新增：
            t0: 自由流通行时间，单位为分钟；
            closed: 是否封闭，默认 False。
    """

    rows = []
    for _,row in edges_data.iterrows():
        base = row.to_dict()
        
        forward = base.copy()
        forward["edge_id"] = base["edge_id"] + "f"
        forward["from_node"] = base["from_node"]
        forward["to_node"] = base["to_node"]

        rows.append(forward)

        if row["bidirectional"]:
            backword = base.copy()

            backword = base.copy()
            backword["edge_id"] = base["edge_id"] + "b"
            backword["from_node"] = base["to_node"]
            backword["to_node"] = base["from_node"]

            rows.append(backword)
    
    directed_edges = pd.DataFrame(rows)
    directed_edges["t0"] = directed_edges["length_m"] / directed_edges["free_speed"]
    directed_edges["closed"] = False

    return directed_edges


def bpr_time(t0, flow, capacity, alpha=alpha, beta=beta): #  根据 `BPR公式` 计算通行时间
    '''参数：
        t0: 自由流通行时间
        flow: 边流量, 单位为人 / 8 分钟时段。
        capacity: 边容量, 单位为人 / 8 分钟时段。
        alpha: BPR 延误系数, default为 0.15。
        beta: BPR 拥堵敏感度指数, default为 4。

    返回：
        travel_time: 拥堵后的通行时间，和 t0 具有相同的形状。
    '''

    t0 = np.asarray(t0, dtype=float)
    flow = np.asarray(flow, dtype=float)
    capacity = np.asarray(capacity, dtype=float)

    result = t0 * (1 + alpha *( (flow / capacity) ** beta))
    return result


def close_edges_by_node_pairs(directed_edges: pd.DataFrame, closed_node_pairs): # 给 BLOCKED 路口提供封锁的 “借口” 

    """
    参数：
        directed_edges: pandas.DataFrame, 有向边表。
        closed_node_pairs: list[tuple[str, str]]，需要封闭的有向节点对，
    返回：
        pandas.DataFrame: 标记封路后的有向边表，其中对应边的 closed=True。
    """

    directed_edges = directed_edges.copy()

    for from_node, to_node in closed_node_pairs:
        mask = (
            (directed_edges["from_node"] == from_node)
            & (directed_edges["to_node"] == to_node)
        )
        directed_edges.loc[mask, "closed"] = True

    return directed_edges


def get_closed_edge_ids(edges: pd.DataFrame): # 需要知道哪些边blocked了
    return edges.loc[edges["closed"], "edge_id"].tolist() 


def build_graph(edges: pd.DataFrame): # 将 directed_edges 转化成 `networkx` 的有向图
    
    '''
    参数：
        directed_edges: pandas.DataFrame, 有向边表, 包含 edge_id、from_node、
        to_node、t0、capacity

    返回：
        graph: networkx.DiGraph。每条边保存 edge_id、road_name、length_m、
        capacity、free_speed、t0 等属性。
    '''
    graph = nx.DiGraph()

    available_edges = edges[~edges["closed"]]
    for _, row in available_edges.iterrows():
        graph.add_edge(
            row["from_node"],
            row["to_node"],
            edge_id=row["edge_id"],
            t0=row["t0"],
            road_name = row["road_name"],
            length_m = row["length_m"],
            lanes = row["lanes"],
            road_class  = row["road_class"],
            capacity = row["capacity"],
            free_speed  = ["free_speed "],
        )  
        
    return graph
import pandas as pd
import numpy as np


def prepare_edge_index(directed_edges: pd.DataFrame):
    '''
    参数：
        directed_edges: 有向边表，必须包含 edge_id 列。

    返回：
        edge_id_to_idx: dict, edge_id -> 数组下标。
        idx_to_edge_id: dict, 数组下标 -> edge_id。
    '''
    edge_ids = directed_edges["edge_id"].tolist()

    edge_id_to_idx = {edge_id: idx for idx, edge_id in enumerate(edge_ids)}
    idx_to_edge_id = {idx: edge_id for idx, edge_id in enumerate(edge_ids)}

    return edge_id_to_idx, idx_to_edge_id


def prepare_source_vector(directed_edges, od_pairs, od_paths, edge_id_to_idx):
    '''
    参数：
        directed_edges: 有向边表, 用于确定边数量
        od_pairs: OD 需求表, 包含 demand
        od_paths: AON 分配得到的 OD 边路径字典
        edge_id_to_idx: edge_id 到数组下标的映射

    返回：
        source_vector: numpy.ndarray, 长度为有向边数量
    '''
    source_vector = np.zeros(len(edge_id_to_idx))

    for od_idx, edge_path in od_paths.items():

        demand = od_pairs.loc[od_idx, "demand"]
        edge_path_idx = edge_id_to_idx[edge_path[0]]

        source_vector[edge_path_idx] += demand

    return source_vector



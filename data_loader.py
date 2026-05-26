import pandas as pd

from config import DATA_DIR

def load_nodes():
    return pd.read_csv(DATA_DIR / "nodes.csv")

def load_edges():
    return pd.read_csv(DATA_DIR / "edges.csv")

def load_od_pairs():
    return pd.read_csv(DATA_DIR / "od_pairs.csv")

def load_release_curve():
    return pd.read_csv(DATA_DIR / "release_curve.csv")

def load_all_data():
    """
    一次性读取本作业所需的全部输入数据。
    返回：
        nodes: 节点表，包含 node_id、type、name、x、y、population 
        edges: 原始道路表，包含 from_node、to_node、length_m、capacity 
        od_pairs: OD 需求表，包含 origin、destination、demand
        release_curve: 人流释放曲线，包含 t_minute、release_rate
    """
    
    nodes = load_nodes()
    edges = load_edges()
    od_pairs = load_od_pairs()
    release_curve = load_release_curve()

    return nodes, edges, od_pairs, release_curve
import pandas as pd

from config import DATA_DIR

def clean_text_columns(df):
    """清理空字符。"""
    df = df.copy()
    def clean_value(value):
        if isinstance(value, str):
            return value.replace("\x00", "").strip()
        return value
    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].map(clean_value)
    return df

def load_nodes():
    nodes = pd.read_csv(DATA_DIR / "nodes.csv")
    return clean_text_columns(nodes)

def load_edges():
    edges = pd.read_csv(DATA_DIR / "edges.csv")
    return clean_text_columns(edges)

def load_od_pairs():
    od_pairs = pd.read_csv(DATA_DIR / "od_pairs.csv")
    return clean_text_columns(od_pairs)

def load_release_curve():
    release_curve = pd.read_csv(DATA_DIR / "release_curve.csv")
    return clean_text_columns(release_curve)

def load_all_data():
    """
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
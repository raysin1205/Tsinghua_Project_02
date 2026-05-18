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
    nodes = load_nodes()
    edges = load_edges()
    od_pairs = load_od_pairs()
    release_curve = load_release_curve()

    return nodes, edges, od_pairs, release_curve
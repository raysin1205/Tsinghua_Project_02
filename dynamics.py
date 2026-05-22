import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from scipy.integrate import solve_ivp
from config import PEAK_DURATION, T_END, DT


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


def prepare_turn_matrix(directed_edges, od_pairs, od_paths, edge_id_to_idx):
    '''
    参数：
        directed_edges: 有向边表，用于确定边数量。
        od_pairs: OD 需求表，包含 demand。
        od_paths: AON 分配得到的 OD 边路径字典。
        edge_id_to_idx: edge_id 到 ODE 状态向量下标的映射。

    返回：
        turn_matrix: scipy.sparse.csr_matrix, 形状为 E ✖️ E。
            turn_matrix[f_idx, e_idx] 表示从边 f 转向边 e 的比例。
    '''
    edges_nums = len(edge_id_to_idx)
    edge_total_demand = np.zeros(edges_nums)
    turn_demand = {}

    for od_idx, edge_path in od_paths.items():

        demand = od_pairs.loc[od_idx, "demand"]

        for edge_id in edge_path:

            edge_idx = edge_id_to_idx[edge_id]
            edge_total_demand[edge_idx] += demand

        for from_edge, to_edge in zip(edge_path[:-1], edge_path[1:]):

            from_idx = edge_id_to_idx[from_edge]
            to_idx = edge_id_to_idx[to_edge]
            key = (from_idx, to_idx)
            turn_demand[key] = turn_demand.get(key, 0.0) + demand

    rows = []
    cols = []
    data = []

    for (from_idx, to_idx), demand in turn_demand.items():

        if edge_total_demand[from_idx] > 0:

            ratio = demand / edge_total_demand[from_idx]
            rows.append(from_idx)
            cols.append(to_idx)
            data.append(ratio)

    turn_matrix = csr_matrix((data, (rows, cols)), shape=(edges_nums, edges_nums))

    return turn_matrix


def release_rate(t, release_curve):
    '''
    释放曲线 `r(t)`
    参数：
        t: 时间
        release_curve: 释放曲线, 由 data 中的 release_curve.csv 提供

    返回：
        v: t时刻的释放速度, 用于插入(np.interp)到释放曲线中
    '''
    return np.interp(
    t,
    release_curve["t_minute"].values,
    release_curve["release_rate"].values,
    left=0.0,
    right=0.0,
    )


def build_rhs(directed_edges, source_vector, turn_matrix, release_curve):
    '''
    创建right hand side 函数
    参数：
        directed_edges: 有向边表，包含 t0 和 capacity。
        source_vector: 每条边的源释放总需求。
        turn_matrix: 边到边的转向比矩阵。
        release_curve: 释放曲线表。
    返回：
        rhs 函数
    '''

    t0 = directed_edges["t0"].values.astype(float)
    capacity_per_min = directed_edges["capacity"].values.astype(float) / PEAK_DURATION

    def rhs(t, n):
        '''
        rhs函数
        参数：
            t: 时间
            n: 人数
        返回：  
            q_in - q_out ,即 dn / dt
        '''
        n = np.maximum(n, 0.0)

        q_out = np.minimum(capacity_per_min, n / t0)

        q_in_source = source_vector * release_rate(t, release_curve)
        q_in_turn = np.asarray(turn_matrix.T @ q_out).ravel()
        q_in = q_in_source + q_in_turn

        return q_in - q_out

    return rhs


def run_ode_simulation(directed_edges, source_vector, turn_matrix, release_curve):
    """
    调用 solve_ivp 运行 ODE 动态交通流仿真。

    参数：
        directed_edges: 有向边表。
        source_vector: 每条边的源释放需求量。
        turn_matrix: 转向比矩阵。
        release_curve: 释放曲线表。

    返回：
        sol: solve_ivp 返回的求解结果对象。
    """
    num_edges = len(directed_edges)
    y0 = np.zeros(num_edges)
    rhs = build_rhs(directed_edges, source_vector, turn_matrix, release_curve)
    t_eval = np.arange(0.0, T_END + DT, DT)

    sol = solve_ivp(
    fun=rhs,
    t_span=(0.0, T_END),
    y0=y0,
    t_eval=t_eval,
    method="RK45",
    )

    return sol


def compute_dynamic_metrics(sol, total_demand):
    """
    计算 ODE 动态仿真的核心指标。

    参数：
        sol: solve_ivp 返回的求解结果对象。
        total_demand: OD 总需求人数。

    返回：
        dict: 包含 dynamic_tstt、completion_rate、nfev、steps。
    """
    total_in_net = sol.y.sum(axis=0)
    dynamic_tstt = np.trapezoid(total_in_net, sol.t)
    remaining = total_in_net[-1]
    completion_rate = 1 - remaining / total_demand

    return {
    "dynamic_tstt": float(dynamic_tstt),
    "completion_rate": float(completion_rate),
    "nfev": int(sol.nfev),
    "steps": int(len(sol.t)),
    }
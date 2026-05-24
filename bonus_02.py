import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from config import OUTPUT_DIR, BLOCKED_NODE_PAIRS
from data_loader import load_all_data
from run_scenario import run_scenario

def main():
    nodes, edges, od_pairs, release_curve = load_all_data()
    OUTPUT_DIR.mkdir(exist_ok=True)

    # S1：额外封路场景
    s1_closed_pairs = BLOCKED_NODE_PAIRS + [
    ("T05", "T02"),
    ("T02", "T05"),
    ]

    s1_result = run_scenario(
    "S1",
    edges,
    od_pairs,
    release_curve,
    s1_closed_pairs,
    )


    # S2：容量减半场景
    s2_edges = edges.copy()

    mask = (
    ((s2_edges["from_node"] == "C04") & (s2_edges["to_node"] == "C08"))
    |
    ((s2_edges["from_node"] == "C08") & (s2_edges["to_node"] == "C04"))
    )

    s2_edges.loc[mask, "capacity"] = s2_edges.loc[mask, "capacity"] * 0.5

    s2_result = run_scenario(
    "S2",
    s2_edges,
    od_pairs,
    release_curve,
    )


    # S3：食堂关闭需求转移
    s3_od_pairs = od_pairs.copy()
    s3_od_pairs.loc[s3_od_pairs["destination"] == "C01", "destination"] = "C02"

    s3_result = run_scenario(
    "S3",
    edges,
    s3_od_pairs,
    release_curve,
    )


    # 多场景敏感分析表格
    bonus_results = [s1_result, s2_result, s3_result]

    rows = []
    for result in bonus_results:
        rows.append({
            "scenario": result["name"],
            "static_tstt": result["static_metrics"]["static_tstt"],
            "dynamic_tstt": result["dynamic_metrics"]["dynamic_tstt"],
            "max_vc": result["static_metrics"]["max_vc"],
            "saturated_count": result["static_metrics"]["saturated_count"],
            "completion_rate": result["dynamic_metrics"]["completion_rate"],
            })

    summary = pd.DataFrame(rows)

    summary.to_csv(
        OUTPUT_DIR / "bonus_scenario_summary.csv",
        index=False,
        encoding="utf-8-sig",
    )


    # 可视化
    output_path = OUTPUT_DIR / "bonus_scenario_comparison.png"

    fig, ax = plt.subplots(figsize=(8,8))
    
    x = np.arange(len(summary))
    width = 0.35

    ax.bar(
    x - width / 2,
    summary["static_tstt"],
    width,
    label="Static TSTT",
    )

    ax.bar(
    x + width / 2,
    summary["dynamic_tstt"],
    width,
    label="Dynamic TSTT",
    )

    ax.set_xticks(x)
    ax.set_xticklabels(summary["scenario"])

    ax.set_title("Bonus B2 Scenario Comparison")
    ax.set_ylabel("TSTT (person-min)")
    ax.set_xlabel("Scenario")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    main()
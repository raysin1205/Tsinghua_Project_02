"""
It can also be run directly for debugging:
    python3 bonus_02.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from config import OUTPUT_DIR, BLOCKED_NODE_PAIRS
from data_loader import load_all_data
from run_scenario import run_scenario


# Public entry point for main.py

def run_bonus_b2_sensitivity_analysis(
    edges,
    od_pairs,
    release_curve,
    output_dir=OUTPUT_DIR,
    baseline_result=None,
):

    output_dir.mkdir(exist_ok=True)

    scenario_results = {}

    # S1: 额外封路场景
    s1_closed_pairs = BLOCKED_NODE_PAIRS + [
        ("T05", "T02"),
    ]

    scenario_results["S1"] = run_scenario(
        "S1",
        edges,
        od_pairs,
        release_curve,
        s1_closed_pairs,
    )

    # S2: 容量减半场景
    s2_edges = edges.copy()

    s2_mask = (
        ((s2_edges["from_node"] == "C04") & (s2_edges["to_node"] == "C08"))
        |
        ((s2_edges["from_node"] == "C08") & (s2_edges["to_node"] == "C04"))
    )

    s2_edges.loc[s2_mask, "capacity"] = s2_edges.loc[s2_mask, "capacity"] * 0.5

    scenario_results["S2"] = run_scenario(
        "S2",
        s2_edges,
        od_pairs,
        release_curve,
    )

    # S3: 食堂关闭需求转移
    s3_od_pairs = od_pairs.copy()
    s3_od_pairs.loc[s3_od_pairs["destination"] == "C01", "destination"] = "C02"

    scenario_results["S3"] = run_scenario(
        "S3",
        edges,
        s3_od_pairs,
        release_curve,
    )

    # Build summary table
    rows = []

    if baseline_result is not None:
        rows.append(_result_to_summary_row("Baseline", baseline_result))

    for scenario_name in ["S1", "S2", "S3"]:
        rows.append(_result_to_summary_row(scenario_name, scenario_results[scenario_name]))

    summary = pd.DataFrame(rows)

    summary.to_csv(
        output_dir / "bonus_scenario_summary.csv",
        index=False,
        encoding="utf-8-sig",
    )

    plot_bonus_b2_comparison(
        summary,
        output_dir / "bonus_scenario_comparison.png",
    )

    print(f"Bonus B2 summary saved to: {output_dir / 'bonus_scenario_summary.csv'}")
    print(f"Bonus B2 comparison figure saved to: {output_dir / 'bonus_scenario_comparison.png'}")

    return summary, scenario_results


# Helper functions

def _result_to_summary_row(scenario_name, result):
    """Convert one run_scenario result into one summary-table row."""
    return {
        "scenario": scenario_name,
        "static_tstt": result["static_metrics"]["static_tstt"],
        "dynamic_tstt": result["dynamic_metrics"]["dynamic_tstt"],
        "max_vc": result["static_metrics"]["max_vc"],
        "saturated_count": result["static_metrics"]["saturated_count"],
        "completion_rate": result["dynamic_metrics"]["completion_rate"],
    }


def plot_bonus_b2_comparison(summary, output_path):
    """Plot static and dynamic TSTT comparison for Bonus B2 scenarios."""
    fig, ax = plt.subplots(figsize=(9, 6))

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


# Direct debugging entry point

def main():
    """Allow this Bonus module to be run independently for debugging."""
    _, edges, od_pairs, release_curve = load_all_data()
    
    baseline_result = run_scenario(
        "Baseline",
        edges,
        od_pairs,
        release_curve,
        BLOCKED_NODE_PAIRS,
    )

    run_bonus_b2_sensitivity_analysis(
        edges,
        od_pairs,
        release_curve,
        OUTPUT_DIR,
        baseline_result=baseline_result,
    )


if __name__ == "__main__":
    main()
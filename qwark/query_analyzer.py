from typing import Dict, List, Any
from .models import ExplainPlan


def compare_and_filter_plans(
    plans: List[ExplainPlan],
    cost_threshold: float = 1.2,
    time_threshold: float = 1.2,
) -> List[ExplainPlan]:
    """
    Compare multiple query plans and discard plans significantly worse than the best.

    Args:
        plans (List[ExplainPlan]): List of EXPLAIN JSON plan dictionaries.
        cost_threshold (float, optional): Maximum factor over best total cost to
            keep a plan. Defaults to 1.2.
        time_threshold (float, optional): Maximum factor over best execution time
            (ms) to keep a plan. Defaults to 1.2.

    Returns:
        List[ExplainPlan]: Filtered list of plans considered good candidates.
    """
    if not plans:
        return []

    def extract_cost(plan: ExplainPlan) -> float:
        # Total cost reported at top node: plan['Plan']['Total Cost']
        return plan.get("Plan", {}).get("Total_Cost", float("inf"))

    def extract_exec_time(plan: ExplainPlan) -> float:
        # Execution Time in milliseconds
        return plan.get("Execution_Time", float("inf"))

    best_cost = min(extract_cost(p) for p in plans)
    best_time = min(extract_exec_time(p) for p in plans)

    filtered: List[ExplainPlan] = []
    for plan in plans:
        cost = extract_cost(plan)
        time = extract_exec_time(plan)
        if cost <= best_cost * cost_threshold and time <= best_time * time_threshold:
            filtered.append(plan)

    return filtered


def summarize_best_plans(plans: List[ExplainPlan]) -> List[Dict[str, Any]]:
    """
    Generate summaries for the given list of query plans.

    Args:
        plans (List[ExplainPlan]): List of EXPLAIN JSON plan dictionaries.

    Returns:
        List[Dict[str, Any]]: List of dictionaries containing summarized info per plan:
            - total_cost (float)
            - execution_time_ms (float)
            - plan_type (str) top node type
            - actual_rows (int)
            - buffers (Dict[str, int])
            - summary (str) human-readable summary
    """
    summaries: List[Dict[str, Any]] = []

    for plan in plans:
        p = plan.get("Plan", {})
        total_cost = p.get("Total_Cost", 0.0)
        execution_time = plan.get("Execution_Time", 0.0)
        plan_type = p.get("Node_Type", "Unknown")
        actual_rows = p.get("Actual_Rows", 0)

        buffers = p.get("Buffers", {})
        buffer_summary = (
            ", ".join(f"{k}: {v}" for k, v in buffers.items())
            if buffers
            else "No buffer info"
        )

        summary_text = (
            f"Plan Type: {plan_type}\n"
            f"Total Cost: {total_cost:.2f}\n"
            f"Execution Time: {execution_time:.2f} ms\n"
            f"Actual Rows: {actual_rows}\n"
            f"Buffers: {buffer_summary}"
        )

        summaries.append(
            {
                "total_cost": total_cost,
                "execution_time_ms": execution_time,
                "plan_type": plan_type,
                "actual_rows": actual_rows,
                "buffers": buffers,
                "summary": summary_text,
            }
        )

    return summaries

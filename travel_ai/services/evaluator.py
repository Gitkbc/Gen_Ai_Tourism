from typing import Dict, Any


def evaluate_plan(plan_data: Dict[str, Any], budget_info: Dict[str, Any]) -> Dict[str, Any]:
    days = plan_data.get("days", [])
    num_days = len(days)

    total_entities = sum(len(day.get("activities", [])) for day in days)
    avg_entities = total_entities / num_days if num_days > 0 else 0.0

    validation_passed = (
        num_days > 0
        and avg_entities > 0
        and budget_info.get("within_budget", False)
    )

    return {
        "days_generated": num_days,
        "avg_entities_per_day": round(avg_entities, 2),
        "within_budget": budget_info.get("within_budget", False),
        "validation_passed": validation_passed,
    }
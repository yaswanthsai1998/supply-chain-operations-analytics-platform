from pathlib import Path
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
ASSETS_DIR = BASE_DIR / "assets"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)


def load_data() -> dict:
    required = ["orders.csv", "inventory.csv", "warehouses.csv", "carriers.csv", "demand_forecast.csv"]
    missing = [file for file in required if not (RAW_DIR / file).exists()]
    if missing:
        raise FileNotFoundError(
            f"Missing raw files: {missing}. Run `python src/generate_synthetic_data.py` first."
        )
    return {
        "orders": pd.read_csv(RAW_DIR / "orders.csv", parse_dates=["order_date", "promised_delivery_date", "actual_delivery_date"]),
        "inventory": pd.read_csv(RAW_DIR / "inventory.csv", parse_dates=["snapshot_date"]),
        "warehouses": pd.read_csv(RAW_DIR / "warehouses.csv"),
        "carriers": pd.read_csv(RAW_DIR / "carriers.csv"),
        "forecast": pd.read_csv(RAW_DIR / "demand_forecast.csv", parse_dates=["forecast_date"]),
    }


def calculate_order_kpis(orders: pd.DataFrame, carriers: pd.DataFrame) -> pd.DataFrame:
    df = orders.merge(carriers, on="carrier_id", how="left")
    df["delivered_on_time"] = df["actual_delivery_date"] <= df["promised_delivery_date"]
    df["delay_days"] = (df["actual_delivery_date"] - df["promised_delivery_date"]).dt.days.clip(lower=0)
    summary = df.groupby(["warehouse_id", "carrier_id", "carrier_name", "mode"], as_index=False).agg(
        total_orders=("order_id", "count"),
        total_units=("ordered_units", "sum"),
        on_time_orders=("delivered_on_time", "sum"),
        avg_delay_days=("delay_days", "mean")
    )
    summary["otif_percent"] = (summary["on_time_orders"] / summary["total_orders"] * 100).round(2)
    summary["avg_delay_days"] = summary["avg_delay_days"].round(2)
    return summary.sort_values(["otif_percent", "avg_delay_days"])


def calculate_inventory_kpis(inventory: pd.DataFrame, orders: pd.DataFrame) -> pd.DataFrame:
    demand = orders.groupby(["warehouse_id", "sku"], as_index=False)["ordered_units"].sum()
    inv = inventory.groupby(["warehouse_id", "sku"], as_index=False).agg(
        avg_on_hand_units=("on_hand_units", "mean"),
        min_on_hand_units=("on_hand_units", "min"),
        avg_reorder_point=("reorder_point", "mean"),
        avg_unit_cost=("unit_cost", "mean")
    )
    df = inv.merge(demand, on=["warehouse_id", "sku"], how="left")
    df["ordered_units"] = df["ordered_units"].fillna(0)
    df["inventory_turnover"] = (df["ordered_units"] / df["avg_on_hand_units"].replace(0, np.nan)).round(2)
    df["inventory_value"] = (df["avg_on_hand_units"] * df["avg_unit_cost"]).round(2)
    df["inventory_status"] = np.where(df["min_on_hand_units"] < df["avg_reorder_point"], "REORDER RISK", "HEALTHY")
    return df.sort_values(["inventory_status", "inventory_turnover"], ascending=[False, False])


def calculate_forecast_accuracy(forecast: pd.DataFrame) -> pd.DataFrame:
    df = forecast.groupby(["warehouse_id", "sku"], as_index=False).agg(
        actual_units=("actual_units", "sum"),
        forecast_units=("forecast_units", "sum")
    )
    df["absolute_error"] = (df["actual_units"] - df["forecast_units"]).abs()
    df["forecast_accuracy_percent"] = (100 * (1 - df["absolute_error"] / df["actual_units"].replace(0, np.nan))).round(2)
    df["forecast_accuracy_percent"] = df["forecast_accuracy_percent"].clip(lower=0)
    return df.sort_values("forecast_accuracy_percent")


def run_scenario_analysis(orders: pd.DataFrame, warehouses: pd.DataFrame) -> pd.DataFrame:
    daily_demand = orders.groupby(["warehouse_id", "order_date"], as_index=False)["ordered_units"].sum()
    scenarios = []
    scenario_config = {
        "Baseline": 1.00,
        "Peak Demand +15%": 1.15,
        "Promotion Surge +25%": 1.25,
        "Capacity Constraint -10%": 1.00,
    }
    for scenario, demand_multiplier in scenario_config.items():
        temp = daily_demand.merge(warehouses[["warehouse_id", "daily_capacity_units"]], on="warehouse_id", how="left")
        temp["scenario"] = scenario
        temp["scenario_demand_units"] = (temp["ordered_units"] * demand_multiplier).round().astype(int)
        if scenario == "Capacity Constraint -10%":
            temp["scenario_capacity_units"] = (temp["daily_capacity_units"] * 0.90).round().astype(int)
        else:
            temp["scenario_capacity_units"] = temp["daily_capacity_units"]
        temp["utilization_percent"] = (temp["scenario_demand_units"] / temp["scenario_capacity_units"] * 100).round(2)
        temp["capacity_risk_flag"] = np.where(temp["utilization_percent"] >= 85, "HIGH RISK", "NORMAL")
        scenarios.append(temp)
    result = pd.concat(scenarios, ignore_index=True)
    return result.groupby(["warehouse_id", "scenario"], as_index=False).agg(
        avg_utilization_percent=("utilization_percent", "mean"),
        max_utilization_percent=("utilization_percent", "max"),
        high_risk_days=("capacity_risk_flag", lambda x: (x == "HIGH RISK").sum())
    ).round(2)


def create_charts(carrier_performance: pd.DataFrame, scenario_analysis: pd.DataFrame, forecast_accuracy: pd.DataFrame) -> None:
    """Create lightweight CSV chart source files for BI tools.

    These outputs avoid hard dependency on a local charting engine and can be
    imported directly into Power BI, Tableau, QuickSight, or Excel.
    """
    carrier_performance.groupby("carrier_name", as_index=False)["otif_percent"].mean().to_csv(
        ASSETS_DIR / "chart_source_otif_by_carrier.csv", index=False
    )
    scenario_analysis.groupby("scenario", as_index=False)["avg_utilization_percent"].mean().to_csv(
        ASSETS_DIR / "chart_source_scenario_utilization.csv", index=False
    )
    forecast_accuracy.head(10).to_csv(
        ASSETS_DIR / "chart_source_forecast_accuracy_risks.csv", index=False
    )

def main() -> None:
    data = load_data()
    carrier_performance = calculate_order_kpis(data["orders"], data["carriers"])
    inventory_kpis = calculate_inventory_kpis(data["inventory"], data["orders"])
    forecast_accuracy = calculate_forecast_accuracy(data["forecast"])
    scenario_analysis = run_scenario_analysis(data["orders"], data["warehouses"])

    kpi_summary = pd.DataFrame({
        "metric": [
            "Total Orders",
            "Total Units",
            "Average OTIF %",
            "Average Forecast Accuracy %",
            "SKUs at Reorder Risk",
            "High-Risk Scenario Days"
        ],
        "value": [
            len(data["orders"]),
            int(data["orders"]["ordered_units"].sum()),
            round(carrier_performance["otif_percent"].mean(), 2),
            round(forecast_accuracy["forecast_accuracy_percent"].mean(), 2),
            int((inventory_kpis["inventory_status"] == "REORDER RISK").sum()),
            int(scenario_analysis["high_risk_days"].sum())
        ]
    })

    carrier_performance.to_csv(PROCESSED_DIR / "carrier_performance.csv", index=False)
    inventory_kpis.to_csv(PROCESSED_DIR / "inventory_kpis.csv", index=False)
    forecast_accuracy.to_csv(PROCESSED_DIR / "forecast_accuracy.csv", index=False)
    scenario_analysis.to_csv(PROCESSED_DIR / "scenario_analysis.csv", index=False)
    kpi_summary.to_csv(PROCESSED_DIR / "kpi_summary.csv", index=False)

    create_charts(carrier_performance, scenario_analysis, forecast_accuracy)
    print("Pipeline completed successfully.")
    print(f"Processed outputs saved in: {PROCESSED_DIR}")
    print(f"Charts saved in: {ASSETS_DIR}")


if __name__ == "__main__":
    main()

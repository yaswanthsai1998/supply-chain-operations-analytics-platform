from pathlib import Path
import numpy as np
import pandas as pd

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

np.random.seed(42)

WAREHOUSES = pd.DataFrame({
    "warehouse_id": ["WH_CHI", "WH_DFW", "WH_ATL", "WH_PHX"],
    "warehouse_name": ["Chicago FC", "Dallas FC", "Atlanta FC", "Phoenix FC"],
    "region": ["Midwest", "South", "Southeast", "West"],
    "daily_capacity_units": [4200, 3900, 3600, 3400],
    "labor_hours_available": [580, 540, 510, 480]
})

CARRIERS = pd.DataFrame({
    "carrier_id": ["CR_A", "CR_B", "CR_C", "CR_D"],
    "carrier_name": ["NorthStar Logistics", "RapidRoute", "BlueLine Freight", "MetroShip"],
    "mode": ["Parcel", "Parcel", "LTL", "Parcel"],
    "contracted_sla_days": [2, 2, 4, 3]
})

SKUS = [f"SKU_{i:03d}" for i in range(1, 21)]
REGIONS = ["Midwest", "South", "Southeast", "West", "Northeast"]
DATES = pd.date_range("2026-01-01", "2026-03-31", freq="D")


def generate_orders(n_orders: int = 5000) -> pd.DataFrame:
    records = []
    for i in range(1, n_orders + 1):
        order_date = np.random.choice(DATES)
        wh = WAREHOUSES.sample(1).iloc[0]
        carrier = CARRIERS.sample(1).iloc[0]
        units = int(np.random.gamma(shape=2.0, scale=8.0)) + 1
        promised = pd.Timestamp(order_date) + pd.Timedelta(days=int(carrier["contracted_sla_days"]))
        delay_risk = 0.10
        if carrier["carrier_id"] == "CR_C":
            delay_risk = 0.18
        if wh["warehouse_id"] == "WH_PHX":
            delay_risk += 0.04
        delay_days = np.random.choice([0, 1, 2, 3], p=[1-delay_risk, delay_risk*0.55, delay_risk*0.30, delay_risk*0.15])
        actual = promised + pd.Timedelta(days=int(delay_days))
        records.append({
            "order_id": f"ORD_{i:06d}",
            "order_date": pd.Timestamp(order_date).date(),
            "customer_region": np.random.choice(REGIONS),
            "sku": np.random.choice(SKUS),
            "ordered_units": units,
            "promised_delivery_date": promised.date(),
            "actual_delivery_date": actual.date(),
            "warehouse_id": wh["warehouse_id"],
            "carrier_id": carrier["carrier_id"]
        })
    return pd.DataFrame(records)


def generate_inventory() -> pd.DataFrame:
    records = []
    for date in DATES:
        for wh in WAREHOUSES["warehouse_id"]:
            for sku in SKUS:
                base = np.random.randint(250, 950)
                seasonal_drop = 0.78 if date.month == 3 and wh in ["WH_CHI", "WH_PHX"] else 1.0
                on_hand = int(base * seasonal_drop + np.random.normal(0, 40))
                records.append({
                    "snapshot_date": date.date(),
                    "warehouse_id": wh,
                    "sku": sku,
                    "on_hand_units": max(on_hand, 0),
                    "reorder_point": np.random.randint(300, 520),
                    "unit_cost": round(np.random.uniform(8, 45), 2)
                })
    return pd.DataFrame(records)


def generate_forecast(orders: pd.DataFrame) -> pd.DataFrame:
    actual = (orders.groupby(["order_date", "sku", "warehouse_id"], as_index=False)["ordered_units"]
              .sum().rename(columns={"order_date": "forecast_date", "ordered_units": "actual_units"}))
    actual["forecast_units"] = (actual["actual_units"] * np.random.normal(1.03, 0.16, len(actual))).round().astype(int)
    actual["forecast_units"] = actual["forecast_units"].clip(lower=0)
    return actual[["forecast_date", "sku", "warehouse_id", "forecast_units", "actual_units"]]


def main() -> None:
    orders = generate_orders()
    inventory = generate_inventory()
    forecast = generate_forecast(orders)

    WAREHOUSES.to_csv(RAW_DIR / "warehouses.csv", index=False)
    CARRIERS.to_csv(RAW_DIR / "carriers.csv", index=False)
    orders.to_csv(RAW_DIR / "orders.csv", index=False)
    inventory.to_csv(RAW_DIR / "inventory.csv", index=False)
    forecast.to_csv(RAW_DIR / "demand_forecast.csv", index=False)
    print(f"Synthetic data generated in {RAW_DIR}")


if __name__ == "__main__":
    main()

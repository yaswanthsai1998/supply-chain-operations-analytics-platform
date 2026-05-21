# Supply Chain Operations Analytics Platform

> An end-to-end Python analytics pipeline simulating real-world supply chain operations across fulfillment centers — automating OTIF tracking, inventory risk flagging, demand forecast accuracy scoring, and multi-scenario capacity planning.

---

## 📌 Project Overview

This project mirrors the analytics workflows used by supply chain teams at large-scale e-commerce and retail operations. It generates a realistic synthetic dataset and runs a full analytics pipeline to produce KPIs, risk flags, and scenario outputs — all exportable to **Power BI, Tableau, AWS QuickSight, and Excel**.

Built to demonstrate proficiency in **end-to-end supply chain analytics**, big data handling, automation, and cross-functional BI reporting.

---

## 🏗️ Architecture

```
supply-chain-operations-analytics-platform/
│
├── src/
│   ├── generate_synthetic_data.py   # Synthetic data generation
│   └── run_pipeline.py              # Analytics pipeline
│
├── data/
│   ├── raw/                         # Generated source data (CSVs)
│   └── processed/                   # KPI outputs
│
├── assets/                          # Chart-ready CSV exports for BI tools
└── README.md
```

---

## 📊 Dataset

| Entity | Details |
|---|---|
| **Orders** | 5,000 orders across Q1 2026 |
| **Warehouses** | 4 fulfillment centers — Chicago, Dallas, Atlanta, Phoenix |
| **Carriers** | 4 carriers (Parcel & LTL) with varying SLA and delay risk profiles |
| **SKUs** | 20 products with seasonal demand variation |
| **Regions** | 5 customer regions — Midwest, South, Southeast, West, Northeast |
| **Inventory Snapshots** | Daily on-hand units, reorder points, unit costs per SKU per warehouse |
| **Demand Forecast** | Forecast vs. actuals with simulated ±16% forecast error |

---

## ⚙️ Pipeline Modules

### 1. `generate_synthetic_data.py`
Generates realistic supply chain data with:
- Carrier-specific delay risk modeling (LTL carriers carry higher delay probability)
- Warehouse-level capacity constraints and seasonal inventory drops
- Statistically modeled demand forecast error using normal distribution

### 2. `run_pipeline.py`
Runs the full analytics pipeline across 5 modules:

| Module | Output |
|---|---|
| **Order KPIs** | OTIF %, average delay days by carrier and warehouse |
| **Inventory KPIs** | Inventory turnover, reorder risk flags, inventory value per SKU |
| **Forecast Accuracy** | Absolute error, forecast accuracy % vs. actuals |
| **Scenario Analysis** | Capacity utilization and risk flags across 4 demand scenarios |
| **KPI Summary** | Aggregated executive-level supply chain scorecard |

---

## 🔀 Scenario Analysis

Four demand and capacity scenarios modeled to support S&OP planning:

| Scenario | Description |
|---|---|
| **Baseline** | Normal operating conditions |
| **Peak Demand +15%** | Demand surge simulation (seasonal peak, holiday) |
| **Promotion Surge +25%** | Flash sale or promotional event impact |
| **Capacity Constraint -10%** | Reduced warehouse capacity (labor shortage, disruption) |

Each scenario outputs **utilization %, max utilization %, and high-risk days** per warehouse — enabling leadership to evaluate fulfillment tradeoffs before events occur.

---

## 📈 Key KPIs Calculated

- **OTIF %** — On-Time In-Full delivery rate by carrier and warehouse
- **Inventory Turnover** — Demand / average on-hand units per SKU
- **Forecast Accuracy %** — `1 - (|actual - forecast| / actual)`
- **Reorder Risk Flag** — SKUs where minimum on-hand < reorder point
- **Capacity Utilization %** — Scenario demand / warehouse daily capacity
- **Inventory Value** — Average on-hand units × unit cost

---

## 🛠️ Tech Stack

| Tool | Usage |
|---|---|
| **Python** | Core pipeline and data engineering |
| **Pandas** | Data transformation and aggregation |
| **NumPy** | Statistical modeling and simulation |
| **Power BI / Tableau** | BI dashboard consumption (via CSV exports) |
| **Excel / Power Query** | Operational reporting |
| **AWS QuickSight** | Cloud BI compatibility |

---

## 🚀 How to Run

**1. Clone the repository**
```bash
git clone https://github.com/yaswanthsai1998/supply-chain-operations-analytics-platform.git
cd supply-chain-operations-analytics-platform
```

**2. Install dependencies**
```bash
pip install pandas numpy
```

**3. Generate synthetic data**
```bash
python src/generate_synthetic_data.py
```

**4. Run the analytics pipeline**
```bash
python src/run_pipeline.py
```

**5. View outputs**
- Processed KPIs → `data/processed/`
- BI-ready chart exports → `assets/`

---

## 📤 Outputs

| File | Description |
|---|---|
| `carrier_performance.csv` | OTIF %, delay days by carrier and warehouse |
| `inventory_kpis.csv` | Turnover, reorder risk, inventory value per SKU |
| `forecast_accuracy.csv` | Forecast vs. actual accuracy by SKU and warehouse |
| `scenario_analysis.csv` | Capacity utilization across 4 demand scenarios |
| `kpi_summary.csv` | Executive supply chain scorecard |
| `chart_source_otif_by_carrier.csv` | Power BI / Tableau ready OTIF chart data |
| `chart_source_scenario_utilization.csv` | Scenario utilization chart data |
| `chart_source_forecast_accuracy_risks.csv` | Top forecast risk SKUs |

---

## 👤 Author

**Yaswanth Sai**
Supply Chain Analyst | MBA – Business Analytics & Project Management
[LinkedIn](https://www.linkedin.com/in/naga-yaswanth-sai-kesanakurthy-5a09621b7/) • [GitHub](https://github.com/yaswanthsai1998)

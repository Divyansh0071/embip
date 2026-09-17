# Evaluation & Benchmarking Framework (`evaluation/`)

This directory contains golden ground-truth evaluation benchmark datasets, execution scripts, and reports for testing EMBIP's future AI agents (SQL Agent, RAG Engine, Analytics Agent, and Report Generator).

---

## 1. Directory Structure

```
evaluation/
├── datasets/
│   └── novamart_ground_truth.json  # 10 golden evaluation questions with exact calculated ground-truth
├── scripts/
│   └── generate_ground_truth.py    # Ground-truth metrics calculator derived directly from NovaMart dataset
├── reports/                        # Performance and accuracy benchmark reports
└── README.md                       # Documentation
```

---

## 2. Golden Evaluation Benchmark Suite (Phase 5)

| ID | Category | Question | Target Intent | Calculated Ground-Truth Answer |
| :--- | :--- | :--- | :--- | :--- |
| `eval_001` | Revenue | Total 3-Year Sales Revenue | Overall Revenue Aggregation | `₹2,132,681,669.01` |
| `eval_002` | Store Performance | Top Store by Total Revenue | Store Ranking | `NovaMart Connaught Place` (`₹385,350,508.93`) |
| `eval_003` | Sales Volume | Total Product Units Sold | Volume Aggregation | `276,972 units` |
| `eval_004` | Category Performance | Top Category by Revenue | Category Ranking | `Home Appliances` (`₹647,359,520.00`) |
| `eval_005` | Product Performance | Top 5 Best-Selling Products | Product Ranking | `SmartHome Voice Assistant Hub` (5,772 units) |
| `eval_006` | Customer Behavior | Highest Lifetime Spend Customer | Customer LTV | `Garima Vala` (`CUST-09538`) (`₹809,133.97`) |
| `eval_007` | Inventory | Products with Stock < 50 units | Low Stock Alert | `0 products` |
| `eval_008` | Time Trends | Calendar Year 2025 Revenue | Time Window Filter | `₹758,117,485.72` |
| `eval_009` | Profit/Margin | Total Gross Profit | Profit Margin | `₹581,712,866.00` (~27.27% margin) |
| `eval_010` | Comparative Analysis | Bandra Store 2024 vs 2025 Revenue | YoY Growth Comparison | 2024: `₹108.17M`, 2025: `₹118.42M` (`+9.48% YoY`) |

---

## 3. Regenerate Ground-Truth Answers

To recalculate the ground truth evaluation dataset directly from the generated CSV data:

```bash
backend\.venv\Scripts\python.exe evaluation/scripts/generate_ground_truth.py
```

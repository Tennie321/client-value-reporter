#!/usr/bin/env python3
"""
AI Agency Client Value & Impact Report Generator
=================================================
Calculates and generates professional ROI/impact reports for AI automation
agency clients. Use this to demonstrate delivered value for retention,
upsells, and case studies.

Usage:
  python ai_client_value_reporter.py
  python ai_client_value_reporter.py --interactive
  python ai_client_value_reporter.py --batch clients.csv

Standalone — zero dependencies. Works on Python 3.6+.
"""

import csv
import json
import os
import sys
from datetime import datetime, date
from pathlib import Path

# ── Helpers ──────────────────────────────────────────────────────────────────

def fmt_currency(n):
    """Format as $X,XXX.XX"""
    if n >= 0:
        return f"${n:,.2f}"
    return f"-${abs(n):,.2f}"

def fmt_pct(n):
    return f"{n * 100:.1f}%"

def strip_trailing_zeros(s):
    return s.rstrip("0").rstrip(".")

# ── Calculation Engine ───────────────────────────────────────────────────────

class ClientImpactReport:
    def __init__(self, *, client_name, industry, engagement_months,
                 monthly_invoice, hours_saved_per_month, hourly_rate,
                 revenue_increase_per_month, cost_reduction_per_month,
                 hours_saved_scalability_multiplier=1.0):
        self.client_name = client_name
        self.industry = industry
        self.engagement_months = engagement_months
        self.monthly_invoice = monthly_invoice
        self.hours_saved_per_month = hours_saved_per_month
        self.hourly_rate = hourly_rate
        self.revenue_increase_per_month = revenue_increase_per_month
        self.cost_reduction_per_month = cost_reduction_per_month
        self.hours_saved_scalability_multiplier = hours_saved_scalability_multiplier

    @property
    def labor_cost_saved_per_month(self):
        return self.hours_saved_per_month * self.hourly_rate * self.hours_saved_scalability_multiplier

    @property
    def total_monthly_value(self):
        return (self.labor_cost_saved_per_month +
                self.revenue_increase_per_month +
                self.cost_reduction_per_month)

    @property
    def total_value_to_date(self):
        return self.total_monthly_value * self.engagement_months

    @property
    def cumulative_invoice(self):
        return self.monthly_invoice * self.engagement_months

    @property
    def net_roi_dollars(self):
        return self.total_value_to_date - self.cumulative_invoice

    @property
    def roi_ratio(self):
        if self.cumulative_invoice == 0:
            return float("inf")
        return self.total_value_to_date / self.cumulative_invoice

    @property
    def roi_pct(self):
        return self.roi_ratio - 1.0

    @property
    def payback_months(self):
        if self.total_monthly_value <= 0:
            return float("inf")
        return self.monthly_invoice / self.total_monthly_value

    @property
    def annualized_value(self):
        return self.total_monthly_value * 12

    @property
    def value_to_cost_ratio(self):
        if self.monthly_invoice == 0:
            return float("inf")
        return self.total_monthly_value / self.monthly_invoice

    @property
    def hours_saved_total(self):
        return self.hours_saved_per_month * self.engagement_months * self.hours_saved_scalability_multiplier

    @property
    def hours_saved_cumulative_with_scaling(self):
        return self.hours_saved_per_month * self.engagement_months * self.hours_saved_scalability_multiplier

    # ── Report generation ──────────────────────────────────────────────────

    def generate_markdown_report(self):
        d = date.today().strftime("%B %d, %Y")
        roip = fmt_pct(self.roi_pct)
        val = fmt_currency(self.total_monthly_value)
        tot = fmt_currency(self.total_value_to_date)
        inv = fmt_currency(self.cumulative_invoice)
        net = fmt_currency(self.net_roi_dollars)
        hrs = f"{self.hours_saved_total:,.0f}"
        lab = fmt_currency(self.labor_cost_saved_per_month)
        rev = fmt_currency(self.revenue_increase_per_month)
        cost = fmt_currency(self.cost_reduction_per_month)
        ann = fmt_currency(self.annualized_value)
        pb  = f"{self.payback_months:.1f}" if self.payback_months != float("inf") else "N/A"
        vcr = f"{self.value_to_cost_ratio:.1f}x"
        moinv = fmt_currency(self.monthly_invoice)

        report = f"""# Client Value & Impact Report

**Client:** {self.client_name}
**Industry:** {self.industry}
**Report Date:** {d}
**Engagement Duration:** {self.engagement_months} months

---

## Executive Summary

Since engaging AI automation services, **{self.client_name}** has realized
**{tot}** in total measurable value against a total investment of **{inv}** —
a **{roip}** net return on investment.

**Current monthly value delivered: {val}**
**Monthly investment: {moinv}** (value-to-cost ratio: **{vcr}**)

---

## Value Breakdown

| Category | Monthly Value | Total to Date |
|---|---|---|
| Labor Cost Savings | {lab} | {fmt_currency(self.labor_cost_saved_per_month * self.engagement_months)} |
| Revenue Increase | {rev} | {fmt_currency(self.revenue_increase_per_month * self.engagement_months)} |
| Cost Reduction | {cost} | {fmt_currency(self.cost_reduction_per_month * self.engagement_months)} |
| **Total** | **{val}** | **{tot}** |

---

## Efficiency Metrics

| Metric | Value |
|---|---|
| Hours Saved per Month | {self.hours_saved_per_month:,.0f} |
| Total Hours Saved | {hrs} |
| Effective Hourly Rate of Hours Saved | {fmt_currency(self.hourly_rate)} |
| Scalability Multiplier | {self.hours_saved_scalability_multiplier:.1f}x |
| Payback Period | {pb} months |
| Annualized Value | {ann} |
| Net ROI | {net} |
| ROI Percentage | {roip} |

---

## Annualized Projection

If current value delivery continues, **{self.client_name}** will realize
**{ann}** in annual value — representing a **{vcr}** return on every dollar
invested in automation services.

---

## Key Takeaways

1. **{fmt_currency(self.hours_saved_per_month * self.hourly_rate)}/month** in labor cost savings
   alone — equivalent to recovering {self.hours_saved_per_month:,.0f} employee hours monthly.
2. **{fmt_currency(self.revenue_increase_per_month)}/month** in incremental revenue
   directly attributable to automation initiatives.
3. **{fmt_currency(self.cost_reduction_per_month)}/month** in ongoing operational cost reduction.
4. **{vcr} value-to-cost ratio** — every $1 invested returns ${vcr.replace('x','')} in measurable value.

---

*Report generated by AI Agency Client Value & Impact Report Generator*
*{d}*
"""
        return report

    def to_dict(self):
        return {
            "client_name": self.client_name,
            "industry": self.industry,
            "engagement_months": self.engagement_months,
            "monthly_invoice": self.monthly_invoice,
            "hours_saved_per_month": self.hours_saved_per_month,
            "hourly_rate": self.hourly_rate,
            "revenue_increase_per_month": self.revenue_increase_per_month,
            "cost_reduction_per_month": self.cost_reduction_per_month,
            "hours_saved_scalability_multiplier": self.hours_saved_scalability_multiplier,
            "total_monthly_value": self.total_monthly_value,
            "total_value_to_date": self.total_value_to_date,
            "cumulative_invoice": self.cumulative_invoice,
            "net_roi_dollars": self.net_roi_dollars,
            "roi_ratio": self.roi_ratio,
            "roi_pct": self.roi_pct,
            "payback_months": self.payback_months,
            "annualized_value": self.annualized_value,
            "value_to_cost_ratio": self.value_to_cost_ratio,
            "total_hours_saved": self.hours_saved_total
        }


# ── Interactive Mode ─────────────────────────────────────────────────────────

def interactive_mode():
    print("=" * 62)
    print("  AI Agency Client Value & Impact Report Generator")
    print("=" * 62)
    print()

    client = input("Client name: ").strip()
    industry = input("Industry (e.g., Real Estate, E-commerce, Legal): ").strip()
    months = int(input("Engagement duration (months): ").strip())
    invoice = float(input("Monthly invoice amount ($): ").strip())
    hrs = float(input("Hours saved per month (automation): ").strip())
    rate = float(input("Effective hourly rate of saved hours ($): ").strip())
    rev = float(input("Revenue increase per month ($): ").strip())
    cost = float(input("Cost reduction per month ($): ").strip())
    scale = float(input("Scalability multiplier (default 1.0): ").strip() or "1.0")

    report = ClientImpactReport(
        client_name=client,
        industry=industry,
        engagement_months=months,
        monthly_invoice=invoice,
        hours_saved_per_month=hrs,
        hourly_rate=rate,
        revenue_increase_per_month=rev,
        cost_reduction_per_month=cost,
        hours_saved_scalability_multiplier=scale
    )

    md = report.generate_markdown_report()
    print()
    print(md)

    out_dir = Path("client_reports")
    out_dir.mkdir(exist_ok=True)
    safe_name = client.lower().replace(" ", "_").replace("'", "").replace('"', "")
    fname = out_dir / f"{safe_name}_impact_report.md"
    fname.write_text(md)
    print(f"✅ Report saved to {fname}")

    # Also save as JSON
    jname = out_dir / f"{safe_name}_impact_report.json"
    jname.write_text(json.dumps(report.to_dict(), indent=2))
    print(f"✅ JSON data saved to {jname}")

    return report


# ── Batch Mode ────────────────────────────────────────────────────────────────

def batch_mode(csv_path):
    reports = []
    out_dir = Path("client_reports")
    out_dir.mkdir(exist_ok=True)

    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            report = ClientImpactReport(
                client_name=row["client_name"],
                industry=row.get("industry", "General"),
                engagement_months=int(row["engagement_months"]),
                monthly_invoice=float(row["monthly_invoice"]),
                hours_saved_per_month=float(row["hours_saved_per_month"]),
                hourly_rate=float(row["hourly_rate"]),
                revenue_increase_per_month=float(row.get("revenue_increase_per_month", 0)),
                cost_reduction_per_month=float(row.get("cost_reduction_per_month", 0)),
                hours_saved_scalability_multiplier=float(row.get("hours_saved_scalability_multiplier", 1.0))
            )
            reports.append(report)
            safe_name = report.client_name.lower().replace(" ", "_").replace("'", "").replace('"', "")
            fname = out_dir / f"{safe_name}_impact_report.md"
            fname.write_text(report.generate_markdown_report())
            print(f"✅ {report.client_name} → {fname}")

    # Summary CSV
    summary_path = out_dir / "all_clients_summary.csv"
    with open(summary_path, "w", newline="") as f:
        fieldnames = list(reports[0].to_dict().keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in reports:
            writer.writerow(r.to_dict())
    print(f"✅ Summary → {summary_path}")
    return reports


# ── Sample Data ───────────────────────────────────────────────────────────────

def generate_sample_csv():
    sample = [
        {"client_name": "BrightStar Realty", "industry": "Real Estate",
         "engagement_months": 6, "monthly_invoice": 2500,
         "hours_saved_per_month": 40, "hourly_rate": 75,
         "revenue_increase_per_month": 5000, "cost_reduction_per_month": 2000,
         "hours_saved_scalability_multiplier": 1.2},
        {"client_name": "GreenLeaf Legal", "industry": "Legal",
         "engagement_months": 4, "monthly_invoice": 3500,
         "hours_saved_per_month": 60, "hourly_rate": 100,
         "revenue_increase_per_month": 8000, "cost_reduction_per_month": 1500,
         "hours_saved_scalability_multiplier": 1.0},
        {"client_name": "MedConnect Health", "industry": "Healthcare",
         "engagement_months": 8, "monthly_invoice": 3000,
         "hours_saved_per_month": 50, "hourly_rate": 85,
         "revenue_increase_per_month": 6000, "cost_reduction_per_month": 3000,
         "hours_saved_scalability_multiplier": 1.5},
        {"client_name": "Summit Ecom", "industry": "E-commerce",
         "engagement_months": 3, "monthly_invoice": 2000,
         "hours_saved_per_month": 30, "hourly_rate": 65,
         "revenue_increase_per_month": 12000, "cost_reduction_per_month": 1000,
         "hours_saved_scalability_multiplier": 1.0},
    ]
    path = "sample_clients.csv"
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=sample[0].keys())
        w.writeheader()
        w.writerows(sample)
    print(f"✅ Sample CSV created: {path}")
    return path


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("AI Agency Client Value & Impact Report Generator")
    print("=" * 55)
    print()

    args = sys.argv[1:]

    if "--sample" in args:
        generate_sample_csv()
        return

    if "--batch" in args:
        idx = args.index("--batch")
        if idx + 1 < len(args):
            csv_path = args[idx + 1]
            if not os.path.exists(csv_path):
                print(f"❌ CSV not found: {csv_path}")
                sys.exit(1)
            batch_mode(csv_path)
        else:
            print("Usage: --batch <path-to-csv>")
            sys.exit(1)
        return

    if "--json" in args:
        # Generate a standalone JSON output example
        report = ClientImpactReport(
            client_name="Acme Corp",
            industry="Real Estate",
            engagement_months=6,
            monthly_invoice=2500,
            hours_saved_per_month=40,
            hourly_rate=75,
            revenue_increase_per_month=5000,
            cost_reduction_per_month=2000,
            hours_saved_scalability_multiplier=1.2
        )
        print(json.dumps(report.to_dict(), indent=2))
        return

    if "--help" in args or "-h" in args or len(args) == 0 or "--interactive" in args:
        print("Modes:")
        print("  (default / --interactive)  Guided input mode")
        print("  --batch <csv>              Process multiple clients from CSV")
        print("  --sample                   Generate sample CSV file")
        print("  --json                     Output example as JSON")
        print("  --help                     This message")
        print()
        if "--help" in args or "-h" in args:
            return
        interactive_mode()
        return

    # Fallback: default interactive
    interactive_mode()


if __name__ == "__main__":
    main()
# Phase 3 — Silver to Gold, Analytics and AI Roadmap

Implementation begins only after Gate 2.

## Outcome

- business-owned Gold data products;
- versioned metric definitions and dimensional models;
- Athena for ad-hoc workloads and Redshift Serverless for repeated BI workloads when justified;
- QuickSight dashboards with freshness and access SLOs;
- Lake Formation permissions and traceable lineage;
- SageMaker/Bedrock use only approved Silver/Gold datasets;
- evaluation and human oversight before AI outputs influence decisions.

## Example market-data products

- `price_by_minute`;
- `trading_volume_by_asset`;
- `realized_volatility`;
- `top_movers`;
- `market_activity_summary`;
- anomaly features with documented windows and thresholds.

## Core evidence

- approved semantic definitions;
- query accuracy, freshness, performance, and cost reports;
- column/table access tests;
- source-to-metric lineage;
- dashboard operational runbook;
- model evaluation, drift, privacy, and approval evidence.

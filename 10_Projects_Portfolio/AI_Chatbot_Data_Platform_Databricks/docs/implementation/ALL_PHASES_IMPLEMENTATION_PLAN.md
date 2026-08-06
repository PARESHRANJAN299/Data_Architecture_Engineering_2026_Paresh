# End-to-End Implementation Phases

The project is divided into seven phases. Each phase introduces a clear process change and a clear business or technical benefit.

---

## Phase 1 - Foundation and live ingestion

### Objective

Create the first complete live path:

```text
Open Food Facts + Scala commerce simulator
        ↓
Kafka
        ↓
Databricks Bronze Delta
```

### Main work

- finalize the event model
- create Kafka topics
- build the Scala product collector
- build the Scala commerce simulator
- publish product and business events
- create Databricks Bronze ingestion
- configure checkpoints
- record Kafka metadata
- add basic logging and monitoring

### Process change

Before Phase 1, data is manually collected or exists only as disconnected source records.

After Phase 1:

- events flow automatically
- data arrives continuously
- every event has a stable identity
- raw history is stored in one place
- failures can be replayed

### Function change

The platform gains the ability to:

- collect real product data
- generate live commerce activity
- transport events reliably
- ingest streaming data into Delta
- restart from checkpoints

### Benefits

- removes manual data loading
- establishes the production data path
- creates a raw source of truth
- enables near-real-time monitoring
- provides the foundation for every later phase

### Phase 1 deliverables

- Docker Compose Kafka environment
- Kafka topic creation scripts
- Scala product collector
- Scala commerce simulator
- event schemas
- sample events
- Bronze streaming pipeline
- Bronze Delta tables
- checkpoint configuration
- dead-letter topic
- test evidence
- runbook

### Phase 1 success criteria

- live product events reach Kafka
- simulated customer, order, payment, inventory, and clickstream events reach Kafka
- Databricks writes all event families into Bronze
- restarting jobs continues from checkpoints
- malformed events reach the dead-letter path
- Kafka offsets and Bronze row counts reconcile

---

## Phase 2 - Silver data quality and trusted records

### Objective

Convert raw Bronze events into clean and reliable business entities.

### Main work

- parse payloads using explicit schemas
- remove duplicates
- enforce data contracts
- validate required fields
- standardize timestamps and currency
- join orders to customers and products
- process payment states
- apply inventory movements
- build clickstream sessions
- quarantine invalid records
- handle late events

### Process change

Before Phase 2, teams must interpret raw events themselves.

After Phase 2:

- data rules are centralized
- bad records are separated
- duplicate delivery does not duplicate business records
- each business entity has a trusted definition

### Function change

The platform gains:

- clean products
- clean customers
- clean orders
- clean payments
- clean inventory movements
- sessionized clickstream data
- reusable quality rules

### Benefits

- reduces reporting errors
- improves pipeline reliability
- gives all teams consistent data
- simplifies analysis
- supports safe replay

### Key Silver tables

- `products`
- `customers`
- `orders`
- `order_items`
- `payments`
- `inventory_events`
- `clickstream_events`
- `customer_sessions`
- `quarantined_events`

---

## Phase 3 - Gold business models and KPIs

### Objective

Transform trusted Silver data into business-ready models.

### Main work

- define sales metrics
- define product metrics
- define customer metrics
- build star-schema dimensions and facts
- create daily and monthly aggregates
- create semantic views
- optimize Gold tables for BI
- document KPI definitions

### Process change

Before Phase 3, analysts repeatedly rebuild metrics from detailed records.

After Phase 3:

- calculations are reusable
- KPI definitions are consistent
- reporting becomes faster
- senior stakeholders see one version of the truth

### Function change

The platform gains:

- revenue reporting
- product-performance reporting
- customer-growth reporting
- inventory reporting
- reusable semantic datasets

### Benefits

- faster decision-making
- lower analyst effort
- consistent executive reporting
- better query performance
- easier self-service BI

### Key Gold products

- `sales_daily`
- `sales_monthly`
- `product_performance_daily`
- `customer_growth_daily`
- `inventory_risk_daily`
- `conversion_funnel_daily`
- `executive_kpis`

---

## Phase 4 - BI and self-service analytics

### Objective

Deliver dashboards and governed analyst access.

### Main work

- configure Databricks SQL warehouse
- create executive dashboards
- create product dashboards
- create customer dashboards
- create inventory dashboards
- define access groups
- validate dashboard freshness and cost

### Process change

Before Phase 4, users depend on engineers for every question.

After Phase 4:

- analysts query governed data directly
- executives receive current KPIs
- operational teams monitor live performance

### Function change

The platform gains:

- executive reporting
- self-service SQL
- shared dashboards
- operational monitoring
- governed data access

### Benefits

- faster answers
- better transparency
- lower reporting dependency
- stronger business alignment

---

## Phase 5 - AI and machine learning

### Objective

Use the lakehouse data to create predictive and recommendation capabilities.

### Main work

- build feature tables
- create training snapshots
- train demand forecasting models
- build recommendation features
- build churn and segmentation models
- track experiments with MLflow
- register approved models
- run batch scoring
- optionally deploy online endpoints

### Process change

Before Phase 5, the company reacts to past events.

After Phase 5:

- the platform predicts future demand
- products can be recommended
- high-risk customers can be identified
- inventory decisions become proactive

### Function change

The platform gains:

- demand forecasts
- product recommendations
- churn scores
- customer segments
- anomaly scores

### Benefits

- revenue-growth opportunities
- improved customer experience
- reduced inventory waste
- better targeting
- proactive operations

---

## Phase 6 - Governance, security, and environments

### Objective

Make the platform safe for multiple teams and environments.

### Main work

- create dev, stage, and prod catalogs
- configure Unity Catalog
- define ownership
- apply role-based access
- protect sensitive customer fields
- configure service principals
- manage secrets
- record lineage and audit activity
- define retention policies

### Process change

Before Phase 6, access and deployment may be informal.

After Phase 6:

- permissions are controlled centrally
- assets have clear owners
- environments are separated
- access is auditable

### Function change

The platform gains:

- governed data access
- row and column protection
- catalog lineage
- environment isolation
- controlled service identities

### Benefits

- lower security risk
- better compliance readiness
- safer collaboration
- clear accountability
- easier production approval

---

## Phase 7 - Production reliability, CI/CD, and scale testing

### Objective

Prove that the platform can operate reliably under production-style load.

### Main work

- package deployments with Databricks Asset Bundles
- automate tests
- deploy through GitHub Actions
- add freshness and lag alerts
- monitor cost and throughput
- test replay and backfill
- test job restart
- test partition skew
- test high event volume
- document disaster recovery
- define SLOs and operational runbooks

### Process change

Before Phase 7, releases and recovery depend on manual knowledge.

After Phase 7:

- releases are repeatable
- failures are detected quickly
- recovery steps are documented
- capacity limits are measured

### Function change

The platform gains:

- automated deployment
- automated validation
- production monitoring
- replay and recovery
- scale certification
- cost controls

### Benefits

- reduced downtime
- safer releases
- predictable performance
- lower operational risk
- evidence-based scaling decisions

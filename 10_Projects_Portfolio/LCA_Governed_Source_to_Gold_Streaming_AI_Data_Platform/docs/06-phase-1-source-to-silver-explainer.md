# Phase -1 — Source-to-Silver Backend Explainer

**Owner:** Paresh Ranjan Rout

## One-page architecture

![Phase 1 source-to-Silver complete flow](../architecture/phase-1-source-to-silver-complete-flow.svg)

This diagram is the end-to-end learning and deployment view. The main README execution tracker remains the authority for which steps are built and verified.

## Final agreed processing rule

```text
Coinbase source JSON
    → transport unchanged through ECS and Kinesis
    → batch unchanged into S3 Bronze JSON.GZIP objects
    → standardize, validate and transform in Glue/Spark
    → commit to one logical Silver Iceberg table
    → obtain business approval before building Gold
```

Bronze is the immutable source copy. It preserves Coinbase field names, values and nested message structure. The first business transformation occurs while Glue/Spark creates Silver.

## Service-by-service responsibility

| Step | Service | Exact responsibility | It does not do |
|---:|---|---|---|
| 1 | Coinbase WebSocket | Sends live `market_trades` JSON messages | Create S3 files or Silver tables |
| 2 | ECS Fargate adapter | Connect, subscribe, monitor heartbeat, reconnect and pass raw messages | Rename columns, aggregate trades or create business facts |
| 3 | Kinesis Data Streams | Accept and retain many streaming records for consumers/replay | Combine records into S3 objects |
| 4 | Data Firehose | Read Kinesis, buffer records by time/size, compress and deliver batches | Append forever to one S3 object |
| 5 | S3 Bronze | Store many immutable JSON.GZIP batch objects under one dataset prefix | Present dimension/fact tables |
| 6 | Glue/Spark | Incrementally read new Bronze objects, explode trades, cast, rename, deduplicate and run quality rules | Change the Bronze source history |
| 7 | Apache Iceberg Silver | Commit standardized rows and manage table snapshots/files | Store everything in one appendable Parquet file |
| 8 | Glue Data Catalog | Store `silver.fact_market_trade` and its current Iceberg metadata location | Store all trade rows directly |
| 9 | Athena/Spark | Resolve the Catalog entry and Iceberg metadata, then read required Parquet files | Manually discover every S3 file |

## Questions resolved during architecture review

### Does every Kinesis event create one S3 object?

No. Firehose buffers many Kinesis records and writes them together. Object count is controlled by delivery buffering, data rate, compression and partitioning.

### Can S3 maintain one file and append every new event?

No. S3 data-lake objects are immutable delivery units. Each Firehose flush creates a new object. The Bronze prefix is the dataset; an individual object is only one batch within it.

### If one Bronze dataset has ten batch files, does Silver create ten tables?

No. Glue/Spark reads the ten objects for that dataset and appends their standardized rows to one logical table, such as `silver.fact_market_trade`.

### If four Bronze datasets contain forty files, how many Silver tables are created?

The mapping is controlled by dataset contracts, not file count:

```text
10 market-trade batches → silver.fact_market_trade
10 instrument batches   → silver.dim_instrument
10 ticker batches       → silver.fact_ticker
10 candle batches       → silver.fact_candle
```

The result is four logical Silver tables.

### Why can one Iceberg table contain several Parquet files?

Parquet files are physical S3 objects and are not continuously appendable. Iceberg manages those files through snapshots and manifests. Users query the one logical table name rather than the individual files.

### How does the query engine know which files belong to the table?

```text
Athena/Spark
    → Glue Catalog entry: silver.fact_market_trade
    → current Iceberg metadata JSON
    → snapshot and manifest files
    → required Parquet files
```

### Why not use CSV to obtain one file?

CSV objects in S3 also do not solve continuous append. CSV additionally loses strong typing, column pruning and efficient compression. Silver therefore uses Iceberg with Parquet; a single CSV can be generated later only as an export.

## Deployment sequence and proof

| Order | Build | Required proof before continuing |
|---:|---|---|
| 1 | Connect locally to Coinbase | Heartbeat and trade messages captured safely |
| 2 | Send unchanged source messages to a local/test sink | Byte/payload comparison proves no business transformation |
| 3 | Publish raw messages to Kinesis | Received and acknowledged counts reconcile |
| 4 | Deliver Kinesis records through Firehose | Multiple input records appear in batched JSON.GZIP Bronze objects |
| 5 | Run incremental Glue/Spark processing | Only new Bronze objects are processed; trade arrays become rows |
| 6 | Create `silver.fact_market_trade` as Iceberg | Glue Catalog entry, metadata JSON, snapshot, manifests and Parquet files exist |
| 7 | Query through Athena | Table count and values reconcile to the processed Bronze window |
| 8 | Run compaction when file metrics justify it | Fewer/larger data files with unchanged row-level result |
| 9 | Run Silver quality and business review | Approved names, types, null rules, deduplication and definitions |
| 10 | Begin Gold only after approval | Approval record links to the accepted Silver contract |

## Silver approval loop

```text
Create standardized Silver table
    → run technical quality checks
    → business reviews columns and definitions
        → rejected: modify Silver rules, rebuild and resubmit
        → approved: version the contract and begin Gold
```

SCD Type 2 is applied only to dimensions that require attribute-history tracking. Trade facts remain append-oriented and are not automatically modeled as SCD Type 2.

# Data Contract — <source system name>

**Producer team:**
**Producer contact:**
**Consumer:** LCA Governed Data Platform
**Effective date:**
**Version:**

## 1. Delivery

Ingestion mechanism: DMS CDC / Kinesis / IoT Core / Firehose
Expected frequency:
Expected volume (records per day):
Freshness SLA:

## 2. Schema

| Field | Type | Nullable | Contains PII | Description |
|---|---|---|---|---|
| | | | | |

## 3. Guarantees the producer makes

- Field types will not change without notice
- Required fields will always be present
- Schema version will be incremented on any change
- Notice period before a breaking change:

## 4. What counts as a breaking change

- Removing a field
- Changing a field's type
- Changing the meaning of an existing field
- Changing the grain of the data

## 5. What happens on violation

Records failing schema validation are quarantined, not dropped. The producer is notified via the quarantine-rate alarm. Sustained violation is escalated to the data owner.

## 6. Sign-off

| Role | Name | Date |
|---|---|---|
| Producer owner | | |
| Platform owner | Paresh Ranjan Rout | |

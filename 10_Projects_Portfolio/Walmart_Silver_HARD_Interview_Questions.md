# Hardest Scenario-Level Interview Questions — Walmart Silver Merge

*Senior/Lead-level. These test judgment, edge cases, and trade-offs — not just definitions. For each, the model answer shows the depth an interviewer wants. Practice reasoning out loud.*

---

## ⭐ TOP QUESTION (the one that separates senior from junior)

**Q0. Walk me through how you'd merge 4 source tables into one Silver table, and everywhere you could silently produce WRONG data — and how you'd catch each one before it reaches the model.**

Model answer (the full reasoning):
1. **Start from the fact (sales).** LEFT join dimensions onto it so no sales row is lost.
2. **Row multiplication** — the biggest silent risk. If any joined table has >1 row per key, sales inflate. Catch it: compare total vs distinct key count per dimension before joining; if a table (like store/ecomm inventory) is finer-grained, dedup or aggregate first.
3. **Wrong join key** — if the same item has different key values across tables, joining on the wrong one links to the wrong product/brand. Catch it: compare key values across tables (SAME vs DIFFERENT); investigate patterns (a constant offset = masking, not real difference); confirm the correct key with the data owner.
4. **Duplicate column names** — crashes the job or, worse, silently keeps the wrong one. Catch it: enumerate columns appearing in >1 table; rename by source; keep join keys once.
5. **Same name, different data** — dropping one loses info. Catch it: value-compare matched rows; keep both (renamed) when different.
6. **Partial referential match** — a low FK match rate may be normal (channel-specific inventory) or a data gap. Catch it: break down non-matches by dimension (channel, date) to explain the gap.
7. **Validate the output** — row count ≈ fact count (no inflation), null rates on keys, referential match rates. Only then promote.

Key line: *"The output looking fine is not proof it's correct. I verify each join's grain, key, and match rate before trusting it — because for a causal model, silently-wrong data is worse than a crash."*

---

## Section A — Deep Join & Grain Edge Cases

**Q1. Your sales fact has a composite key (item + catlg + date + channel). You LEFT join a dimension keyed only on item. The row count triples. Explain exactly why, and whether it's a bug.**
The dimension has multiple rows per item (not unique on item alone). Each sales row matches all of them → multiplication. It's a bug *if* the dimension should be one-per-item; it's expected *if* the dimension is legitimately finer (e.g. item+effective-date) and you forgot to pick the right version. Fix: dedup the dimension to the grain you need (latest by effective date) before joining.

**Q2. You must join inventory that is at item-per-store-per-day grain to sales at item-per-day grain. How do you avoid a 500× explosion but still keep useful inventory info?**
Don't join raw. First aggregate inventory to the sales grain: group by item+day, sum/avg the inventory measures (e.g. total on-hand qty across stores). Then join the aggregated (item+day) inventory to sales. This preserves inventory signal without multiplying sales rows.

**Q3. A LEFT join is giving NULLs you didn't expect on the right side. List every possible cause and how you'd isolate the real one.**
Causes: (a) key genuinely absent on the right; (b) key present but value differs (masking/format); (c) a secondary join key (like op_cmpny_cd) is too strict and knocks out matches; (d) type mismatch (string vs int key); (e) whitespace/case differences in string keys. Isolate: check match rate on the primary key alone, then add secondary keys one at a time to see which drops matches; sample the NULL rows and look up their key on the right table directly.

**Q4. You join on two keys (item + company_code). Company_code is ~87% the same across tables. What's the risk, and would you keep it in the join?**
Risk: the 13% where company_code differs will FAIL to match even though the item is the same → lost matches / unexpected NULLs. Decide by testing: join on item only vs item+company_code and compare match rates. If company_code drops many valid matches, join on item alone and keep company_code as a data column, not a key.

**Q5. Explain how you'd detect a "fan-out then aggregate" bug where a sum is silently doubled.**
Fan-out (a join multiplied rows) followed by SUM double-counts. Detect: sum a measure BEFORE the join and AFTER; they must match for the fact's own measures. If the post-join sum is larger, a join multiplied rows. Also compare distinct grain-key count before/after join — it should be unchanged for the fact.

---

## Section B — Data Correctness & Trust

**Q6. A join key is 100% different between two tables in sandbox. Your manager says "just build it, we're behind schedule." What do you do?**
Push back with evidence, briefly and respectfully. Show that building on an unverified key risks linking sales to the wrong product — silently-wrong data that's expensive to unwind and pollutes the model. Offer a fast path: a 10-minute check of whether the difference is a pattern (masking) or real, and confirm the correct key. Speed that produces wrong data isn't speed.

**Q7. You discover the difference is a constant +1111 offset. How confident are you it's masking, and how would you be sure before relying on it?**
A constant offset across 100% of rows strongly suggests systematic masking, not real data. But "strongly suggests" isn't "sure." To confirm: check whether the downstream tables (product/ecomm) still match on the masked value (if they do, masking is internally consistent); and confirm with the data owner that production is unmasked. Rely on it only after both.

**Q8. How do you distinguish a data-quality problem from expected business behavior when a match rate is low?**
Decompose the non-matches by a business dimension. Example: only 37% of items match ecomm inventory — break the non-matches down by sales channel. If they're mostly store-only items, low ecomm match is expected. If online-sold items also lack inventory, that's a real gap. Business context turns a scary number into an explained one.

**Q9. Your Silver table feeds a causal model. Why is a subtle 2× inflation worse here than in a normal BI dashboard?**
A dashboard shows a wrong number a human might sanity-check. A causal model *learns relationships* from the data — inflated volume distorts the estimated effect of drivers (e.g. overstates a promotion's lift), producing confidently-wrong causal conclusions that drive real budget decisions. The error is laundered into a "scientific" recommendation.

**Q10. How would you build automated guardrails so this pipeline can't silently ship inflated data?**
DLT expectations + reconciliation: (a) expect row count within tolerance of the fact count; (b) expect distinct grain-key count unchanged post-join; (c) expect key null rate below a threshold; (d) expect FK match rates within known ranges; (e) fail or quarantine on violation, and log every check to a quality table with alerting.

---

## Section C — Schema, Columns, Governance

**Q11. "Keep all columns" gives you a 330-column table with 24 duplicate names, many identical. Defend keeping vs trimming.**
Keep (literal instruction, owner reviews everything, easy to trim later, hard to un-drop): right for a first Silver where UL must see everything. Trim (identical columns are noise, wide tables cost storage/scan, confusing downstream): right once the owner confirms what's redundant. Resolution: keep all now, flag the identical duplicates to the owner, trim in a later iteration with sign-off — don't unilaterally drop on a shared deliverable.

**Q12. Two columns share a name and are identical in sandbox. Would you drop one? What could go wrong if you do?**
Risk: "identical in sandbox" may not hold in production (masking can make sandbox values collapse). Dropping based on sandbox could lose a column that genuinely differs in prod. Safer: keep both (renamed) until you've confirmed on production data, or confirm with the owner. Decisions made on masked sandbox data are suspect.

**Q13. How do you make the rename scheme robust so adding a 5th source later doesn't break the pipeline?**
Drive renaming by config, not hardcoding: define join keys per source, and a function that prefixes all non-key columns by source name. Adding a source = add its key set + prefix; the merge logic is generic. Avoid manual per-column renames that rot as schemas evolve.

**Q14. Source adds a new column next month. What happens to your pipeline, and how do you want it to behave?**
With schema enforcement it may fail; with blind evolution it may silently absorb an unvetted column. Preferred: detect the drift (compare current vs expected schema), alert, and decide — auto-add if it's clearly safe (new descriptive column) or hold for review if it affects keys/measures. Never let an unknown column silently flow to a model unreviewed.

**Q15. Why keep Bronze raw and untouched even though it "wastes" storage by duplicating source data?**
Bronze is the immutable landing zone: it lets you reprocess Silver/Gold if transform logic changes, audit exactly what the source sent, and recover from downstream bugs without re-pulling from the source API. Storage is cheap; losing the ability to reproduce/audit is expensive. Raw Bronze is a correctness and trust guarantee, not waste.

---

## Section D — Production, Scale, Ops

**Q16. Sandbox has 6 days and 126K rows; production has years and billions. What breaks or changes?**
Full-table DISTINCT/dedup gets expensive (shuffles); joins need broadcast vs shuffle decisions; you need incremental processing (only new partitions), partitioning (by date), OPTIMIZE/Z-ORDER, and skew handling. The *logic* stays; the *execution strategy* and *cost controls* change. Validate on a representative slice, not just 6 days.

**Q17. Your dedup keeps "latest inventory row per item by date." At billion scale this window function is slow. Alternatives?**
Options: pre-filter to the needed date partition before windowing; use a max-date join instead of row_number; maintain inventory as an SCD/current-snapshot table upstream so Silver reads a pre-deduped source; or aggregate rather than pick-latest if the business wants totals. Choose based on what "current inventory" should mean.

**Q18. How do you make this pipeline idempotent so re-running never duplicates or corrupts data?**
Use Delta MERGE / DLT (declarative, recomputes deterministically) rather than blind append; key the target; ensure the transform is a pure function of inputs. Delta's ACID commits mean partial runs don't corrupt; re-running reproduces the same result. Validate with a duplicate check (total vs distinct) after runs.

**Q19. The daily job partially failed — some tables refreshed, some didn't. Is the data corrupt? What do you do?**
Not corrupt (Delta writes are atomic — each table's write fully commits or not). But the dataset may be *inconsistent* (mixed fresh/stale). Action: re-run to completion before anyone consumes it; verify with row counts/timestamps that all targets are current; add task dependencies + alerting so a partial failure is visible and auto-retried.

**Q20. How do you promote from sandbox to production safely, table-name and validation-wise?**
Parameterize environment (sandbox vs prod table names/schemas) — no hardcoded suffixes. In prod: verify keys match on real (unmasked) data, run on a backfill slice first, compare metrics to a known baseline, enable quality expectations, then schedule. Gate go-live on validation, not on "it ran."

---

## Section E — The Killers (curveballs)

**Q21. If both a LEFT join and a properly-deduped dimension still change your fact's total sales, what happened?**
The "dimension" wasn't actually unique after your dedup (dedup key was wrong), OR the join key isn't unique on the fact side either (many-to-many), OR a filter/expectation dropped rows. Diagnose: recompute fact total pre-join; check dedup produced true 1-row-per-key; check the join isn't many-to-many on both sides.

**Q22. Interviewer: "Just use FULL OUTER join to be safe — you never lose anything." Respond.**
FULL doesn't lose rows, but it *adds* rows that don't belong in a sales table (unsold items, dimension-only records with NULL sales), changing the table's meaning and grain. "Losing nothing" isn't the goal; *correct semantics* is. For a sales fact you want LEFT from sales, so the table stays "one row per sale."

**Q23. How could a join produce the RIGHT row count but the WRONG data?**
Many-to-one that happens to net out numerically, a key that matches the wrong-but-equal-cardinality record (e.g. joining on a masked key that coincidentally maps 1:1 to a different item), or a coalesce picking the wrong duplicate column. Row count is necessary but not sufficient — you also validate values/spot-checks and referential correctness.

**Q24. You're told "the numbers look right to the business, ship it," but your reconciliation flags a 3% row inflation. What do you do?**
Investigate the 3% before shipping. "Looks right" is aggregate eyeballing; 3% inflation can hide in a segment and bias the model. Find which key multiplied, show the root cause, quantify the impact. If it's benign (explained real sales), document it; if it's a defect, fix it. Don't let social pressure override a failing check.

**Q25. Design the single most important automated test that would have caught every silent bug you hit in this project.**
A post-build reconciliation test: assert (a) Silver row count == fact row count (no multiplication), and (b) fact measure totals (sales, qty) are unchanged before vs after all joins. This single invariant catches row multiplication, bad dedup, and many-to-many joins — the failure modes that silently corrupt a fact table. Wire it as a DLT expectation that fails the run.

---

## How to use this set
- **Master Q0 and Q25 first** — they're the "senior signal" answers.
- For each, explain the *reasoning and trade-off*, not a one-word answer.
- Recurring senior themes: **grain, verify-before-trust, semantics over convenience, guardrails, and correctness for a causal model.**
- You lived most of these today — anchor each answer in what you actually did (the +1111 masking, the row-multiply check, the 37% ecomm decomposition).

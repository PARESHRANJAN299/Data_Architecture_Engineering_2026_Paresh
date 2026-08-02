# 30 Interview Questions — Walmart Silver Merge Scenario

*Based on your real Walmart LCA Silver pipeline project. Each question has a short model answer. Practice saying the answers out loud in plain English.*

---

## Section A — Joins & Keys (the core)

**Q1. You have a sales fact table and 3 other tables to merge. Which join type do you use and why?**
LEFT join from the sales fact (center). Because you want to keep every sales row even if a matching detail row is missing. INNER would drop sales with no match; FULL would add non-sales rows (unsold items). LEFT keeps all sales, fills NULL where no match.

**Q2. What is the difference between a LEFT join and a FULL OUTER join? Give an example.**
LEFT keeps all rows from the left table + matches from the right (NULL if no match). FULL keeps all rows from BOTH tables. Example: left ages 1,2,3,4 and right 1,2,5,6 → LEFT keeps 1,2,3,4 (5,6 dropped); FULL keeps 1,2,3,4,5,6.

**Q3. Two tables both have a column called `catlg_item_id`. You join them on a different key. What error happens?**
An "ambiguous column" / "duplicate column names" error. Both `catlg_item_id` columns survive the join (since they weren't the join key), giving two columns with the same name, which Spark rejects.

**Q4. How do you fix duplicate column names when merging tables but keeping all columns?**
Rename the clashing non-key columns by their source table (e.g. `item_brand_nm`, `product_brand_nm`). Keep the join keys once. This keeps all data and removes the name clash.

**Q5. Same column name in two tables — does it mean same data? How do you check?**
No. Same name ≠ same data. Verify by joining on the key and comparing values row-by-row: count SAME vs DIFFERENT. Columns can carry different info from different source systems.

**Q6. When is a duplicate column NOT a problem to worry about (only the name matters)?**
The duplicate *values* aren't the problem — you keep both if different. The only technical problem is the duplicate *name* clashing on join. Fix the name (rename), and different values are fine to keep side by side.

**Q7. A dimension table's key appears in your fact table too, but it's not the join key for that pair. What do you do with it?**
It's redundant for that join (you joined on another key). Either drop it or rename it. If it carries no needed info, drop it; if it might be useful, rename by source and keep it.

**Q8. What is a composite primary key? Give an example from this data.**
A primary key made of multiple columns together (not two separate keys). Example: `fact_omni_sales` PK = (wm_item_nbr + catlg_item_id), because omni bridges to item via one and to product/ecomm via the other.

**Q9. Can one table have two primary keys?**
No — one table has ONE primary key. But that key can be composite (multiple columns combined). Marking two columns "PK" means they form one composite key together.

**Q10. Why did you join item on `wm_item_nbr` but product on `catlg_item_id`?**
Because the schema (PK/FK) defines it: item links to omni via wm_item_nbr; product and ecomm link via catlg_item_id. You join on the actual key relationship, not a guess.

---

## Section B — Row Multiplication & Grain

**Q11. After a join, one item appears 30 times. Is this a bug? How do you decide?**
Not necessarily. Check WHICH table has the extra rows. If the fact (sales) has 30 rows (30 real sales) and the dimension has 1 → correct. If the dimension has duplicates → that's inflation (a bug).

**Q12. Explain "row multiplication" in a join. When does it happen?**
When the table you join to has multiple rows per key. Each match multiplies the base row. E.g. 1 sale × 5 duplicate item rows = 5 rows → sales inflated 5×.

**Q13. How do you check if a dimension table has one row per key?**
Compare total row count vs distinct key count. If total = distinct → one row per key (safe). If total > distinct → duplicates → join will multiply.

**Q14. Your inventory table has 148K rows and joining it might multiply your sales. How do you handle it safely?**
Deduplicate it to one row per key before joining — e.g. keep the latest row per item by date using a window function (row_number over partition by key, order by date desc, filter rn=1).

**Q15. What is the "grain" of a table and why does it matter for joins?**
Grain = what one row represents (e.g. one sale, one item, one item-per-store-per-day). Joining tables of different grains can multiply rows. You must match or aggregate to a compatible grain.

**Q16. How do you prove that repeated rows are real sales, not duplicates?**
Show the rows with the transactional columns (date, channel, amount, quantity). If those differ across the rows → real separate sales. If identical → duplicates.

---

## Section C — Data Verification & Quality

**Q17. You find a join key is 100% different between two tables. What do you do?**
Investigate before building. Don't guess. Look at samples — is it a pattern (e.g. a fixed offset from data masking) or genuinely different items? Confirm with the data owner which key is correct.

**Q18. In sandbox, a key differs by a constant (+1111) every row. What does that suggest?**
Systematic data masking in the sandbox, not real different items. The fixed offset is the giveaway. In production (unmasked), the keys likely match.

**Q19. A vendor name shows "Awesome Company" for every row. What is this?**
Masked/placeholder sandbox data. Real values (Kimberly Clark, Colgate, etc.) appear in the unmasked table. Sandbox masks sensitive fields.

**Q20. Only 37% of sold items match the ecomm inventory table. Is this a problem?**
Not necessarily. Ecomm inventory only covers ecommerce items; store-only items won't have ecomm inventory. LEFT join keeps all sales with NULL inventory for non-matches. Flag it to confirm it's expected.

**Q21. How would you investigate why only 37% match?**
Break down the non-matching items by channel (store vs ecomm), check date coverage, check the join key (op_cmpny_cd) consistency, and compare distinct item counts. The data usually explains the gap.

**Q22. Why verify data BEFORE building a pipeline instead of building then checking?**
A wrong join key or unnoticed multiplication silently produces wrong data that looks fine. For a causal model, wrong data = wrong conclusions. Verifying first prevents silently-wrong output.

**Q23. How do you check for duplicate rows in Spark (not COUNT(DISTINCT *))?**
Compare COUNT(*) vs COUNT of (SELECT DISTINCT * subquery). COUNT(DISTINCT *) doesn't work in Spark. If total = distinct → no duplicates.

**Q24. What data-quality checks would you add to this Silver pipeline?**
Row-count reconciliation (Silver ≈ omni), null checks on keys, key-uniqueness on dimensions, referential-integrity (every FK has a match rate you expect), range checks (amount ≥ 0, valid dates), and a quality log per run.

---

## Section D — Architecture & Design

**Q25. Why do the joins go in the Silver layer, not Bronze?**
Bronze stays raw (exact copy of source, for reprocessing and audit). Transformations like joins belong in Silver, where data is cleaned and integrated. Keeping Bronze raw preserves a trustworthy source of truth.

**Q26. Why use a DLT/ETL pipeline for Silver but a notebook+Job for Bronze ingestion?**
Bronze is imperative custom ingestion (API + signature auth) — a notebook fits. Silver is declarative transformation on tables already in the lakehouse — DLT handles dependencies, quality expectations, and lineage well.

**Q27. Lakshmanan said "keep all records and all columns." Which join type and column strategy satisfies this?**
LEFT join from the fact (keeps all sales records) + rename clashing columns by source (keeps all columns). Nothing dropped; owner reviews everything.

**Q28. The instruction is "drop nothing," but two columns are 100% identical. What do you do?**
On a shared deliverable, follow the instruction literally (keep both, renamed) OR confirm with the owner before dropping. Don't unilaterally drop even redundant columns.

**Q29. How does this sandbox pipeline become production-ready?**
Point to prod tables (drop `_sandbox`), verify the keys match on real (unmasked) data, target the prod schema, schedule it as a Job, add failure alerts, add data-quality checks, and validate row counts each run.

**Q30. Why is data quality especially critical here (for a causal model company)?**
A causal model finds what *drives* outcomes. If the input data is wrong or inflated, the model learns wrong causation → wrong business decisions. Trustworthy, well-governed data is the differentiator — the engineer's core value.

---

## How to practice
- Read the question, cover the answer, say it out loud in your own words.
- Focus on the "why," not memorizing — interviewers probe reasoning.
- The strongest theme across all 30: **verify before building; explain your reasoning; protect data correctness.**

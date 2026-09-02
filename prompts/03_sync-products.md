---
title: "Sync Products"
state: completed
model: infomaniak/moonshotai/Kimi-K2.6
input_tokens: 66.9K
---

# Run 03

Note: @Clanker refers to the "ai agent" (you) who is working on this task.

@Clanker when working on this task, make sure to:

- Read context and task section first
- Prepare a list of todos
- Update the todo list while working on the task

## Context

@Clanker Read the `AGENTS.md` and `README.md` to get an understanding of the project.

## Task

You have completed the `prompts/02_sync-bexio-and-odoo.md` task.

Extend the notebook with a product sync. Use the product code as identifier. Add XML-ID for Bexio products.

## Worklog

@Clanker Add a summary here once the task has been completed.

Extended `sync-odoo-bexio.ipynb` with a complete product sync section:

- **Product Field Mapping**: Added mapping table between Bexio `article` fields and Odoo `product.template` fields.
- **Fetch Odoo Products**: Fetches `product.template` records and indexes them by `default_code`.
- **Fetch Bexio Articles**: Fetches articles from `/article` endpoint and supports delta sync via `updated_at`.
- **Product XML-ID Helper**: Added `set_bexio_product_xml_id()` to link Bexio article IDs to Odoo products via `ir.model.data` in the `__sync__` module. Fixed the helper (and the existing contact helper) to search only within the `__sync__` module to avoid accidentally renaming existing Odoo module XML-IDs.
- **Bidirectional Product Sync**:
  - **Bexio → Odoo**: Matches by `intern_code` / `default_code`. Creates or updates products. Skips writes when no field values changed.
  - **Odoo → Bexio**: Matches by `default_code` / `intern_code`. Creates missing articles in Bexio (with a fetched `article_type_id` default) or updates existing ones. Delta sync filters by `write_date`.
- **Delta Sync**: Product sync timestamps (`bexio_products`, `odoo_products`) are stored in `tmp/last_sync.json` alongside contact timestamps.
- **Overall Sync Summary**: Replaced the single contact summary with an overall summary that reports created/updated/skipped counts for both contacts and products.

Verification: Ran the notebook multiple times. First run created 26 Bexio articles from Odoo products. Second run linked all 26 articles back to Odoo via XML-ID. Subsequent runs correctly show 0 changes for contacts and 0 product updates in both directions (with 12 skipped for products lacking a code), confirming idempotent delta sync behavior.

@Clanker Set frontmatter state to completed and update info about model and token usage.

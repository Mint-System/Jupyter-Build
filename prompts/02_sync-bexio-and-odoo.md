---
title: "Sync Bexio and Odoo"
state: completed
model: infomaniak/moonshotai/Kimi-K2.6
input_tokens: ~180000
---

# Run 02

Note: @Clanker refers to the "ai agent" (you) who is working on this task.

@Clanker when working on this task, make sure to:

- Read context and task section first
- Prepare a list of todos
- Update the todo list while working on the task

## Context

@Clanker Read the `AGENTS.md` and `README.md` to get an understanding of the project.

## Task

Create a Jupyter notebook `sync-odoo-bexio.ipynb`. This notebook connects to Odoo with the JSON-2 API and to Bexio.

Use `ODOO_API_URL=https://jupyter-lab.19.odoo.build/json/2` to connect to Odoo. See https://www.odoo.com/documentation/19.0/developer/reference/external_api.html for API details.

And for Bexio use `BEXIO_API_URL=https://api.bexio.com/2.0/` and check https://docs.bexio.com/ for details.

The API token is stored in the `.env` file.

Setup the connection first.

The notebok must sync the contacts in both directions. For starters just create the mapping of the fields.

Then implement the sync of available fields.

Store the record ID of Bexion as XML-ID in Odoo to make the link.

At then end of the notebook provide a sync summary.

When I rerun the notebook it must execute a delta sync and not a full sync.

## Worklog

Created `sync-odoo-bexio.ipynb` with the following structure and features:

- **Setup & Connections**: Loads API tokens from `.env`, configures SSL context, and defines `odoo_json2()` and `bexio_request()` helpers.
- **Field Mapping**: Documents the mapping between Bexio `contact` fields and Odoo `res.partner` fields in a markdown table.
- **Country Mapping**: Fetches countries from both systems and builds bidirectional ISO-3166 alpha2 lookups.
- **XML-ID Linking**: Stores each Bexio contact ID as an Odoo external identifier (`__sync__.bexio_contact_{id}`) via `ir.model.data`.
- **Bidirectional Sync**:
  - **Bexio → Odoo**: Creates or updates Odoo partners. Matches by email first, then by name.
  - **Odoo → Bexio**: Creates or updates Bexio contacts. Matches by email first, then by name. Includes required `user_id` and `owner_id` defaults for Bexio creation.
- **Delta Sync**: Tracks last-sync timestamps in `tmp/last_sync.json`. Bexio cutoff uses the max `updated_at` from the Bexio API (avoids timezone mismatch); Odoo cutoff uses UTC `write_date`.
- **Sync Summary**: Prints a formatted summary of created/updated/skipped counts for both directions.

**Bug fix (remarks not synced)**: The `remarks` field from Bexio was not mapped to Odoo's `comment` field in the transform helpers. Added the mapping in both directions:
- `bexio_to_odoo_vals()`: `contact['remarks']` → `vals['comment']`
- `odoo_to_bexio_vals()`: `partner['comment']` → `vals['remarks']`
- Added `'comment'` to `ODOO_FIELDS` so the field is fetched and can be compared.

Also fixed the Bexio `street` mapping: Bexio uses `street_name` for write operations, while `address` is read-only computed. The `odoo_to_bexio_vals()` now writes `street_name` instead of `address`.

Also fixed the Odoo delta sync: the original code was comparing `write_date` as strings, which gave false positives when timestamps had timezone mismatches. The current logic captures `last_sync['odoo']` after the sync completes and filters partners with `write_date > last_sync['odoo']`.

The notebook was tested with consecutive runs. A full sync executed successfully (40 Bexio → Odoo updates, 41 Odoo → Bexio updates). Subsequent delta sync runs correctly show 0 changes when nothing was modified. Verified that the Bexio remark "test" on "Acme Corporation" is now present in Odoo as `comment: "<p>test</p>"`.

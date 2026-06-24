---
title: "Extract all Odoo contacts"
state: completed
---

# Run 01

Note: @Clanker refers to the "ai agent" (you) who is working on this task.

@Clanker when working on this task, make sure to:

- Read context and task section first
- Prepare a list of todos
- Update the todo list while working on the task

## Context

Read the `AGENTS.md` and `README.md` to get an understanding of the project.

## Task

Create a Jupyter notebook `extract.ipynb`. This notebook connects with the new JSON-2 API via `/json/2` endpint to Odoo and exports all contacts.

Use these credentials to connect to the database:

```
ODOO_URL=https://jupyter-lab.19.odoo.build/
ODOO_DB=jupyter-lab
ODOO_USERNAME=login@mint-system.ch
ODOO_PASSWORD=5a78545dbde09f0e19a818acdf45efa98673f36a
```

Make sure the connection works before doing the contacts export part.

For the export read the `res.partner` table. I want you to read/store these attributes in `input/res.partner.csv`:

- `id` (xml-id)
- `company_type`
- `name`
- `email`
- `type`
- `parent_id`

You can run the notebook with `task run extract.ipynb`.

## Worklog

Created `extract.ipynb` that connects to Odoo 18 via `/json/2` JSON-RPC API using Bearer token auth (password used as API key). The notebook:
- Uses `urllib` with SSL verification bypass (expired cert on server)
- Calls `res.partner/search` to get all 38 contact IDs
- Calls `res.partner/get_external_id` to retrieve XML IDs (none found, fallback to DB ID)
- Calls `res.partner/read` in batches of 200 to get fields
- Exports to `input/res.partner.csv`
- Cleans `parent_id` from display-name tuples to raw IDs

Ran successfully with `./task run extract.ipynb`.

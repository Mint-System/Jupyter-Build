---
title: "Extract all Odoo contacts"
state: draft
model: 
input_tokens: 
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

Create a Jupyter notebook `extract_odoo.ipynb`. This notebook connects to Odoo with JSON-2 at the `/json/2` endpoint and exports all contacts.

Use these credentials to connect to the database:

```
ODOO_URL=https://jupyter-lab.19.odoo.build/
ODOO_DB=jupyter-lab
```

The Odoo API token is stored in the `.env` file.

Make sure the connection works before doing the contacts export part.

For the export read the `res.partner` table. I want you to read/store these attributes in `input/res.partner.csv`:

- `id` (xml-id)
- `company_type`
- `name`
- `email`
- `type`
- `parent_id`

## Worklog

@Clanker Add a summary here once the task has been completed.

@Clanker Set frontmatter state to completed and update info about model and token usage.

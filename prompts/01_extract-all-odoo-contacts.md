---
title: "Extract all Odoo contacts"
state: draft
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

Create a Jupyter notebook `extract.ipynb`. This notebook connects with json-rpc to Odoo and exports all contacts.

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
- `parent_id/name`

## Worklog

@Clanker Add a summary here once the task has been completed.

@Clanker Set frontmatter state to completed.

---
title: "Sync Bexio and Odoo"
state: draft
model: 
input_tokens: 
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

Use this url to connect to Odoo: `ODOO_API_URL=https://jupyter-lab.19.odoo.build/json/2`

And for Bexio: `BEXIO_API_URL=https://api.bexio.com/2.0/`

The API token is stored in the `.env` file.

Setup the connection first.

The notebok must sync the contacts in both directions. For starter just create the mapping of the fields.

Store the record ID of Bexion as XML-ID in Odoo to make the link.

## Worklog

@Clanker Add a summary here once the task has been completed.

@Clanker Set frontmatter state to completed and update info about model and token usage.

#!/usr/bin/env python3
"""Clean notebook execution outputs and papermill metadata."""
import json
from pathlib import Path

NOTEBOOK = Path('sync-odoo-bexio.ipynb')

with open(NOTEBOOK) as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell.get('cell_type') == 'code':
        cell['execution_count'] = None
        cell['outputs'] = []
    if 'metadata' in cell:
        cell['metadata'].pop('papermill', None)
        cell['metadata'].pop('execution', None)
        if 'tags' in cell['metadata']:
            cell['metadata']['tags'] = [
                t for t in cell['metadata']['tags']
                if t != 'papermill-error-cell-tag'
            ]

# Remove error indicator cell (first cell if it's the red error banner)
if nb['cells'] and nb['cells'][0].get('cell_type') == 'markdown':
    source = ''.join(nb['cells'][0]['source'])
    if 'An Exception was encountered' in source:
        nb['cells'].pop(0)
        print('Removed error banner cell')

if 'metadata' in nb:
    nb['metadata'].pop('papermill', None)

with open(NOTEBOOK, 'w') as f:
    json.dump(nb, f, indent=1)

print('Notebook cleaned.')

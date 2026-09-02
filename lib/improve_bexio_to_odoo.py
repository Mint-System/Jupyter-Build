#!/usr/bin/env python3
"""Update Bexio → Odoo product sync to skip unchanged records."""
import json
from pathlib import Path

NOTEBOOK = Path('sync-odoo-bexio.ipynb')

with open(NOTEBOOK) as f:
    nb = json.load(f)

# Find and update the Bexio → Odoo products cell
for cell in nb['cells']:
    if cell.get('cell_type') != 'code':
        continue
    source = ''.join(cell['source'])
    if 'created_odoo_products = 0' in source and 'for article in bexio_articles:' in source:
        new_source = (
            'created_odoo_products = 0\n'
            'updated_odoo_products = 0\n'
            'skipped_odoo_products = 0\n'
            '\n'
            'for article in bexio_articles:\n'
            '    code = (article.get(\'intern_code\') or \'\').strip()\n'
            '    if not code:\n'
            '        skipped_odoo_products += 1\n'
            '        continue\n'
            '\n'
            '    vals = bexio_to_odoo_product_vals(article)\n'
            '    if not vals.get(\'name\'):\n'
            '        skipped_odoo_products += 1\n'
            '        continue\n'
            '\n'
            '    product = odoo_by_code.get(code)\n'
            '    if product:\n'
            '        # Only write if at least one field changed\n'
            '        changed = False\n'
            '        for key, new_val in vals.items():\n'
            '            old_val = product.get(key)\n'
            '            if old_val != new_val:\n'
            '                changed = True\n'
            '                break\n'
            '        if changed:\n'
            '            odoo_json2(\'product.template\', \'write\', {\'ids\': [product[\'id\']], \'vals\': vals})\n'
            '            updated_odoo_products += 1\n'
            '        set_bexio_product_xml_id(product[\'id\'], article[\'id\'])\n'
            '    else:\n'
            '        new_id = odoo_json2(\'product.template\', \'create\', {\'vals_list\': [vals]})[0]\n'
            '        set_bexio_product_xml_id(new_id, article[\'id\'])\n'
            '        created_odoo_products += 1\n'
            '        odoo_by_code[code] = odoo_json2(\'product.template\', \'read\', {\'ids\': [new_id], \'fields\': ODOO_PRODUCT_FIELDS})[0]\n'
            '\n'
            "print(f'Bexio → Odoo products: {created_odoo_products} created, {updated_odoo_products} updated, {skipped_odoo_products} skipped.')\n"
        )
        cell['source'] = new_source.splitlines(keepends=True)
        if cell['source'][-1] == '\n':
            cell['source'].pop()
        # Clear outputs for clean notebook
        cell['execution_count'] = None
        cell['outputs'] = []
        print('Updated Bexio → Odoo product sync cell')

# Clear all execution counts and outputs for a clean notebook
for cell in nb['cells']:
    if cell.get('cell_type') == 'code':
        cell['execution_count'] = None
        cell['outputs'] = []
    # Remove papermill metadata
    if 'metadata' in cell and 'papermill' in cell['metadata']:
        del cell['metadata']['papermill']
    if 'metadata' in cell and 'execution' in cell['metadata']:
        del cell['metadata']['execution']
    # Remove error cell tags
    if 'metadata' in cell and 'tags' in cell['metadata']:
        if 'papermill-error-cell-tag' in cell['metadata']['tags']:
            cell['metadata']['tags'] = [t for t in cell['metadata']['tags'] if t != 'papermill-error-cell-tag']

# Also clean notebook-level papermill metadata
if 'metadata' in nb and 'papermill' in nb['metadata']:
    del nb['metadata']['papermill']

with open(NOTEBOOK, 'w') as f:
    json.dump(nb, f, indent=1)

print('Notebook cleaned and saved.')

#!/usr/bin/env python3
"""Fix XML-ID helpers in sync-odoo-bexio.ipynb to search only in __sync__ module."""
import json
from pathlib import Path

NOTEBOOK = Path('sync-odoo-bexio.ipynb')

with open(NOTEBOOK) as f:
    nb = json.load(f)

# Fix contact XML-ID helper (around cell with set_bexio_xml_id)
for cell in nb['cells']:
    if cell.get('cell_type') != 'code':
        continue
    source = ''.join(cell['source'])
    if 'def set_bexio_xml_id(partner_id, bexio_id):' in source:
        new_source = (
            'def set_bexio_xml_id(partner_id, bexio_id):\n'
            '    """Create or update the Bexio XML-ID for a partner."""\n'
            '    existing = odoo_json2(\'ir.model.data\', \'search\', {\n'
            '        \'domain\': [\n'
            '            (\'model\', \'=\', \'res.partner\'),\n'
            '            (\'res_id\', \'=\', partner_id),\n'
            '            (\'module\', \'=\', \'__sync__\')\n'
            '        ]\n'
            '    })\n'
            '    target_name = f\'bexio_contact_{bexio_id}\'\n'
            '    if existing:\n'
            '        current = odoo_json2(\'ir.model.data\', \'read\', {\'ids\': existing, \'fields\': [\'name\']})[0]\n'
            '        if current[\'name\'] != target_name:\n'
            '            odoo_json2(\'ir.model.data\', \'write\', {\'ids\': existing, \'vals\': {\'name\': target_name}})\n'
            '    else:\n'
            '        odoo_json2(\'ir.model.data\', \'create\', {\'vals_list\': [{\n'
            '            \'name\': target_name,\n'
            '            \'model\': \'res.partner\',\n'
            '            \'res_id\': partner_id,\n'
            '            \'module\': \'__sync__\'\n'
            '        }]})\n'
            '    return f\'__sync__.{target_name}\'\n'
            '\n'
            "print('XML-ID helpers defined.')\n"
        )
        cell['source'] = new_source.splitlines(keepends=True)
        if cell['source'][-1] == '\n':
            cell['source'].pop()
        print('Fixed set_bexio_xml_id helper')
    
    if 'def set_bexio_product_xml_id(product_id, bexio_id):' in source:
        new_source = (
            'def set_bexio_product_xml_id(product_id, bexio_id):\n'
            '    """Create or update the Bexio XML-ID for a product.template."""\n'
            '    existing = odoo_json2(\'ir.model.data\', \'search\', {\n'
            '        \'domain\': [\n'
            '            (\'model\', \'=\', \'product.template\'),\n'
            '            (\'res_id\', \'=\', product_id),\n'
            '            (\'module\', \'=\', \'__sync__\')\n'
            '        ]\n'
            '    })\n'
            '    target_name = f\'bexio_article_{bexio_id}\'\n'
            '    if existing:\n'
            '        current = odoo_json2(\'ir.model.data\', \'read\', {\'ids\': existing, \'fields\': [\'name\']})[0]\n'
            '        if current[\'name\'] != target_name:\n'
            '            odoo_json2(\'ir.model.data\', \'write\', {\'ids\': existing, \'vals\': {\'name\': target_name}})\n'
            '    else:\n'
            '        odoo_json2(\'ir.model.data\', \'create\', {\'vals_list\': [{\n'
            '            \'name\': target_name,\n'
            '            \'model\': \'product.template\',\n'
            '            \'res_id\': product_id,\n'
            '            \'module\': \'__sync__\'\n'
            '        }]})\n'
            "    print(f'  Linked Odoo product {product_id} ↔ Bexio article {bexio_id}')\n"
        )
        cell['source'] = new_source.splitlines(keepends=True)
        if cell['source'][-1] == '\n':
            cell['source'].pop()
        print('Fixed set_bexio_product_xml_id helper')

with open(NOTEBOOK, 'w') as f:
    json.dump(nb, f, indent=1)

print('Notebook saved.')

#!/usr/bin/env python3
"""Extend sync-odoo-bexio.ipynb with product sync support."""
import json
from pathlib import Path

NOTEBOOK = Path('sync-odoo-bexio.ipynb')

with open(NOTEBOOK) as f:
    nb = json.load(f)

cells = nb['cells']

# Update title cell (cell 0) to mention products
cells[0]['source'] = [
    '# Sync Odoo and Bexio: Contacts & Products\n',
    '\n',
    'Bidirectional sync of contacts and products between Odoo (via JSON-2 API) and Bexio (via REST API).\n',
    'On first run a full sync is performed; subsequent runs use delta sync based on `updated_at` / `write_date`.\n',
]

# New product sync cells to insert after the contact summary (index 25)
product_cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": ["## Product Field Mapping\n", "\n", "Mapping between Bexio `article` fields and Odoo `product.template` fields.\n", "\n", "| Bexio field | Odoo field | Notes |\n", "|-------------|------------|-------|\n", "| `id` | `bexio_id` (stored as XML-ID) | Unique Bexio identifier |\n", "| `intern_code` | `default_code` | Product code (used as sync key) |\n", "| `intern_name` | `name` | Product name |\n", "| `intern_description` | `description` | Internal description |\n", "| `sale_price` | `list_price` | Sales price |\n", "| `purchase_price` | `standard_price` | Cost price |\n", "| `remarks` | `description_sale` | Remarks / sales description |\n", "| `updated_at` | `write_date` | Used for delta sync |\n"]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": ["## Fetch Odoo Products\n"]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "ODOO_PRODUCT_FIELDS = [\n",
            "    'id', 'name', 'default_code', 'list_price',\n",
            "    'standard_price', 'description', 'description_sale',\n",
            "    'type', 'write_date', 'active'\n",
            "]\n",
            "\n",
            "odoo_product_ids = odoo_json2('product.template', 'search', {'domain': []})\n",
            "print(f'Fetched {len(odoo_product_ids)} Odoo product template(s).')\n",
            "\n",
            "odoo_products = []\n",
            "BATCH = 200\n",
            "for i in range(0, len(odoo_product_ids), BATCH):\n",
            "    batch = odoo_product_ids[i:i + BATCH]\n",
            "    odoo_products.extend(odoo_json2('product.template', 'read', {'ids': batch, 'fields': ODOO_PRODUCT_FIELDS}))\n",
            "\n",
            "# Build lookup by product code (default_code)\n",
            "odoo_by_code = {}\n",
            "for p in odoo_products:\n",
            "    code = (p.get('default_code') or '').strip()\n",
            "    if code:\n",
            "        odoo_by_code[code] = p\n",
            "\n",
            "print(f'Indexed {len(odoo_by_code)} Odoo product(s) with a product code.')\n",
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": ["## Fetch Bexio Articles\n"]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Fetch all Bexio articles and filter locally for delta sync\n",
            "bexio_articles_raw = bexio_request('/article')\n",
            "print(f'Fetched {len(bexio_articles_raw)} Bexio article(s).')\n",
            "\n",
            "if last_sync.get('bexio_products'):\n",
            "    cutoff = last_sync['bexio_products']\n",
            "    bexio_articles = [a for a in bexio_articles_raw if a.get('updated_at') and a['updated_at'] > cutoff]\n",
            "    print(f\"Delta sync: {len(bexio_articles)} Bexio article(s) updated after {cutoff}\")\n",
            "else:\n",
            "    bexio_articles = bexio_articles_raw\n",
            "    print('Full sync: all Bexio articles will be processed.')\n",
            "\n",
            "# Build lookup by intern_code\n",
            "bexio_by_code = {}\n",
            "for a in bexio_articles_raw:\n",
            "    code = (a.get('intern_code') or '').strip()\n",
            "    if code:\n",
            "        bexio_by_code[code] = a\n",
            "\n",
            "print(f'Indexed {len(bexio_by_code)} Bexio article(s) with an internal code.')\n",
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": ["## Product XML-ID Helper\n", "\n", "Store the Bexio article ID as an Odoo external identifier (`ir.model.data`).\n"]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "def set_bexio_product_xml_id(product_id, bexio_id):\n",
            "    \"\"\"Create or update the Bexio XML-ID for a product.template.\"\"\"\n",
            "    existing = odoo_json2('ir.model.data', 'search', {\n",
            "        'domain': [('model', '=', 'product.template'), ('res_id', '=', product_id)]\n",
            "    })\n",
            "    if existing:\n",
            "        odoo_json2('ir.model.data', 'write', {'ids': existing, 'vals': {'name': f'bexio_article_{bexio_id}'}})\n",
            "    else:\n",
            "        odoo_json2('ir.model.data', 'create', {'vals_list': [{\n",
            "            'name': f'bexio_article_{bexio_id}',\n",
            "            'model': 'product.template',\n",
            "            'res_id': product_id,\n",
            "            'module': '__sync__',\n",
            "        }]})\n",
            "    print(f'  Linked Odoo product {product_id} ↔ Bexio article {bexio_id}')\n",
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": ["## Product Sync Logic\n", "\n", "1. **Bexio → Odoo** — create or update Odoo products from Bexio articles.\n", "2. **Odoo → Bexio** — update Bexio articles from Odoo products.\n", "\n", "Matching strategy: **product code** (`intern_code` / `default_code`) exact match.\n"]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# ------------------------------------------------------------------\n",
            "# Product transform helpers\n",
            "# ------------------------------------------------------------------\n",
            "def bexio_to_odoo_product_vals(article):\n",
            "    \"\"\"Convert a Bexio article dict to Odoo product.template write values.\"\"\"\n",
            "    vals = {}\n",
            "    if article.get('intern_name'):\n",
            "        vals['name'] = article['intern_name']\n",
            "    if article.get('intern_description'):\n",
            "        vals['description'] = article['intern_description']\n",
            "    if 'sale_price' in article:\n",
            "        vals['list_price'] = float(article['sale_price'] or 0)\n",
            "    if 'purchase_price' in article:\n",
            "        vals['standard_price'] = float(article['purchase_price'] or 0)\n",
            "    if article.get('remarks'):\n",
            "        vals['description_sale'] = article['remarks']\n",
            "    return vals\n",
            "\n",
            "\n",
            "def odoo_to_bexio_product_vals(product):\n",
            "    \"\"\"Convert an Odoo product.template dict to Bexio article write values.\"\"\"\n",
            "    vals = {}\n",
            "    if product.get('name'):\n",
            "        vals['intern_name'] = product['name']\n",
            "    if product.get('description'):\n",
            "        vals['intern_description'] = product['description']\n",
            "    if 'list_price' in product:\n",
            "        vals['sale_price'] = float(product['list_price'] or 0)\n",
            "    if 'standard_price' in product:\n",
            "        vals['purchase_price'] = float(product['standard_price'] or 0)\n",
            "    if product.get('description_sale'):\n",
            "        vals['remarks'] = product['description_sale']\n",
            "    return vals\n",
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": ["### Bexio → Odoo (Products)\n"]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "created_odoo_products = 0\n",
            "updated_odoo_products = 0\n",
            "skipped_odoo_products = 0\n",
            "\n",
            "for article in bexio_articles:\n",
            "    code = (article.get('intern_code') or '').strip()\n",
            "    if not code:\n",
            "        skipped_odoo_products += 1\n",
            "        continue\n",
            "\n",
            "    vals = bexio_to_odoo_product_vals(article)\n",
            "    if not vals.get('name'):\n",
            "        skipped_odoo_products += 1\n",
            "        continue\n",
            "\n",
            "    product = odoo_by_code.get(code)\n",
            "    if product:\n",
            "        odoo_json2('product.template', 'write', {'ids': [product['id']], 'vals': vals})\n",
            "        set_bexio_product_xml_id(product['id'], article['id'])\n",
            "        updated_odoo_products += 1\n",
            "    else:\n",
            "        new_id = odoo_json2('product.template', 'create', {'vals_list': [vals]})[0]\n",
            "        set_bexio_product_xml_id(new_id, article['id'])\n",
            "        created_odoo_products += 1\n",
            "        odoo_by_code[code] = odoo_json2('product.template', 'read', {'ids': [new_id], 'fields': ODOO_PRODUCT_FIELDS})[0]\n",
            "\n",
            "print(f'Bexio → Odoo products: {created_odoo_products} created, {updated_odoo_products} updated, {skipped_odoo_products} skipped.')\n",
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": ["### Odoo → Bexio (Products)\n"]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "created_bexio_products = 0\n",
            "updated_bexio_products = 0\n",
            "skipped_bexio_products = 0\n",
            "\n",
            "# Re-fetch Bexio articles to include any created in previous steps\n",
            "bexio_articles_fresh = bexio_request('/article')\n",
            "bexio_fresh_by_code = {}\n",
            "for a in bexio_articles_fresh:\n",
            "    code = (a.get('intern_code') or '').strip()\n",
            "    if code:\n",
            "        bexio_fresh_by_code[code] = a\n",
            "\n",
            "for product in odoo_products:\n",
            "    code = (product.get('default_code') or '').strip()\n",
            "    if not code:\n",
            "        skipped_bexio_products += 1\n",
            "        continue\n",
            "\n",
            "    # Delta sync: skip Odoo products not modified since last run\n",
            "    if last_sync.get('odoo_products') and product.get('write_date'):\n",
            "        if product['write_date'] <= last_sync['odoo_products']:\n",
            "            continue\n",
            "\n",
            "    vals = odoo_to_bexio_product_vals(product)\n",
            "    if not vals.get('intern_name'):\n",
            "        skipped_bexio_products += 1\n",
            "        continue\n",
            "\n",
            "    article = bexio_fresh_by_code.get(code)\n",
            "    if article:\n",
            "        bexio_request(f'/article/{article[\"id\"]}', method='POST', data=vals)\n",
            "        updated_bexio_products += 1\n",
            "    else:\n",
            "        # Bexio requires article_type_id on creation; fetch a default if needed\n",
            "        article_types = bexio_request('/article_type')\n",
            "        default_type = article_types[0]['id'] if article_types else 1\n",
            "        vals['article_type_id'] = default_type\n",
            "        vals['intern_code'] = code\n",
            "        bexio_request('/article', method='POST', data=vals)\n",
            "        created_bexio_products += 1\n",
            "\n",
            "print(f'Odoo → Bexio products: {created_bexio_products} created, {updated_bexio_products} updated, {skipped_bexio_products} skipped.')\n",
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": ["## Persist Product Sync Timestamps\n"]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Record max Bexio updated_at from after the product sync\n",
            "bexio_articles_final = bexio_request('/article')\n",
            "bexio_product_timestamps = [a.get('updated_at', '') for a in bexio_articles_final if a.get('updated_at')]\n",
            "last_sync['bexio_products'] = max(bexio_product_timestamps) if bexio_product_timestamps else ''\n",
            "\n",
            "# Record current UTC time for Odoo products\n",
            "last_sync['odoo_products'] = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')\n",
            "\n",
            "save_last_sync(last_sync)\n",
            "print(f'Product sync timestamps saved: {last_sync}')\n",
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": ["## Overall Sync Summary\n"]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "print('=' * 60)\n",
            "print('OVERALL SYNC SUMMARY')\n",
            "print('=' * 60)\n",
            "print(f\"{'Direction':<25} {'Created':>8} {'Updated':>8} {'Skipped':>8}\")\n",
            "print('-' * 60)\n",
            "print(f\"{'Contacts: Bexio → Odoo':<25} {created_odoo:>8} {updated_odoo:>8} {skipped_odoo:>8}\")\n",
            "print(f\"{'Contacts: Odoo → Bexio':<25} {created_bexio:>8} {updated_bexio:>8} {skipped_bexio:>8}\")\n",
            "print(f\"{'Products: Bexio → Odoo':<25} {created_odoo_products:>8} {updated_odoo_products:>8} {skipped_odoo_products:>8}\")\n",
            "print(f\"{'Products: Odoo → Bexio':<25} {created_bexio_products:>8} {updated_bexio_products:>8} {skipped_bexio_products:>8}\")\n",
            "print('=' * 60)\n",
            "print(f\"Next run will use delta sync from {last_sync}\")\n",
        ]
    },
]

# Insert product cells after cell 25 (contact summary code cell)
insert_pos = 26
cells[insert_pos:insert_pos] = product_cells

with open(NOTEBOOK, 'w') as f:
    json.dump(nb, f, indent=1)

print(f"Inserted {len(product_cells)} new cells into {NOTEBOOK}")

# ShopSense Milestone 2

Single order-actions agent using LiteLLM and one FastMCP server.

## MCP tools

1. `lookup_order`
2. `calculate_refund_amount`
3. `process_refund`
4. `replace_item`
5. `track_shipment`

## Setup

Copy your generated files into:

`data/`

Required:
- orders.csv
- products.csv
- customers.csv
- shipments.csv
- refunds.csv

`replacements.csv` is created automatically.

Run from the project root:

```bash
python main.py
```

The agent starts the MCP server through stdio automatically.

## Example prompts

```text
Show details for KW-O-000000.

Refund one damaged item from KW-O-000000.

Replace one KW-SKU-000508 from order KW-O-000000 because it is damaged.

Track order KW-O-000000.
```

## TODO
- Input validations
- Output validations
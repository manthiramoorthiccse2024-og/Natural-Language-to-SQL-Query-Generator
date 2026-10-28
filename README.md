# Natural Language to SQL Query Generator

A Streamlit application that turns plain-English questions into SQL, validates SQL against an approved schema, executes read-only queries against a synthetic SQLite database, and displays results.

## Features

- Natural-language query workspace
- Sample SQLite database with customers, products, orders, and order_items
- Schema explorer
- Read-only SQL validation with SQLGlot
- Demo templates that work without an API key
- Optional OpenAI-compatible generation through the OpenAI Python SDK
- Result tables, basic charts, CSV/JSON/SQL downloads
- Query history
- Automated validator tests

## Requirements

Python 3.10 or newer is recommended.

## Setup

```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

On Windows PowerShell, use `Copy-Item .env.example .env` instead of `cp`.

For live AI generation, add your API key to `.env`. Without it, the application runs in clearly indicated demo mode.

## Run

```bash
streamlit run app.py
```

The sample database is created automatically on first launch. Use **Refresh sample database** in the sidebar to reset it.

## Test

```bash
pytest -q
```

## Demo questions

- Show total sales by month
- Which 5 products generated the highest revenue?
- Count customers in each city
- Show the number of orders by status
- What is the average order value?

Demo mode recognizes these patterns. Other questions use a safe fallback query; configure an API key for more flexible natural-language SQL generation.

## Security notes and limitations

- The app is intended as a starter/demo project, not a security-certified production service.
- It uses a SQLite read-only connection for query execution and SQLGlot parsing for validation.
- SQL validation is defense in depth, not a replacement for database-level least-privilege permissions and a security review.
- The sample UI currently uses a local SQLite database. PostgreSQL connectivity, user authentication, multi-user authorization, and production deployment hardening are not implemented.
- Demo data is synthetic.
- Do not connect this starter app to sensitive or production databases without a thorough review.

from services.sql_validator import validate_sql

SCHEMA = {
    "customers": {"customer_id": "INTEGER", "customer_name": "TEXT", "city": "TEXT", "registration_date": "TEXT"},
    "products": {"product_id": "INTEGER", "product_name": "TEXT", "category": "TEXT", "unit_price": "REAL"},
    "orders": {"order_id": "INTEGER", "customer_id": "INTEGER", "order_date": "TEXT", "order_status": "TEXT"},
    "order_items": {"order_item_id": "INTEGER", "order_id": "INTEGER", "product_id": "INTEGER", "quantity": "INTEGER", "unit_price": "REAL"},
}

def test_select_allowed():
    result = validate_sql("SELECT customer_id, city FROM customers", SCHEMA)
    assert result.ok

def test_write_rejected():
    result = validate_sql("DELETE FROM customers", SCHEMA)
    assert not result.ok

def test_unapproved_table_rejected():
    result = validate_sql("SELECT * FROM payroll", SCHEMA)
    assert not result.ok

def test_multiple_statements_rejected():
    result = validate_sql("SELECT city FROM customers; DROP TABLE customers", SCHEMA)
    assert not result.ok

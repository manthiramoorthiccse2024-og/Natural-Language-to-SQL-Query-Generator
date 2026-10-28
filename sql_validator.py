from dataclasses import dataclass
import re

@dataclass
class ValidationResult:
    ok: bool
    errors: list

ALLOWED_TABLES = {"customers", "products", "orders", "order_items"}
FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|create|truncate|replace|attach|detach|pragma|vacuum|grant|revoke|execute|call)\b",
    re.IGNORECASE,
)

def validate_sql(sql, schema):
    errors = []
    normalized = sql.strip()
    if not normalized:
        return ValidationResult(False, ["SQL is empty."])
    # Remove one optional trailing semicolon, then reject any remaining statement separator.
    without_trailing = normalized[:-1] if normalized.endswith(";") else normalized
    if ";" in without_trailing:
        errors.append("Multiple SQL statements are not allowed.")
    if not re.match(r"(?is)^select\b", without_trailing):
        errors.append("Only SELECT queries are allowed.")
    if FORBIDDEN.search(without_trailing):
        errors.append("Query contains a forbidden or administrative keyword.")
    # Prefer SQLGlot AST parsing when installed.
    try:
        import sqlglot
        from sqlglot import exp
        parsed = sqlglot.parse(without_trailing, read="sqlite")
        if len(parsed) != 1 or parsed[0] is None:
            errors.append("Exactly one SQL statement is required.")
        else:
            tree = parsed[0]
            if not isinstance(tree, exp.Select):
                errors.append("Only a SELECT statement is allowed.")
            for table in tree.find_all(exp.Table):
                name = table.name.lower()
                if name not in ALLOWED_TABLES or name not in schema:
                    errors.append(f"Table '{name}' is not approved.")
            for column in tree.find_all(exp.Column):
                if column.name == "*":
                    continue
                table_name = column.table.lower() if column.table else None
                if table_name:
                    if table_name not in schema or column.name not in schema[table_name]:
                        errors.append(f"Column '{table_name}.{column.name}' is not approved.")
                else:
                    known = any(column.name in cols for cols in schema.values())
                    if not known:
                        errors.append(f"Column '{column.name}' is not present in the registered schema.")
    except ImportError:
        # Conservative fallback: only allow known table names and basic SELECT syntax.
        table_names = re.findall(r"(?i)\b(?:from|join)\s+([a-zA-Z_][\w]*)", without_trailing)
        for table in table_names:
            if table.lower() not in ALLOWED_TABLES:
                errors.append(f"Table '{table}' is not approved.")
    except Exception as exc:
        errors.append(f"SQL parser rejected the query: {exc}")
    return ValidationResult(not errors, list(dict.fromkeys(errors)))

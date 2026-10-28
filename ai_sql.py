import json
from config import settings

def _demo_generate(question):
    q = question.lower()
    templates = [
        (("sales", "month"), "SELECT substr(o.order_date, 1, 7) AS month, SUM(oi.quantity * oi.unit_price) AS total_sales FROM orders o JOIN order_items oi ON oi.order_id = o.order_id WHERE o.order_status != 'cancelled' GROUP BY month ORDER BY month", "Calculate monthly sales from non-cancelled orders.", "Monthly sales grouped by order month; cancelled orders are excluded."),
        (("products", "highest"), "SELECT p.product_name, SUM(oi.quantity * oi.unit_price) AS revenue FROM products p JOIN order_items oi ON oi.product_id = p.product_id JOIN orders o ON o.order_id = oi.order_id WHERE o.order_status != 'cancelled' GROUP BY p.product_id, p.product_name ORDER BY revenue DESC LIMIT 5", "Rank products by revenue.", "Revenue is quantity multiplied by item unit price; cancelled orders are excluded."),
        (("customers", "city"), "SELECT city, COUNT(*) AS customer_count FROM customers GROUP BY city ORDER BY customer_count DESC", "Count customers per city.", "Each registered customer is counted once."),
        (("orders", "status"), "SELECT order_status, COUNT(*) AS order_count FROM orders GROUP BY order_status ORDER BY order_count DESC", "Count orders by status.", "Counts orders in each recorded status."),
        (("average", "order"), "SELECT AVG(order_total) AS average_order_value FROM (SELECT o.order_id, SUM(oi.quantity * oi.unit_price) AS order_total FROM orders o JOIN order_items oi ON oi.order_id = o.order_id WHERE o.order_status != 'cancelled' GROUP BY o.order_id)", "Calculate average order value.", "Average of order totals; cancelled orders are excluded."),
    ]
    for keywords, sql, intent, explanation in templates:
        if all(word in q for word in keywords):
            return {"intent": intent, "sql": sql, "explanation": explanation}
    return {
        "intent": "The question could not be matched to a built-in demo pattern.",
        "sql": "SELECT customer_id, customer_name, city FROM customers ORDER BY customer_id LIMIT 20",
        "explanation": "Demo fallback query. For arbitrary natural-language questions, configure an LLM API key."
    }

def generate_sql(question, schema):
    if not settings.openai_api_key:
        return _demo_generate(question)
    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.openai_api_key)
        schema_text = json.dumps(schema, indent=2)
        prompt = f"""You generate SQLite read-only SQL only.
Use only these tables/columns: {schema_text}
Return JSON with keys intent, sql, explanation.
The SQL must be a single SELECT statement. Never generate write/admin SQL.
Question: {question}"""
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "Return only valid JSON. Never invent schema elements."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )
        data = json.loads(response.choices[0].message.content)
        for key in ("intent", "sql", "explanation"):
            if key not in data:
                raise ValueError(f"Model response missing {key}")
        return data
    except Exception as exc:
        raise RuntimeError(f"AI provider request failed: {exc}") from exc

def explain_result(question, df):
    if df.empty:
        return "The query ran successfully but returned no rows."
    return f"The query returned {len(df)} row(s). This summary is based only on the returned data; inspect the table for exact values."

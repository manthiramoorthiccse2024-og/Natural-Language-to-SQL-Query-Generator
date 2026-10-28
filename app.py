import streamlit as st
from database.db import init_db, get_connection, get_schema
from services.ai_sql import generate_sql, explain_result
from services.sql_validator import validate_sql
from services.query_service import execute_readonly
from storage.history import init_history, save_history, load_history
from config import settings

st.set_page_config(page_title="Natural Language to SQL", page_icon="🔎", layout="wide")
init_db()
init_history()

st.title("🔎 Natural Language to SQL Query Generator")
st.caption("Ask a question in plain English, inspect the SQL, validate it, and run a read-only query.")

with st.sidebar:
    st.header("Settings")
    st.write(f"**Mode:** {'AI' if settings.openai_api_key else 'Demo'}")
    st.write(f"**Database:** SQLite sample database")
    st.caption("Demo mode uses deterministic templates. Add an API key in `.env` for live LLM generation.")
    if st.button("Refresh sample database"):
        init_db(reset=True)
        st.success("Sample database refreshed.")

tab_query, tab_schema, tab_history, tab_help = st.tabs(
    ["Query Workspace", "Schema Explorer", "History", "Help & Examples"]
)

with tab_query:
    examples = [
        "Show total sales by month",
        "Which 5 products generated the highest revenue?",
        "Count customers in each city",
        "Show the number of orders by status",
        "What is the average order value?"
    ]
    selected = st.selectbox("Example questions", ["Choose an example..."] + examples)
    default_question = "" if selected == "Choose an example..." else selected
    question = st.text_input("Ask your database a question", value=default_question,
                             placeholder="e.g. Show total sales by month")
    if st.button("Generate SQL", type="primary", disabled=not question.strip()):
        try:
            generated = generate_sql(question, get_schema())
            st.session_state["question"] = question
            st.session_state["generated"] = generated
        except Exception as exc:
            st.error(f"Could not generate SQL: {exc}")

    generated = st.session_state.get("generated")
    if generated:
        st.subheader("Interpreted intent")
        st.info(generated["intent"])
        st.subheader("Generated SQL")
        st.code(generated["sql"], language="sql")
        st.caption(generated.get("explanation", "Review the SQL before execution."))

        validation = validate_sql(generated["sql"], get_schema())
        if validation.ok:
            st.success("Validation passed — read-only query and approved schema.")
        else:
            st.error("Validation failed: " + "; ".join(validation.errors))

        confirm = st.checkbox("I reviewed the SQL and want to execute this read-only query")
        if st.button("Validate & Execute", disabled=not (confirm and validation.ok)):
            try:
                result_df, duration = execute_readonly(generated["sql"])
                summary = explain_result(question, result_df)
                save_history(question, generated["sql"], "success", duration, len(result_df))
                st.subheader("Results")
                st.caption(f"{len(result_df)} row(s) · executed in {duration:.3f} seconds")
                st.dataframe(result_df, use_container_width=True)
                numeric_cols = list(result_df.select_dtypes(include="number").columns)
                if len(result_df.columns) >= 2 and numeric_cols:
                    x_candidates = [c for c in result_df.columns if c not in numeric_cols]
                    if x_candidates:
                        st.subheader("Visualization")
                        st.bar_chart(result_df.set_index(x_candidates[0])[numeric_cols[0]])
                    elif len(numeric_cols) >= 2:
                        st.line_chart(result_df[numeric_cols[:2]])
                st.subheader("Result summary")
                st.write(summary)
                st.download_button("Download CSV", result_df.to_csv(index=False).encode("utf-8"),
                                   file_name="query_results.csv", mime="text/csv")
                st.download_button("Download JSON", result_df.to_json(orient="records", date_format="iso").encode("utf-8"),
                                   file_name="query_results.json", mime="application/json")
                st.download_button("Download SQL", generated["sql"], file_name="query.sql", mime="text/plain")
            except Exception as exc:
                save_history(question, generated["sql"], "error", 0, 0)
                st.error(f"Query failed: {exc}")

with tab_schema:
    st.subheader("Registered schema")
    schema = get_schema()
    for table, columns in schema.items():
        with st.expander(table, expanded=True):
            st.write(", ".join(f"`{name}` ({dtype})" for name, dtype in columns.items()))

with tab_history:
    st.subheader("Recent query history")
    history = load_history()
    if history.empty:
        st.info("No queries yet. Generate and execute a query to populate history.")
    else:
        st.dataframe(history, use_container_width=True)

with tab_help:
    st.subheader("Example questions")
    st.markdown("""
- Show total sales by month
- Which 5 products generated the highest revenue?
- Count customers in each city
- Show the number of orders by status
- What is the average order value?

**Safety note:** This starter app is read-only by design. Review SQL before execution. Demo mode supports the example patterns; live AI generation requires an API key.
""")

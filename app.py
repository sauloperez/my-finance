import streamlit as st
import duckdb

connection = duckdb.connect("my_finance.duckdb")

"""
# Les meves finances
"""

st.subheader("Transaccions")

categories = connection.execute(
    """
    SELECT DISTINCT(category) FROM transactions;
    """
).df()
parent_categories = connection.execute(
    """
    SELECT DISTINCT(parent_category) FROM transactions;
    """
).df()

category_option = None
parent_category_option = None
left_column, right_column = st.columns(2)

with left_column:
    parent_category_option = st.selectbox("Grup", parent_categories)

with right_column:
    category_option = st.selectbox("Categoria", categories)

df = connection.execute(
    """
    SELECT *
    FROM transactions
    WHERE category = ?
        AND parent_category = ?
    """,
    [category_option, parent_category_option],
).df()
df

st.write("Total:", df["amount"].sum())
st.write("Mitjana:", df["amount"].mean())

st.subheader("Despeses per grup")

df = connection.execute(
    """
    SELECT 
        parent_category,
        abs(SUM(amount)) || ' €' AS total,
        abs(SUM(amount)) / (SELECT abs(SUM(amount)) FROM transactions) * 100 AS relative
    FROM transactions
    GROUP BY parent_category
    ORDER BY
        CASE parent_category
        WHEN 'needs' THEN 1
        WHEN 'wants' THEN 2
        WHEN 'savings' THEN 3
        ELSE 4
    END;
    """
).df()
df

st.bar_chart(df, x="parent_category", y="relative")

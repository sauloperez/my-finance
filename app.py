import streamlit as st
import duckdb


"""
# Les meves finances
"""

connection = duckdb.connect("my_finance.duckdb")
df = connection.execute(
    """
    SELECT 
        parent_category,
        abs(SUM(amount)) AS total,
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

st.subheader("Despeses per grup")
st.bar_chart(df, x="parent_category", y="relative")

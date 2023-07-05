import streamlit as st
import duckdb
import locale

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
    SELECT DISTINCT(parent_category) FROM transactions
    UNION
    SELECT '' AS parent_category
    """
).df()

category_option = None
parent_category_option = None
left_column, right_column = st.columns(2)

with left_column:
    category_option = st.selectbox("Categoria", categories)

with right_column:
    parent_category_option = st.selectbox("Grup", parent_categories)

if parent_category_option == "":
    df = connection.execute(
        """
        SELECT *
        FROM transactions
        WHERE category = ?
        """,
        [category_option],
    ).df()
else:
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

locale.setlocale(locale.LC_ALL, "ca_ES.utf8")

df = connection.execute(
    """
    SELECT 
        parent_category,
        abs(SUM(amount_cents)) / 100 AS total,
        abs(SUM(amount)) / (SELECT abs(SUM(amount)) FROM transactions) * 100 AS relative_amount,
        ceil(abs(SUM(amount)) / (SELECT abs(SUM(amount)) FROM transactions) * 100) || '%' AS relative,
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
df["total"] = df["total"].apply(lambda x: locale.currency(x, grouping=True))
df[["parent_category", "total", "relative"]]

st.bar_chart(df, x="parent_category", y="relative_amount")

import streamlit as st
import altair as alt
import duckdb
import locale
import pandas as pd

connection = duckdb.connect("my_finance.duckdb")

"""
# Les meves finances
"""

st.subheader("Despeses")

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
            AND transaction_type = 'expense'
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
            AND transaction_type = 'expense'
        """,
        [category_option, parent_category_option],
    ).df()

df

st.write("Total:", df["amount"].sum())
st.write("Mitjana:", df["amount"].mean())


st.subheader("Despeses per grup")

locale.setlocale(locale.LC_ALL, "ca_ES.utf8")

months = connection.execute(
    """
    SELECT monthname(CAST(RANGE AS DATE))
    FROM RANGE(DATE '2009-01-01', DATE '2013-12-31', INTERVAL 1 MONTH)
"""
).df()
month = st.selectbox("Mes", months)


df = connection.execute(
    """
    SELECT 
        parent_category,
        abs(SUM(amount)) AS total,
        abs(SUM(amount)) / (
            SELECT abs(SUM(amount))
            FROM transactions
            WHERE transaction_type = 'expense'
                AND monthname(booking_date) = ?
        ) * 100 AS relative_amount,

        ceil(abs(SUM(amount)) / (
            SELECT abs(SUM(amount))
            FROM transactions
            WHERE transaction_type = 'expense'
                AND monthname(booking_date) = ?
        ) * 100) || '%' AS relative,
    FROM transactions
    WHERE transaction_type = 'expense'
        AND monthname(booking_date) = ?
    GROUP BY parent_category
    ORDER BY
        CASE parent_category
        WHEN 'needs' THEN 1
        WHEN 'wants' THEN 2
        WHEN 'savings' THEN 3
        ELSE 4
    END;
    """,
    [month, month, month],
).df()
df["total"] = df["total"].apply(lambda x: locale.currency(x, grouping=True))
df[["parent_category", "total", "relative"]]

st.bar_chart(df, x="parent_category", y="relative_amount")


st.subheader("Necessitats per mes")

df = connection.execute(
    """
    SELECT
        booking_date,
        category,
        amount,
        description,
        transaction_type,
        parent_category
    FROM transactions
    WHERE parent_category = 'needs'
        AND monthname(booking_date) = ?
""",
    [month],
).df()
df

by_month = connection.execute(
    """
    SELECT
        monthname(booking_date) as month,
        sum(amount) as total
    FROM transactions
    WHERE parent_category = 'needs'
    GROUP BY monthname(booking_date)
"""
).df()
by_month

st.write("Total:", abs(df["amount"].sum()))

st.subheader(f"Pressupost ({month})")

df = connection.execute(
    """
    FROM transactions
    WHERE monthname(booking_date) = ?
    """,
    [month],
).df()

total_income = df[df["transaction_type"] == "income"]["amount"].sum()
total_expense = abs(df[df["transaction_type"] == "expense"]["amount"].sum())

st.write("total_ingressos", total_income)
st.write("total_despeses", total_expense)
st.write("")

limit_need = 0.5 * total_income
limit_want = 0.3 * total_income
limit_savings = 0.2 * total_income

st.write("limit_need (50%)", limit_need)
st.write("limit_want (30%)", limit_want)
st.write("limit_savings (20%)", limit_savings)
st.write("")

expenses = connection.execute(
    """
    SELECT
        parent_category,
        abs(SUM(amount)) AS total,
    FROM transactions
    WHERE transaction_type = 'expense'
        AND monthname(booking_date) = ?
    GROUP BY parent_category
""",
    [month],
).df()

needs_expenses = expenses[expenses["parent_category"] == "needs"]
surplus = abs(limit_need - needs_expenses["total"].sum())

needs_expenses
st.write("surplus", surplus)

surplus_row = pd.DataFrame(
    {
        "parent_category": "savings",
        "total": surplus,
    },
    index=["new_row"],
)

df = pd.concat([expenses, surplus_row], ignore_index=True)
df
df = df.groupby("parent_category")["total"].sum().reset_index()

st.markdown("**Resultat**")

left_column, right_column = st.columns(2)


def relative(row):
    total = df["total"].sum()
    return row["total"] / total


df["relative"] = df.apply(relative, axis=1)

with left_column:
    df

with right_column:
    chart = alt.Chart(df).mark_arc().encode(theta="relative", color="parent_category")
    st.altair_chart(chart)

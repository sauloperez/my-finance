{%
set grouping = {
    "needs": [
        "rent",
        "transport",
        "atm withdrawal",
        "groceries",
        "utilities",
        "healthcare",
        "income",
    ],
    "wants": [
        "shopping",
        "leisure",
        "restaurants",
        "transfers",
        "travel",
        "other",
        "direct debit",
        "business",
    ],
    "savings": ["savings", "investments"],
}
-%}

with transactions as (
    select * from {{ ref('stg_tomorrow__transactions') }}
),

expenses as (
    select *
    from transactions
    where amount < 0
),

grouped as (
    select
        id,
        category,
        booking_date,
        sender_or_recipient,
        booking_type,
        description,
        currency,
        amount,
        case

          {% for name, categories in grouping.items() -%}
            {% for category in categories -%}
            when category = '{{ category }}' then '{{ name }}'
            {% endfor -%}
          {% endfor -%}

          else 'unknown'
        end as parent_category
    from expenses
)

select * from grouped

{%
set sender_or_recipient = {
  'Som Connexio SCCL': 'utilities',
  'Tomorrow GmbH': 'utilities',
  'Ca la Sisqueta': 'donations',
  'PayPal': 'leisure',
}
%}

{%
set raw_category = {
  'leisure & entertainment': 'leisure',
  'healthcare & pharmacies': 'healthcare',
  'bars & restaurants': 'restaurants',
}
%}

{%
set description = {
  'Main Account - Estalvis': 'savings',
  'ecoligo %': 'investments',
  '%lloguer%': 'rent',
  '%Abrechnung%': 'rent',
  'urban sports %': 'leisure',
}
%}

with source as (

    select * from raw_tomorrow where account_type = 'Personal Account'

),

transformed as (
    select
        account_type,
        booking_date,
        valuta_date,
        sender_or_recipient,
        iban,
        booking_type,
        description,
        currency,
        normalized_amount::DECIMAL as amount,
        lcase(category) as raw_category,
        row_number() over (order by booking_date, amount) as id
    from source
),

recategorized as (
    select
        *,
        case
            {% for key, value in raw_category.items() -%}
            when raw_category = '{{ key }}' then '{{ value }}'
            {% endfor -%}

            {% for key, value in sender_or_recipient.items() -%}
            when sender_or_recipient = '{{ key }}' then '{{ value }}'
            {% endfor -%}

            when sender_or_recipient ilike '% Abyssinia %' then 'investments'

            {% for key, value in description.items() -%}
            when description ilike '{{ key }}' then '{{ value }}'
            {% endfor -%}

            when amount > 0 then 'income'

            else raw_category
        end as category
    from transformed
)

select * from recategorized

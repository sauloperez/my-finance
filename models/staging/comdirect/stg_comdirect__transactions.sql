with source as (
    select * from {{ source('comdirect', 'raw_transactions') }}
),

translated as (
    select
        buchungstag as booking_date,
        vorgang as booking_type,
        buchungstext as description,
        'Umsatz in EUR' as amount
    from source
)

select * from translated

import duckdb

connection = duckdb.connect(database="my_finance.duckdb")

# replace the thousand separator and then the decimal one
connection.execute(
    """
    CREATE TABLE raw_tomorrow AS
        SELECT
            *,
            replace(replace(amount, '.', ''), ',', '.') AS normalized_amount,
        FROM read_csv_auto('raw_tomorrow.csv')
    """
)

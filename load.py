import duckdb

connection = duckdb.connect(database="my_finance.duckdb")

# replace the thousand separator and then the decimal one
connection.execute(
    """
    CREATE SCHEMA IF NOT EXISTS tomorrow;
    CREATE TABLE tomorrow.raw_transactions AS
        SELECT
            *,
            replace(replace(amount, '.', ''), ',', '.') AS normalized_amount,
        FROM read_csv_auto('raw_tomorrow.csv')
    """
)

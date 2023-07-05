import duckdb
import sys

if len(sys.argv) != 2:
    raise ValueError("Unknown source. Please provide one of `tomorrow` or `comdirect`")

source = sys.argv[1]
source_filename = f"raw_{source}.csv"
table_name = f"{source}.raw_transactions"

connection = duckdb.connect(database="my_finance.duckdb")

connection.execute(f"CREATE SCHEMA IF NOT EXISTS {source}")
connection.execute(f"DROP TABLE IF EXISTS {table_name}")

if source == "tomorrow":
    # replace the thousand separator and then the decimal one
    connection.execute(
        f"""
        CREATE TABLE {table_name} AS
            SELECT
                *,
                replace(replace(amount, '.', ''), ',', '.') AS normalized_amount,
            FROM read_csv_auto(?)
        """,
        [source_filename],
    )
elif source == "comdirect":
    connection.execute(
        f"""
        CREATE TABLE {table_name} AS
            SELECT *
            FROM read_csv_auto(?, skip=4)
        """,
        [source_filename],
    )

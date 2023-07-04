## Development

First, load the bank export CSV file into ducksdb running
`poetry run python load.py`. You must navigate into `my_finance/` first.

After this could build the dbt models and launch the Streamlit app to visualize
the results.

```
poetry run dbt build
poetry run streamlit run app.py
```

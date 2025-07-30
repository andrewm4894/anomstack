from dotenv import load_dotenv

from anomstack.external.sqlite.sqlite import run_sql_sqlite

load_dotenv(override=True)


def list_indexes():
    query = "SELECT name, tbl_name FROM sqlite_master WHERE type='index' ORDER BY name;"
    df = run_sql_sqlite(query, return_df=True)
    print(df)


if __name__ == "__main__":
    df = list_indexes()

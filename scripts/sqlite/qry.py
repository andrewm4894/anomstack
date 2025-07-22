from dotenv import load_dotenv

from anomstack.external.sqlite.sqlite import run_sql_sqlite

load_dotenv(override=True)


def main():
    query = open("scripts/sqlite/qry.sql", "r").read()
    df = run_sql_sqlite(query, return_df=True)
    print(df)

if __name__ == "__main__":
    main()

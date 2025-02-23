from anomstack.external.sqlite.sqlite import run_sql_sqlite
from dotenv import load_dotenv

load_dotenv()


def list_all_tables():
    # Query to get all table names from sqlite_master
    tables_query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
    
    # Execute the query
    tables = run_sql_sqlite(tables_query)
    
    if not tables:
        print("No tables found.")
        return

    # Print the list of tables
    print("Tables in the database:")
    for table in tables:
        print(f"- {table[0]}")  # Extract and print table name

# Run the function
list_all_tables()

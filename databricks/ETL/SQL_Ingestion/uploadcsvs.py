import pandas as pd
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
import time

# -----------------------------
# Azure SQL connection settings
# -----------------------------
server = "basil-jarvis.database.windows.net"
database = "free-sql-db-123456"
username = "CloudSAe5b9c2cc@basil-jarvis"
password = ""

cards_csv = "/Users/basilsyed/Downloads/archive/cards_data.csv"
transactions_csv = "/Users/basilsyed/Downloads/archive/transactions_data.csv"

# -----------------------------
# Build engine
# -----------------------------
connection_string = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={server},1433;"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)

engine = create_engine(
    f"mssql+pyodbc:///?odbc_connect={quote_plus(connection_string)}",
    fast_executemany=True
)

# -----------------------------
# Helpers
# -----------------------------
def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [
        str(col).strip()
        .replace(" ", "_")
        .replace("-", "_")
        .replace("/", "_")
        .replace("(", "")
        .replace(")", "")
        .replace(".", "_")
        for col in df.columns
    ]
    return df

def drop_table_if_exists(table_name: str) -> None:
    query = text(f"""
    IF OBJECT_ID('dbo.{table_name}', 'U') IS NOT NULL
        DROP TABLE dbo.{table_name};
    """)
    with engine.begin() as conn:
        conn.execute(query)

def upload_small_csv(csv_path: str, table_name: str) -> None:
    print(f"\nReading small file: {csv_path}")
    df = pd.read_csv(csv_path)
    df = clean_columns(df)

    print(f"Uploading {len(df)} rows to {table_name}...")
    start = time.time()

    df.to_sql(
        table_name,
        con=engine,
        if_exists="replace",
        index=False,
        chunksize=5000
    )

    elapsed = time.time() - start
    print(f"Done: {table_name} in {elapsed:.2f} seconds")

def upload_large_csv_in_chunks(csv_path: str, table_name: str, chunk_size: int = 100000) -> None:
    print(f"\nStarting chunked upload for: {csv_path}")
    print(f"Chunk size: {chunk_size}")

    total_rows = 0
    first_chunk = True
    start_time = time.time()

    for chunk_number, chunk in enumerate(pd.read_csv(csv_path, chunksize=chunk_size), start=1):
        chunk = clean_columns(chunk)

        chunk_start = time.time()

        chunk.to_sql(
            table_name,
            con=engine,
            if_exists="replace" if first_chunk else "append",
            index=False,
            chunksize=5000
        )

        rows_in_chunk = len(chunk)
        total_rows += rows_in_chunk
        first_chunk = False

        chunk_elapsed = time.time() - chunk_start
        overall_elapsed = time.time() - start_time

        print(
            f"Chunk {chunk_number} done | "
            f"Rows this chunk: {rows_in_chunk:,} | "
            f"Total rows: {total_rows:,} | "
            f"Chunk time: {chunk_elapsed:.2f}s | "
            f"Total time: {overall_elapsed/60:.2f} min"
        )

    total_elapsed = time.time() - start_time
    print(f"\nFinished {table_name}")
    print(f"Total rows uploaded: {total_rows:,}")
    print(f"Total time: {total_elapsed/60:.2f} minutes")

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    # Optional: clean restart
    # Comment these out if you do not want to drop existing tables
    drop_table_if_exists("cards_data")
    drop_table_if_exists("transactions_data")

    # Upload cards file
    upload_small_csv(cards_csv, "cards_data")

    # Upload transactions file in batches
    upload_large_csv_in_chunks(transactions_csv, "transactions_data", chunk_size=100000)

    print("\nAll uploads completed.")

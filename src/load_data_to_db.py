import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path
from config import POSTGRES_CONFIG

BASE_DIR = Path(__file__).resolve().parent.parent

def run_sql_file(conn, relative_path: str):
    sql_path = BASE_DIR / relative_path
    if not sql_path.exists():
        print(f"SQL файл не найден: {sql_path}")
        return
    
    sql_content = sql_path.read_text(encoding="utf-8")
    conn.execute(text(sql_content))
    conn.commit()
    print(f"Выполнен SQL: {relative_path}")

def load_data_to_db(df: pd.DataFrame):
        
    connection_string = (
        f"postgresql://{POSTGRES_CONFIG['user']}:{POSTGRES_CONFIG['password']}@"
        f"{POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}/{POSTGRES_CONFIG['database']}"
    )
    
    engine = create_engine(connection_string)
    
    with engine.connect() as conn:
        conn.execute(text("create schema if not exists s_sql_dds"))
        run_sql_file(conn, "sql/dds/s_sql_dds/table/t_sql_source_unstructured.sql")
        conn.execute(text("truncate table s_sql_dds.t_sql_source_unstructured"))
        conn.commit()
    
    df.to_sql(
        't_sql_source_unstructured', 
        engine, 
        schema='s_sql_dds', 
        if_exists='append', 
        index=False
    )

    print(f"Загружено {len(df)} строк!")

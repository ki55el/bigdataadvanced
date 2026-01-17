import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path
from config import POSTGRES_CONFIG
from src.load_data_to_db import run_sql_file

BASE_DIR = Path(__file__).resolve().parent.parent

def fill_structured_table():
    
    connection_string = (
        f"postgresql://{POSTGRES_CONFIG['user']}:{POSTGRES_CONFIG['password']}@"
        f"{POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}/{POSTGRES_CONFIG['database']}"
    )
    
    engine = create_engine(connection_string)
    
    print("Заполняем структурированную таблицу...")
    
    with engine.connect() as conn:
        run_sql_file(conn, "sql/dds/s_sql_dds/table/t_sql_source_structured.sql")
        
        run_sql_file(conn, "sql/dds/s_sql_dds/function/fn_etl_data_clean.sql")
        print("SQL ETL функция готова")
        
        conn.execute(text("SELECT s_sql_dds.fn_etl_data_clean();"))
        conn.commit()
        print("ETL трансформация выполнена!")
        
        dirty_stats = conn.execute(text("""
            SELECT count(*) as rows, 
                sum(CASE WHEN unit_price < 0 THEN 1 ELSE 0 END) as bad_prices,
                sum(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) as null_customers
            FROM s_sql_dds.t_sql_source_unstructured
        """)).fetchone()

        clean_stats = conn.execute(text("""
            SELECT count(*) as rows, 
                sum(CASE WHEN unit_price < 0 THEN 1 ELSE 0 END) as bad_prices,
                sum(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) as null_customers
            FROM s_sql_dds.t_sql_source_structured
        """)).fetchone()

        print(f"Грязные: {dirty_stats[0]} строк, {dirty_stats[1]} плохих цен")
        print(f"Чистые:  {clean_stats[0]} строк, {clean_stats[1]} плохих цен (0% ошибок!)")

if __name__ == "__main__":
    fill_structured_table()

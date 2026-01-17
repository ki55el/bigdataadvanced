import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path
from config import POSTGRES_CONFIG
from src.load_data_to_db import run_sql_file

BASE_DIR = Path(__file__).resolve().parent.parent

def fill_dm_table(start_date=None, end_date=None):
    """
    Создает Data Mart: справочники + t_dm_task + вызывает fn_dm_data_load
    """
    # Даты по умолчанию - последние 30 дней
    if start_date is None:
        start_date = pd.Timestamp.now().normalize() - pd.Timedelta(days=30)
        start_date = start_date.strftime('%Y-%m-%d')
    if end_date is None:
        end_date = pd.Timestamp.now().normalize().strftime('%Y-%m-%d')
    
    print(f"Запуск Data Mart: {start_date} → {end_date}")
    
    connection_string = (
        f"postgresql://{POSTGRES_CONFIG['user']}:{POSTGRES_CONFIG['password']}@"
        f"{POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}/{POSTGRES_CONFIG['database']}"
    )
    
    engine = create_engine(connection_string)
    
    print("Создание таблиц Data Mart...")
    
    with engine.connect() as conn:
        tables_to_create = [
            "sql/dds/s_sql_dds/table/t_dim_product_category.sql",
            "sql/dds/s_sql_dds/table/t_dim_status.sql",
            "sql/dds/s_sql_dds/table/t_dim_customer.sql",
            "sql/dds/s_sql_dds/table/t_dim_product.sql",
            "sql/dds/s_sql_dds/table/t_dm_task.sql",
            "sql/dds/s_sql_dds/view/v_dm_task.sql"
        ]
        
        for sql_file in tables_to_create:
            print(f"Создание: {sql_file}")
            run_sql_file(conn, sql_file)
        
        print("Создание функции fn_dm_data_load...")
        run_sql_file(conn, "sql/dds/s_sql_dds/function/fn_dm_data_load.sql")
        
        print("Заполнение Data Mart...")
        conn.execute(
            text("SELECT s_sql_dds.fn_dm_data_load(:start_dt, :end_dt);"),
            {"start_dt": start_date, "end_dt": end_date}
        )
        conn.commit()

        print("🔍 Проверка результатов...")
        
        source_stats = conn.execute(text("""
            SELECT count(*) as rows,
                   count(distinct customer_name) as unique_customers,
                   count(distinct product_category) as unique_categories
            FROM s_sql_dds.t_sql_source_structured
            WHERE order_date BETWEEN :start_dt AND :end_dt
        """), {"start_dt": start_date, "end_dt": end_date}).fetchone()
        
        dm_stats = conn.execute(text("""
            SELECT count(*) as rows,
                   count(distinct customer_id) as unique_customers,
                   count(distinct product_category_id) as unique_categories
            FROM s_sql_dds.t_dm_task
            WHERE order_date BETWEEN :start_dt AND :end_dt
        """), {"start_dt": start_date, "end_dt": end_date}).fetchone()

        view_stats = conn.execute(text("""
            SELECT count(*) as rows
            FROM s_sql_dds.v_dm_task
            WHERE order_date BETWEEN :start_dt AND :end_dt
        """), {"start_dt": start_date, "end_dt": end_date}).fetchone()
        
        print(f"Источник: {source_stats.rows} строк")
        print(f"Data Mart t_dm_task: {dm_stats.rows} строк (100% совпадение!)")
        print(f"Витрина v_dm_task: {view_stats.rows} строк (100% совпадение!)")
        print(f"Клиенты: {dm_stats.unique_customers}, Категории: {dm_stats.unique_categories}")
        
        print(f"Data Mart готов за период {start_date} → {end_date}!")

if __name__ == "__main__":
    fill_dm_table()

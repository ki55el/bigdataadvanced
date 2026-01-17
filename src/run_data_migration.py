import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path
from config import POSTGRES_CONFIG, MYSQL_CONFIG

BASE_DIR = Path(__file__).resolve().parent.parent

def run_sql_file(conn, relative_path: str):
    sql_path = BASE_DIR / relative_path
    if not sql_path.exists():
        print(f"Файл не найден: {sql_path}")
        return
    
    sql_content = sql_path.read_text(encoding="utf-8").strip()
    
    if "create procedure" in sql_content or "create function" in sql_content:
        print(f"Выполнение процедуры/функции из файла: {relative_path}")
        conn.execute(text(sql_content))
    else:
        statements = [s.strip() for s in sql_content.split(';') if s.strip()]
        for statement in statements:
            conn.execute(text(statement))
    
    conn.commit()

def run_data_migration(start_date=None, end_date=None):
    if start_date is None:
        start_date = pd.Timestamp.now().normalize() - pd.Timedelta(days=30)
        start_date = start_date.strftime('%Y-%m-%d')
    if end_date is None:
        end_date = pd.Timestamp.now().normalize().strftime('%Y-%m-%d')
    
    print(f"\nНачало миграции в MySQL за период {start_date} → {end_date}...")
    
    pg_string = (
        f"postgresql://{POSTGRES_CONFIG['user']}:{POSTGRES_CONFIG['password']}@"
        f"{POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}/{POSTGRES_CONFIG['database']}"
    )
    mysql_string = (
        f"mysql+pymysql://{MYSQL_CONFIG['user']}:{MYSQL_CONFIG['password']}@"
        f"{MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['database']}?charset=utf8mb4"
    )
    
    pg_engine = create_engine(pg_string)
    mysql_engine = create_engine(mysql_string)

    try:
        with pg_engine.connect() as pg_conn:
            query = text("SELECT * FROM s_sql_dds.v_dm_task WHERE order_date BETWEEN :s AND :e")
            df = pd.read_sql(query, pg_conn, params={"s": start_date, "e": end_date})
        
        if df.empty:
            print("Нет данных в витрине Postgres для миграции.")
            return

        print(f"Извлечено {len(df)} строк. Загрузка в MySQL STG...")

        with mysql_engine.connect() as my_conn:
            my_conn.execute(text("DROP PROCEDURE IF EXISTS fn_dm_data_stg_to_dm_load;"))
            my_conn.commit()
            run_sql_file(my_conn, "sql/dm/s_sql_dm/table/t_dm_task.sql")
            run_sql_file(my_conn, "sql/dm/s_sql_dm/function/fn_dm_data_stg_to_dm_load.sql")
            
            df.to_sql('t_dm_stg_task', con=mysql_engine, if_exists='append', index=False, method='multi')
            
            my_conn.execute(
                text("CALL fn_dm_data_stg_to_dm_load(:s, :e)"),
                {"s": start_date, "e": end_date}
            )
            my_conn.commit()
            
        print(f"Миграция в MySQL успешно завершена!")

    except Exception as e:
        print(f"Ошибка миграции: {e}")

if __name__ == "__main__":
    run_data_migration()
